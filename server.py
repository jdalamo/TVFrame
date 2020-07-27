import json
import os
import socket
from threading import Thread
from flask import Flask, request, send_file
from downloader import Downloader
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

PICS_PATH = os.path.abspath('pics')

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
            with open('settings.json', 'r') as f:
                settings = json.load(f)
        except json.decoder.JSONDecodeError:
            return 'Something went wrong decoding JSON, try again.', 409
        settings.pop('modes')
        settings.pop('display_photo')
        response = {
            'response': settings
        }
        
        return response, 200

    def put(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
        except json.decoder.JSONDecodeError:
            return 'Something went wrong decoding JSON, try again.', 409
        data = request.json['data']
        settings['device_name'] = data['newName']
        settings['email'] = data['newEmail']
        try:
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
        except json.decoder.JSONDecodeError:
            return 'Something went wrong decoding JSON, try again.', 409

        return 'Updated settings.', 200


class Modes(Resource):
    def get(self):
        try:
            with open('settings.json', 'r') as f:
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
            with open('settings.json', 'r') as f:
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
                with open('settings.json', 'w') as f:
                    json.dump(settings, f)
            except json.decoder.JSONDecodeError:
                return 'Something went wrong decoding JSON, try again.', 409
            return f'Changed mode to {newName}.', 200
        else:
            return 'Invalid mode name.', 400


class DisplayPhoto(Resource):
    def put(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
        except json.decoder.JSONDecodeError:
            return 'Something went wrong deconding JSON, try again.', 409
        newPhoto = request.json['data']
        settings['display_photo'] = newPhoto
        try:
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
        except json.decoder.JSONDecodeError:
            return 'Something went wrong encoding JSON, try again.', 409
        
        return 'Successfully set display picture.', 200

        
class Log(Resource):
    def get(self):
        if os.path.exists('log.txt'):
            f = open('log.txt', 'r')
            response = {
                'response': f.read()
            }
            return response, 200
        else:
            return 'No log created.', 400


api.add_resource(Photos, '/photos/', '/photos/<string:filename>')
api.add_resource(Settings, '/settings/')
api.add_resource(Modes, '/modes/')
api.add_resource(DisplayPhoto, '/display_photo/')
api.add_resource(Log, '/log/')

# def download_manager():
#     d = Downloader()
#     d.start()

if __name__ == '__main__':
    # download_thread = Thread(target=download_manager)
    # download_thread.start()
    hostname = socket.gethostname()
    ipaddr = socket.gethostbyname(hostname)
    app.run('127.0.0.1', debug=True)
