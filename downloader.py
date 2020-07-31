import base64
import os
import re
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config.config import GMAIL


class Downloader:
    def __init__(self):
        if not os.path.exists('pics'):
            os.mkdir('pics')
        self.__PICS_PATH = os.path.abspath('pics')
        self.__LOG_PATH = os.path.abspath('log.txt')
        self.__SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.ppm', '.pnm', '.pgm', '.xpm', '.tif', '.tiff', '.eim']
        self.downloading = False # use later when implementing restart button in app

    def run(self):
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
                        try:
                            sender = self.__extractSenderEmail(msg['payload']['headers'])
                        except (TypeError, AttributeError) as exc:
                            self.__log(str(exc))
                        if ext not in self.__SUPPORTED_FORMATS:
                            self.__sendErrorEmail(sender)
                            break

                        path = os.path.join(self.__PICS_PATH, filename)
                        with open(path, 'wb') as f:
                            f.write(file_data)
                        
                        self.__log(f'Downloaded {filename} from {sender}.')

            # time.sleep(5)

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
            raise AttributeError('Error extracting email--No regular expression match.')

        return result

    def __sendErrorEmail(self, to):
        try:
            message_text = 'The picture file you sent was not an approved file type.  Please try again and make sure that the picture is one of the following file types: ('
            message_text += ', '.join(self.__SUPPORTED_FORMATS)
            message_text += ')'
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = 'TVFrame: Incompatible filetype'
            message.attach(MIMEText(message_text, 'plain'))
            raw_string = base64.urlsafe_b64encode(message.as_bytes()).decode()
            body = {'raw': raw_string}
            GMAIL.users().messages().send(userId='me', body=body).execute()
            print(f'Sent incompatible filetype email to {to}.')
            self.__log(f'Sent incompatible filetype email to {to}.')
        except Exception as exc:
            print(f'Error sending incompatible filetype email to {to}.')
            self.__log(f'Error sending incompatible filetype email to {to}.  ' + str(exc))

    def __log(self, message):
        now = datetime.now()
        dt_string = now.strftime('%m/%d/%Y %H:%M:%S')
        with open(self.__LOG_PATH, 'a') as f:
            message = dt_string + ': ' + message + '\n'
            f.writelines(message)