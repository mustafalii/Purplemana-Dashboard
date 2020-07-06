from googleapiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build


# This class is used by the dashboard to upload image to the "Scanned" folder
class ImageUploader:
    def __init__(self, card_img, date, source, cardName, grade, slot):
        self.img = card_img
        self.imageFileName = str(date) + "_" + source + "_" + cardName + "_" + grade + "_" + slot
        self.scope = ["https://spreadsheets.google.com/feeds",
                      "https://www.googleapis.com/auth/spreadsheets",
                      "https://www.googleapis.com/auth/drive.file",
                      "https://www.googleapis.com/auth/drive",
                      "https://www.googleapis.com/auth/drive.appdata"
                      ]

        self.cred = ServiceAccountCredentials.from_json_keyfile_name("creds.json", self.scope)
        self.service = build('drive', 'v3', credentials=self.cred)
        self.resultsDict = self.service.files().list(fields="nextPageToken, files(id, name)").execute()
        self.myFiles = self.resultsDict.get('files', [])
        print(self.myFiles)

        # Get ID of Scanned folder to serve as parentFolderId
        for file in self.myFiles:
            if file['name'] == 'Scanned':
                scannedFolderId = file['id']
                break

        # body of image to be uploaded
        fileBody = {
            'name': self.imageFileName,
            'parents': [scannedFolderId]
        }

        media = MediaFileUpload(self.img, mimetype='image/png', resumable=True)
        self.service.files().create(body=fileBody, media_body=media).execute()
        print("Image uploaded to scanned folder.")





