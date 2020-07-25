import base64
import email
import imaplib
import os
import pickle
import re
import smtplib
import sys
import time
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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

    def start(self):
        while True:
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
                        filename = self.__getFileName(part['filename'])
                        _, ext = os.path.splitext(filename)
                        if ext not in self.__SUPPORTED_FORMATS:
                            try:
                                sender = self.__extractSenderEmail(msg['payload']['headers'])
                                self.__sendErrorEmail(sender)
                            except (TypeError, AttributeError) as exc:
                                self.__log(str(exc))
                            break

                        path = os.path.join(self.__PICS_PATH, filename)
                        with open(path, 'wb') as f:
                            f.write(file_data)

            # time.sleep(3)

    def __getFileName(self, currentName):
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

    def __extractSenderEmail(self, headers):
        value = None
        for header in headers:
            try:
                if header['name'] == 'From':
                    value = header['value']
            except TypeError:
                continue

        try:
            match = re.search(R'(?<=\<)(.*?)(?=\>)', value)
            result = match.group()
        except TypeError:
            raise TypeError("Error extracting email--'From' header not in headers")
        except AttributeError:
            raise AttributeError("Error extracting email--No regular expression match.")
        
        return result



# Need to rewrite these functions to use Gmail API instead of imaplib library

    def __sendErrorEmail(self, to):
        try:
            _from = 'tvframe.test@gmail.com'
            message_text = f'From: {_from}\nTo: {to}\nSubject: Error\n\nThe picture you sent was not an approved file type.  Please try again and make sure that the picture is one of the following file types:\n'
            message_text += ', '.join(self.__SUPPORTED_FORMATS)
            message = MIMEText(message_text)
            message['to'] = to
            message['from'] = _from
            message['subject'] = 'Incompatible filetype sent to TVFrame'
            body = {'raw': base64.urlsafe_b64encode(message.as_string())}
            GMAIL.users().messages().send(userId='me', body=body).execute()
            print(f'Sent incompatible filetype email to {to}.')
            self.__log(f'Sent incompatible filetype email to {to}.')
        except Exception as exc:
            print(f'Error sending incompatible filetype email to {to}.')
            self.__log(f'Error sending incompatible filetype email to {to}.  ' + str(exc))

    def __log(self, message):
        now = datetime.now()
        dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
        with open(self.__LOG_PATH, 'a') as f:
            message = dt_string + ': ' + message + '\n'
            f.writelines(message)


d = Downloader()
d.start()