from peony import PeonyClient
from pydantic import BaseModel

from game import Game

from . import creds, game_new, game_step

client = PeonyClient(**creds)


class Tweet(BaseModel):
    favorite_count: int
    retweet_count: int
    text: str


async def get_last_game_tweet():
    data = await client.api.statuses.user_timeline.get(screen_name=client.me, trim_user=True, count=1)
    return Tweet(**data[0])


async def continue_game(tweet: Tweet):
    game, bytes_obj, new_controls = game_step(tweet)
    image = await client.upload_media(bytes_obj)
    await client.api.statuses.update.post(status=f"{new_controls};{game.dumps()};", media_ids=[image.media_id])


async def new_game():
    game, bytes_obj = game_new()
    image = await client.upload_media(bytes_obj)
    await client.api.statuses.update.post(status=f"UD;{game.dumps()};", media_ids=[image.media_id])
