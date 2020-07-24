import os
import sys
from datetime import datetime
import time
import base64
import pickle
import imaplib
import smtplib
import email
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders
from config.config import GMAIL

class Downloader:
    def __init__(self):
        self.__WD = os.getcwd()
        if not os.path.exists('pics'):
            os.mkdir('pics')
        self.__PICS_PATH = os.path.join(self.__WD, 'pics')
        self.__LOG_PATH = os.path.join(self.__WD, 'log.txt')
        self.__SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.ppm', '.pnm', '.pgm', '.xpm', '.tif', '.tiff', '.eim']
        self.__START = time.time()
        self.downloading = False # use later when implementing restart button in app

    def refresh_photos(self):
        results = GMAIL.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD']).execute()
        messages = results.get('messages', [])
        for message in messages:
            msg_id = message['id']
            GMAIL.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()
            msg = GMAIL.users().messages().get(userId='me', id=msg_id).execute()

            for part in msg['payload']['parts']:
                if part['filename']:
                    if 'data' in part['body']:
                        data = part['body']
                    else:
                        att_id = part['body']['attachmentId']
                        att = GMAIL.users().messages().attachments().get(userId='me', messageId=msg_id,id=att_id).execute()
                        data = att['data']
                    file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                    filename = self.getFileName(part['filename'])
                    path = os.path.join(self.__PICS_PATH, filename)

                    with open(path, 'wb') as f:
                        f.write(file_data)

    def getFileName(self, currentName):
        fileName, fileExt = os.path.splitext(currentName)
        newName = fileName + fileExt.lower()
        contents = set([p for p in os.listdir(self.__PICS_PATH) if os.path.isfile(os.path.join(self.__PICS_PATH, p)) and p != '.DS_Store'])
        if newName not in contents:
            return newName

        counter = 1
        while newName in contents:
            name, ext = os.path.splitext(newName)
            newName = name + '_' + str(counter) + ext.lower()
            counter += 1
        
        return newName

    def sendErrorEmail(self, to):
        try:
            _from = ADDRESS
            message = f'From: {_from}\nTo: {to}\nSubject: Error\n\nThe picture you sent was not an approved file type.  Please try again and make sure that the picture is one of the following file types:\n'
            message += ', '.join(self.__SUPPORTED_FORMATS)
            smtp = smtplib.SMTP('smtp.gmail.com', 587)
            smtp.ehlo()
            smtp.starttls()
            smtp.login(ADDRESS, PASSWORD)
            smtp.sendmail(_from, to, message)
            smtp.close()
            print(f'Sent incompatible filetype email to {to}.')
            self.log(f'Sent incompatible filetype email to {to}.')
        except Exception as exc:
            print(f'Error sending incompatible filetype email to {to}.')
            self.log(f'Error sending incompatible filetype email to {to}.  ' + str(exc))

    def sendReport(self, exc=False):
        try:
            _from = ADDRESS
            to = 'alamojad@gmail.com'
            subject = 'Report'
            if exc != False:
                subject = 'Possible Fatal Error Report'
            msg = MIMEMultipart() 
            msg['From'] = _from 
            msg['To'] = to
            msg['Subject'] = subject
            body = self.generateReport(exc)
            msg.attach(MIMEText(body, 'plain')) 
            filename = 'log.txt'
            attachment = open(self.__LOG_PATH, 'rb') 
            p = MIMEBase('application', 'octet-stream') 
            p.set_payload((attachment).read()) 
            encoders.encode_base64(p) 
            p.add_header('Content-Disposition', f'attachment; filename= {filename}') 
            msg.attach(p) 
            s = smtplib.SMTP('smtp.gmail.com', 587) 
            s.starttls() 
            s.login(ADDRESS, PASSWORD) 
            text = msg.as_string() 
            s.sendmail(_from, to, text) 
            s.quit() 
            print(f'Sent report to {to}.')
            self.log(f'Sent report to {to}.')
        except Exception as exc:
            print(f'Error sending report email to {to}.')
            self.log(f'Error sending report email to {to}.  ' + str(exc))

    def generateReport(self, exc=False):
        report = F'Address: {ADDRESS}\n'
        now = datetime.now()
        dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
        report += f'Date: {dt_string}\n'
        stop = time.time()
        report += 'Uptime {}\n'.format(stop - self.__START)
        if exc != False:
            report += f'\nError Message: {exc}'

        return report

    def log(self, message):
        now = datetime.now()
        dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
        with open(self.__LOG_PATH, 'a') as f:
            message = dt_string + ': ' + message + '\n'
            f.writelines(message)

d = Downloader()
d.refresh_photos()