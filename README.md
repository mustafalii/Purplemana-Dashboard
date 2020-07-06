# Purplemana-Dashboard: A streamlit application, with a detection-based autocropping program in the backend, to allow easy grading for staff, and enable the automation of updating inventory.

## What it looks like
<img src="/imgs/screencapture.png" width=600>

## In action

### Step 1: Uploading the front-side of scanned image
<img src="/imgs/Step1.JPG" width=500>


### Step 2: Uploading the back-side of scanned image
<img src="/imgs/Step2.JPG" width=500>


### Step 3: Grading and updating inventory
<img src="/imgs/Step3_1.JPG" width=350><img src="/imgs/step3_2.JPG" width=350>  


### Step 4: Check inventory
<img src="/imgs/Step4.JPG" width=500>

## Usage
Assuming you have the python dependencies installed, you may start the application with the following command:
```
streamlit run dashoard.py
```

## Note:
You will need a google service account, and your own creds.json file that is used in driveUploader.py. You must also share the relevant files on your drive with the service account. Once you have the creds.json file, put in the same directory as the python files, and make the associated changes in driveUploader.py and dashboard.py
