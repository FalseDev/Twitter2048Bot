import os

from fastapi import Depends, status, FastAPI, Header, Query, HTTPException
from fastapi.responses import StreamingResponse

from game import Game
from twitter2048.asynchronous import Tweet, continue_game, new_game, client, get_last_game_tweet


def check_auth(authorization: str = Header(...)):
    if authorization != os.environ['AUTHORIZATION']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or no Authorization")


app_kwargs = {}

if "AUTHORIZATION" in os.environ:
    app_kwargs.update({'dependencies': [Depends(check_auth)]})

app = FastAPI(**app_kwargs)


@app.get('/continue')
async def continue_game_route(tweet: Tweet = Depends(get_last_game_tweet)):
    await continue_game(tweet)
    return {'info': "Success", "data": {
        "retweet_count": tweet.retweet_count, "favorite_count": tweet.favorite_count}}


@app.get('/start')
async def start():
    await new_game()
    return {'info': "Success"}


@app.get('/test-image')
async def test_image(text: str = Query("UD")):
    bytes_obj = Game.new().spawn_box().to_twitter_image_bytes(text)
    return StreamingResponse(bytes_obj, media_type="image.png")
