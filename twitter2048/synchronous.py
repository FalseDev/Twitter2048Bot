from twitter.api import Api

from game import Game

from . import creds, game_new, game_step

client = Api(
    **{k if k != "access_token" else "access_token_key": v for k, v in creds.items()})


def get_last_game_tweet():
    return client.GetUserTimeline(
        screen_name="2048GameBot", trim_user=True, count=1)[0]


def continue_game(tweet):
    game, bytes_obj, new_controls = game_step(tweet)
    bytes_obj.mode = "rb"
    client.PostUpdate(
        status=f"{new_controls};{game.dumps()};", media=bytes_obj)


def new_game():
    game, bytes_obj = game_new()
    bytes_obj.mode = "rb"
    client.PostUpdate(status=f"UD;{game.dumps()};", media=bytes_obj)
