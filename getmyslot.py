import config
import tweepy
import pandas as pd
import requests
import datetime
import asyncio
import logging
import sys
import threading, queue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


async def checkMentions():
    logger.info("Retrieving mentions")
    df = pd.read_csv("UserData.csv")

    sinceID = max(df.TweetID.max(),max(failedTweet))
    for mention in tweepy.Cursor(api.mentions_timeline,since_id=sinceID).items():
        splitt = mention.text.split(" ")
        username = mention.user.screen_name
        tweetID = mention.id

        if clean:
            try:
                api.destroy_status(tweetID)
                logger.info("Clean: Deleted")
            except:
                logger.info("Clean: Skipped")
                continue
        else:
            try:
                pin = splitt[2]
                age = int(splitt[3].split("+")[0])
                reply = "@" + username + " You have been successfuly subscribed. I will be reminding you when vaccine slot is available at your pincode " + pin
                api.update_status(reply,tweetID)
                df = df.append({ "Username": username,"TweetID": tweetID, "Pin": pin, "Age": age},ignore_index=True)
                df.to_csv("UserData.csv", index=False)
                print(df.head())
                logger.info(str(pin),str(age),username,str(tweetID))
            except:
                reply = "@" + username + " " + 'There seems to be an error. Please make sure your tweet is in the following format ' + "errorid:" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                file = open("ss.jpeg" , "rb")
                r1 = api.media_upload(filename="ss.jpeg",file=file)
                api.update_status(reply,tweetID,media_ids=[r1.media_id_string])
                logger.info("Wrong tweet")
                failedTweet.append(tweetID)
                continue
    df.to_csv("UserData.csv",index=False)
    logger.info("Waiting...For Mentions")
    await  asyncio.sleep(10)

async def checkCowin():
    logger.info("Checking COWIN")
    baseURL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?"
    coDF = pd.read_csv("UserData.csv")
    for date in dates:
        for pin in coDF["Pin"].unique():

            completeURL = baseURL+"date="+date + "&pincode=" + str(pin)
            try:
                sessions = requests.get(completeURL).json()["sessions"]
                if sessions:
                    vaccines = {"COVISHIELD" : False, "COVAXIN" : False}
                    minAge = {18:False,45:False}
                    availableCapacity = sys.maxsize

                    for session in sessions:
                        availableCapacity = min(availableCapacity,int(session["available_capacity"]))
                        vaccines[session["vaccine"]] = True
                        minAge[session["min_age_limit"]] = True
                    if minAge[18]:
                        tweetAt(availableCapacity,vaccines,pin,date,18)
                    if minAge[45]:
                        tweetAt(availableCapacity,vaccines,pin,date,45)

                else:
                    continue
            except:
                logger.info("Failed to get new sessions")
            finally:
                logger.info("Waiting...For COWIN")
                await asyncio.sleep(3)

def tweetAt(availableCapacity,vaccines,pin,date,age):

    reply = "Atleast " + str(availableCapacity) + " slot(s) for " + " and ".join([v for v,b in vaccines.items() if b == True]) + " is available for age " + str(age) + "+ at pin " + str(pin) + " for " + date
    newDF = coDF.dropna()
    tweetIDs = newDF.loc[(df["Age"]==age) & (df["Pin"]==pin),["TweetID"]]



    for tweetID in tweetIDs.TweetID:
        username = newDF.loc[newDF["TweetID"]==tweetID,["Username"]].Username.item()
        tweet = "@" + username + " " + reply
        alert = newDF.loc[newDF["TweetID"]==tweetID, ["Alert"]].Alert.item()

        if pd.isna(alert) or int(datetime.datetime.now().strftime("%d%H%M")) - alert > 100:
            logger.info(tweet)
            api.update_status(tweet,tweetID)
            coDF.loc[cpDF["TweetID"]==1389614929078935562,"Alert"]  = int(datetime.datetime.now().strftime("%d%H%M"))

    coDF.to_csv("UserData.csv",index=False)

async def run():
    await asyncio.gather(checkMentions(),checkCowin())
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