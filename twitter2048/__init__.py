import json
import os

from game import Game

try:
    with open('creds.json') as f:
        creds = json.load(f)
except FileNotFoundError:
    creds = {key.lower(): os.environ[key] for key in (
        "CONSUMER_KEY", "CONSUMER_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET")}


def game_step(tweet):
    controls, loadable_state, _ = tweet.text.split(";")

    game = Game.loads(loadable_state)
    more_retweets = tweet.favorite_count < tweet.retweet_count
    if controls == "UD":
        move = "up" if more_retweets else "down"
    else:
        move = "left" if more_retweets else "right"

    getattr(game, move)()

    game.spawn_box()

    new_controls = "UD" if controls == "LR" else "LR"
    bytes_obj = game.to_twitter_image_bytes(new_controls)
    return game, bytes_obj, new_controls


def game_new():
    game = Game.new().spawn_box()
    bytes_obj = game.to_twitter_image_bytes("UD")
    return game, bytes_obj
