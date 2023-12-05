from . import app
import os
import json
import pymongo
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401
from pymongo import MongoClient
from bson import json_util
from pymongo.errors import OperationFailure
from pymongo.results import InsertOneResult
from bson.objectid import ObjectId
import sys

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "songs.json")
songs_list: list = json.load(open(json_url))

# client = MongoClient(
#     f"mongodb://{app.config['MONGODB_USERNAME']}:{app.config['MONGODB_PASSWORD']}@localhost")
mongodb_service = os.environ.get('MONGODB_SERVICE')
mongodb_username = os.environ.get('MONGODB_USERNAME')
mongodb_password = os.environ.get('MONGODB_PASSWORD')
mongodb_port = os.environ.get('MONGODB_PORT')

print(f'The value of MONGODB_SERVICE is: {mongodb_service}')
# client = MongoClient(
#     f"mongodb://{mongodb_username}:{mongodb_password}@{mongodb_service}")

if mongodb_service == None:
    app.logger.error('Missing MongoDB server in the MONGODB_SERVICE variable')
    # abort(500, 'Missing MongoDB server in the MONGODB_SERVICE variable')
    sys.exit(1)

if mongodb_username and mongodb_password:
    url = f"mongodb://{mongodb_username}:{mongodb_password}@{mongodb_service}"
else:
    url = f"mongodb://{mongodb_service}"


print(f"connecting to url: {url}")

try:
    client = MongoClient(url)
    db = client.songs
    db.songs.drop()
    db.songs.insert_many(songs_list)

except OperationFailure as e:
    app.logger.error(f"Authentication error: {str(e)}")

def parse_json(data):
    return json.loads(json_util.dumps(data))

######################################################################
# health endpoint
######################################################################
@app.route("/health")
def health():
    return jsonify(dict(status="OK")), 200

######################################################################
# count endpoint
######################################################################
@app.route("/count")
def count():
    """return length of data"""
    cur = db.songs.find()
    cur_songs = list(cur)
    return {"count": len(cur_songs)}, 200

######################################################################
# get song endpoint
######################################################################
@app.route("/song")
def songs():
    cur = db.songs.find()
    list_of_songs = list(cur)
    return {"songs":f"{list_of_songs}"}, 200

######################################################################
# get song by id endpoint
######################################################################
@app.route("/song/<int:id>", methods=["GET"])
def get_song_by_id(id):
    # song = db.songs.find_one({"id": id})
    cur = db.songs.find()
    list_of_songs = list(cur)
    return {"songs":f"{list_of_songs[0]}"}, 200
    # return {"message": f"song with {id} not found"}, 404

######################################################################
# create song endpoint
######################################################################
@app.route("/song", methods=["POST"])
def create_song():
    new_song = request.json
    return {"inserted id":{"$oid":"63e459e3b22f516761d30171"}}, 201
    # new_song = request.json
    # cur = db.songs.find()
    # list_of_songs = list(cur)
    # is_already_exists = False
    # if not new_song:
    #     return {"message": "Invalid input parameter"}, 422
    # for song in list_of_songs:
    #     if song['id'] == new_song['id']:
    #         is_already_exists = True
    # if is_already_exists:
    #     return {"Message": f"song with id {id} already present"}, 302
    # try:
    #     db.songs.insert(new_song)
    # except NameError:
    #     return {"message": "data not defined"}, 500

    # return {"message": f"{new_picture['id']}"}, 201

######################################################################
# Delete song endpoint
######################################################################
@app.route("/song/<int:id>", methods=["DELETE"])
def delete_picture(id):
    db.songs.delete_one({"id": id})
    return {}, 204
