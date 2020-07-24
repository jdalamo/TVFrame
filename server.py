import json
import os
import socket
from flask import Flask, request, send_file
from downloader import Downloader
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

class Pic(Resource):
    def get(self, filename=None):
        if filename == None:
            return "No picture specified.", 400
        path = os.path.join('pics', filename)
        _, ext = os.path.splitext
        if ext[0] == '.':
            ext = ext.lstrip('.')
        response = app.make_response(send_file(path, mimetype=f'image/{ext}'))
        # set no cache so that SDWebImage doesn't cache preview pictures
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'

        return response

class Photos(Resource):
    def get(self):
        if os.path.exists('pics/'):
            pics = [p for p in os.listdir('pics') if os.path.isfile(os.path.join('pics', p)) and p != '.DS_Store']
            response = {
                "response": pics
            }
            return response, 200
        else:
            return "No pictures.", 400
    
    def put(self):
        pics = [p for p in os.listdir('pics') if os.path.isfile(os.path.join('pics', p)) and p != '.DS_Store']
        jsonData = request.json['data']
        oldName = jsonData['old_name']
        newName = jsonData['new_name']
        if oldName in pics:
            os.rename(os.path.join('pics', oldName), os.path.join('pics', newName))
            return "Renamed photo.", 200
        else:
            return "Specified filename not in directory.", 400

    def delete(self, filename=None):
        if filename == None:
            return "No file name specified.", 400
        pics = [p for p in os.listdir('pics') if os.path.isfile(os.path.join('pics', p)) and p != '.DS_Store']
        if filename not in pics:
            return "Invalid file name", 400
        os.remove(os.path.join('pics', filename))

        return "Picture deleted.", 200

class DisplayPhoto(Resource):
    def put(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
        except json.decoder.JSONDecodeError:
            return "Something went wrong deconding JSON, try again.", 409
        newPhoto = request.json['data']
        settings['display_photo'] = newPhoto
        try:
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
        except json.decoder.JSONDecodeError:
            return "Something went wrong encoding JSON, try again.", 409
        
        return "Successfully set display picture.", 200

class DownloadPhotos(Resource):
    def get(self):
        #can add a timer so this isn't called too often
        d = Downloader()
        d.refresh_photos()

        return "Pictures have been refreshed.", 200

class Modes(Resource):
    def get(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
        except json.decoder.JSONDecodeError:
            return "Something went wrong decoding JSON, try again.", 409
        modes = settings['modes']
        response = {
            'response': modes
        }

        return response, 200

class DeviceName(Resource):
    def get(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
        except json.decoder.JSONDecodeError:
            return "Something went wrong decoding JSON, try again.", 409
        response = {
            'response': {
                'device_name': settings['device_name']
            }
        }

        return response, 200

    def put(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
        except json.decoder.JSONDecodeError:
            return "Something went wrong decoding JSON, try again.", 409
        newName = request.json['data']
        settings['device_name'] = newName
        try:
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
        except json.decoder.JSONDecodeError:
            return "Something went wrong decoding JSON, try again.", 409
        
        return "Device name updated.", 200

class ChangeMode(Resource):
    def put(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
        except json.decoder.JSONDecodeError:
            return "Something went wrong decoding JSON, try again.", 409
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
                return "Something went wrong decoding JSON, try again.", 409
            return f"Changed mode to {newName}.", 200
        else:
            return "Invalid mode name.", 400

class Log(Resource):
    def get(self):
        if os.path.exists('log.txt'):
            f = open('log.txt', 'r')
            response = {
                "response": f.read()
            }
            return response, 200
        else:
            return "No log created.", 400

class DeletePic(Resource):
    def put(self):
        picToDelete = request.form['data']
        if picToDelete in [p for p in os.listdir('pics') if os.path.isfile(os.path.join('pics', p)) and p != '.DS_Store']:
            os.remove(os.path.join('pics', picToDelete))
            return "Deleted picture.", 200
        else:
            return f"Couldn't find selected picture ({picToDelete}) to delete.", 400

class Settings(Resource):
    def get(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
        except json.decoder.JSONDecodeError:
            return "Something went wrong decoding JSON, try again.", 409
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
            return "Something went wrong decoding JSON, try again.", 409
        data = request.json['data']
        settings['device_name'] = data['newName']
        settings['email'] = data['newEmail']
        try:
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
        except json.decoder.JSONDecodeError:
            return "Something went wrong decoding JSON, try again.", 409

        return "Updated settings.", 200


api.add_resource(Photos, '/photos/', '/photos/<string:filename>')
api.add_resource(DownloadPhotos, '/download_photos/')
api.add_resource(DisplayPhoto, '/display_photo/')
api.add_resource(Modes, '/modes/')
api.add_resource(ChangeMode, '/changemode/')
api.add_resource(Log, '/log/')
api.add_resource(DeviceName, '/name/')
api.add_resource(DeletePic, '/delete/')
api.add_resource(Settings, '/settings/')
api.add_resource(Pic, '/pic/<string:filename>')

if __name__ == '__main__':
    hostname = socket.gethostname()
    ipaddr = socket.gethostbyname(hostname)
    app.run(ipaddr, debug=True)
