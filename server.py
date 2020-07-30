import json
import os
import socket

from flask import Flask, request, send_file
from flask_restful import Api, Resource

from config.config import GMAIL

app = Flask(__name__)
api = Api(app)

PICS_PATH = os.path.abspath('pics')
SETTINGS_PATH = os.path.abspath('settings.json')
LOG_PATH = os.path.abspath('log.txt')

class Photos(Resource):
    def get(self, filename=None):
        if filename:
            path = os.path.join(PICS_PATH, filename)
            _, ext = os.path.splitext(path)
            if ext[0] == '.':
                ext = ext.lstrip('.')
            response = app.make_response(send_file(path, mimetype=f'image/{ext}'))
            # set no cache so that SDWebImage doesn't cache preview pictures
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'

            return response
        else:
            if os.path.exists(PICS_PATH):
                pics = [p for p in os.listdir(PICS_PATH) if os.path.isfile(os.path.join(PICS_PATH, p)) and p != '.DS_Store']
                response = {
                    'response': pics
                }
                return response, 200
            else:
                return 'No pictures.', 400
    
    #TODO: Implement rename functionality in app
    def put(self):
        pics = [p for p in os.listdir(PICS_PATH) if os.path.isfile(os.path.join(PICS_PATH, p)) and p != '.DS_Store']
        jsonData = request.json['data']
        oldName = jsonData['old_name']
        newName = jsonData['new_name']
        if oldName in pics:
            os.rename(os.path.join(PICS_PATH, oldName), os.path.join(PICS_PATH, newName))
            return 'Renamed photo.', 200
        else:
            return 'Specified filename not in directory.', 400

    def delete(self, filename=None):
        if filename == None:
            return 'No file name specified.', 400
        pics = [p for p in os.listdir(PICS_PATH) if os.path.isfile(os.path.join(PICS_PATH, p)) and p != '.DS_Store']
        if filename not in pics:
            return 'Invalid file name', 400
        os.remove(os.path.join(PICS_PATH, filename))

        return 'Picture deleted.', 200


class Settings(Resource):
    def get(self):
        try:
            with open(SETTINGS_PATH, 'r') as f:
                _settings = json.load(f)
        except json.decoder.JSONDecodeError:
            return 'Something went wrong decoding JSON, try again.', 409

        settings = {}
        settings['device_name'] = _settings['device_name']
        settings['mode'] = _settings['mode']

        response = {
            'response': settings
        }
        
        return response, 200

    def put(self):
        try:
            with open(SETTINGS_PATH, 'r') as f:
                settings = json.load(f)
        except json.decoder.JSONDecodeError:
            return 'Something went wrong decoding JSON, try again.', 409
        data = request.json['data']
        #TODO: Refactor this
        settings['device_name'] = data['newName']
        try:
            with open(SETTINGS_PATH, 'w') as f:
                json.dump(settings, f)
        except json.decoder.JSONDecodeError:
            return 'Something went wrong decoding JSON, try again.', 409

        return 'Updated settings.', 200


class Modes(Resource):
    def get(self):
        try:
            with open(SETTINGS_PATH, 'r') as f:
                settings = json.load(f)
        except json.decoder.JSONDecodeError:
            return 'Something went wrong decoding JSON, try again.', 409
        modes = settings['modes']
        response = {
            'response': modes
        }

        return response, 200
    
    def put(self):
        try:
            with open(SETTINGS_PATH, 'r') as f:
                settings = json.load(f)
        except json.decoder.JSONDecodeError:
            return 'Something went wrong decoding JSON, try again.', 409
        modes = settings['modes']
        modeNames = set([m['name'] for m in modes])
        newName = request.json['data']
        if newName in modeNames:
            settings['mode'] = newName
            for entry in settings['modes']:
                if entry['name'] == newName:
                    entry['active'] = True
                else:
                    entry['active'] = False
            try:
                with open(SETTINGS_PATH, 'w') as f:
                    json.dump(settings, f)
            except json.decoder.JSONDecodeError:
                return 'Something went wrong decoding JSON, try again.', 409
            return f'Changed mode to {newName}.', 200
        else:
            return 'Invalid mode name.', 400


class Email(Resource):
    def get(self):
        try:
            GMAIL_response = GMAIL.users().getProfile(userId='me').execute()
            address = GMAIL_response['emailAddress']
        except:
            return 'Something went wrong retrieving email address', 409
        
        response = {
            'response': address
        }

        return response, 200


class DisplayPhoto(Resource):
    def put(self):
        try:
            with open(SETTINGS_PATH, 'r') as f:
                settings = json.load(f)
        except json.decoder.JSONDecodeError:
            return 'Something went wrong deconding JSON, try again.', 409
        newPhoto = request.json['data']
        settings['display_photo'] = newPhoto
        try:
            with open(SETTINGS_PATH, 'w') as f:
                json.dump(settings, f)
        except json.decoder.JSONDecodeError:
            return 'Something went wrong decoding JSON, try again.', 409
        
        return 'Successfully set display picture.', 200


class ConnectionStatus(Resource):
    def put(self):
        try:
            with open(SETTINGS_PATH, 'r') as f:
                settings = json.load(f)
        except json.decoder.JSONDecodeError:
            return 'Something went wrong deconding JSON, try again.', 409

        status = request.json['data']
        settings['app_is_connected'] = status
        try:
            with open(SETTINGS_PATH, 'w') as f:
                json.dump(settings, f)
        except json.decoder.JSONDecodeError:
            return 'Something went wrong decoding JSON, try again.', 409

        return 'Successfully updated connection status.', 200
        
        
class Log(Resource):
    def get(self):
        if os.path.exists(LOG_PATH):
            f = open(LOG_PATH, 'r')
            response = {
                'response': f.read()
            }
            return response, 200
        else:
            return 'No log created.', 400


api.add_resource(Photos, '/photos/', '/photos/<string:filename>')
api.add_resource(Settings, '/settings/')
api.add_resource(Modes, '/modes/')
api.add_resource(Email, '/email/')
api.add_resource(DisplayPhoto, '/display_photo/')
api.add_resource(ConnectionStatus, '/connection_status/')
api.add_resource(Log, '/log/')


def getIP(remote_server="google.com"):
    """
    Return the/a network-facing IP number for this system.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s: 
        s.connect((remote_server, 80))
        return s.getsockname()[0]
    
    return ip

if __name__ == '__main__':
    ip = getIP()
    print(ip)
    app.run(ip, debug=True)
