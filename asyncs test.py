import config
import tweepy
import pandas as pd
import requests
import datetime
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

async def checkMentions():
    print("Check Mention")
    await  asyncio.sleep(1)

async def checkCowin():
    logger.info("CheckCowin")
    await asyncio.sleep(10)


async def run():
    await  asyncio.gather(checkCowin(),checkMentions())
    await run()
if __name__ == "__main__":
    today = datetime.datetime.today()
    tomorrow = today + datetime.timedelta(days=1)
    dayAfter = today + datetime.timedelta(days=2)
    dates = [today.strftime("%d-%m-%Y"), tomorrow.strftime("%d-%m-%Y"), dayAfter.strftime("%d-%m-%Y")]
    failedTweet = [1389616776728645636]

    clean = False
    df = pd.read_csv("UserData.csv")

    auth = tweepy.OAuthHandler(config.key, config.scret_key)
    auth.set_access_token(config.access_token, config.access_token_secret)
    api = tweepy.API(auth)

    asyncio.run(run())


