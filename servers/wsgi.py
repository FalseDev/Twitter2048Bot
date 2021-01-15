import os
from flask import Flask, jsonify, request

from twitter2048.synchronous import new_game, continue_game, get_last_game_tweet

app = Flask(__name__)


@app.before_request
def check():
    if request.headers.get('Authorization') != os.environ.get('AUTHORIZATION'):
        return jsonify({"Error": "Authorization invalid"}), 401


@app.route('/start', methods=['GET'])
def start():
    new_game()
    return jsonify({'info': 'Success'})


@app.route('/continue', methods=['GET'])
def continue_game_route():
    continue_game(get_last_game_tweet())
    return jsonify({"info": "success"})
