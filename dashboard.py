import streamlit as st
import autocrop as ac
import numpy as np
import cv2
import gspread
from datetime import date
import driveUploader


# Fetch inventory from MainInventory in drive
# Cached so it doesn't fetch everytime the script is run.
@st.cache(allow_output_mutation=True)
def getInventory():
    gc = gspread.service_account(filename='creds.json')
    inv = gc.open("MainInventory").sheet1
    return inv


# Convert bytesIO to numpy array
# Autocropper takes care of highlighting detected cards in image (imgCropper.detected)
# and extracting cropped cards (imgCropper.cropped)
@st.cache
def detectCards(img_stream):
    file_bytes = np.asarray(bytearray(img_stream.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    imgCropper = ac.Autocropper(img)
    return imgCropper.detected, imgCropper.cropped


# Combine the front and back of each cropped card
@st.cache
def combineCrops(front, back):
    stacked = []
    for i in range(len(front)):
        cropFront = front[i]
        cropBack = back[i]
        max_height = max(cropFront.shape[0], cropBack.shape[0])
        max_width = max(cropFront.shape[1], cropBack.shape[1])
        final_image_front = np.zeros((max_height, max_width, 3), dtype=np.uint8)
        final_image_back = np.zeros((max_height, max_width, 3), dtype=np.uint8)
        final_image_front[:cropFront.shape[0], :cropFront.shape[1]] = cropFront
        final_image_back[:cropBack.shape[0], :cropBack.shape[1]] = cropBack
        stack = np.hstack((final_image_front, final_image_back))
        stacked.append(stack)
    return stacked


# Present the combined card to user and prompt for grading and updating inventory
def gradeCards(front, back):
    combinedCards = combineCrops(front, back)
    k = 0
    for card in combinedCards:
        st.image(card)
        cardName = st.text_input("Card Name:", key=k)
        source = st.text_input("Source:", key=k)
        slot = st.text_input("Slot:", key=k)
        grade = st.selectbox("Assign grade", ["None", "NM", "LP", "MP", "HP", "D"], key=k)
        confirmCheck = st.checkbox("Confirm entry and upload image", key=k)
        if confirmCheck:
            row = ["In Hand", source, slot, cardName, grade, str(date.today())]
            updateEntry(row, card)
        k += 1


# Update inventory and upload scanned image when user confirms.
@st.cache
def updateEntry(row, card):
    inv = getInventory()
    inv.append_row(row)
    card = cv2.cvtColor(card, cv2.COLOR_BGR2RGB)
    cv2.imwrite("toUpload/temp.png", card)
    driveUploader.ImageUploader("toUpload/temp.png", row[5], row[1], row[3], row[4], row[2])


# Header
st.title("Purplemana Dashoard 🔮💧☀️💀🎄🔥")
st.write("## 1. Upload front of scanned image:")


# Upload front-scan
# Detect cards in uploaded image
# Show detected cards
frontImgStream = st.file_uploader("Upload file", key="front_image_uploader")
if frontImgStream:
    st.write("Detected cards are highlighted:")
    frontDetected, frontCropped = detectCards(frontImgStream)
    for detected in frontDetected:
        st.image(detected, width=500)


# Upload back-scan
# Detect cards in uploaded image
# Show detected cards
st.write("## 2. Upload back of scanned image:")
backImgStream = st.file_uploader("Upload file", key="back_image_uploader")
if backImgStream:
    st.write("Detected cards are highlighted:")
    backDetected, backCropped = detectCards(backImgStream)
    for detected in backDetected:
        st.image(detected, width=500)


# Start grading process
# combineCrops(img1, img2) combines the front and back of individual card crops
# each card is shown and user is asked to enter some data
st.write("## 3. Update inventory:")
startGrading = st.checkbox("Start grading")
recordsToAdd = []
if startGrading:
    gradeCards(frontCropped, backCropped)


# Show the main inventory
st.write("## 4. Check Inventory:")
showInventory = st.checkbox("Show Inventory")
if showInventory:
    st.dataframe(getInventory().get_all_records())

