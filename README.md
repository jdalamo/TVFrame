# Smart picture frame software for a Raspberry Pi + Companion iOS app

App available [here](https://github.com/jdalamo/TVFrame_App).

## About
---
TVFrame is a project that emulates the functionality of a "smart" picture frame on your TV.  It's intended to be run on a Raspberry Pi connected to your TV and pictures can be emailed to it at an email specified by the user.  The companion iOS app extends this functionality by allowing the user to view the pictures saved on the device, switch modes between slideshow (where all the pictures are played) and single-photo mode (where the user can use the app to select photos to view), delete pictures from the device, and view the device's activity log.

## Stack
---
- Python
- Flask

## Depenencies
---
- Gmail API

## Get it running
---
This tutorial assumes you already have Raspbian OS running on your Raspberry Pi
1. Clone the directory onto your Raspberry Pi
2. Go to https://developers.google.com/gmail/api/quickstart/python
3. Click "Enable the Drive API" (Make sure the google account you are signed in as is the email you want pictures to be emailed to)
4. Follow the prompts and then download the user credentials
5. Copy the json file to TVFrame/config and rename it "credentials.json"
6. Run the following commands in the cloned directory:

Note: May need to use pip and python instead of pip3 and python3 if you don't have multiple versions of python installed
```
> pip3 install -r requirements.txt
> python3 server.py
```
In a separate terminal window:
```
> python3 setup.py
```
7. In the browser window that opened, select the account you want to use
8. Click "Advanced"
9. Click "Go to {App Name}
10. Click "Allow" twice
11. The program should now be running on your screen
12. To add pictures to your device email them to the Gmail account you set it up with
13. Download the [Companion iOS app](https://github.com/jdalamo/TVFrame_App) and build it to your phone to control the display

## Planned Future Functionality
---
- Allow users to rename pictures from the app
- Allow user to download pictures from the app to their iOS device
- Allow users to create playlists and select a playlist for viewing