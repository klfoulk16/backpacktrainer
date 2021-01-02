"""Grabbing My Activity Data From Strava"""

import os
from dotenv import load_dotenv
import requests
import json
import time
from datetime import datetime
from application.db import get_db

# Get environment variables
load_dotenv()


def get_initial_token(code):
    """Creates strava_tokens.json with initial authorization token.

    :param code: Initial code to get token with.
    To get this code paste
    http://www.strava.com/oauth/authorize?client_id=[REPLACE_WITH_YOUR_CLIENT_ID]&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:read_all,activity:read_all
    into your browser with your client ID. Click authorize and you will be
    redirected to a page with the following URL:
    http://localhost/exchange_token?state=&code=[THIS_IS_THE_CODE_YOU_NEED_TO_COPY]&scope=read,activity:read_all,profile:read_all
    Pull the code from that second URL and pass it to this function.
    :type body: str
    """
    # Make Strava auth API call with your
    # client_code, client_secret and code
    response = requests.post(
        url="https://www.strava.com/oauth/token",
        data={
            "client_id": os.getenv("CLIENT_ID"),
            "client_secret": os.getenv("CLIENT_SECRET"),
            "code": code,
            "grant_type": "authorization_code",
        },
    )
    # Save json response as a variable
    strava_tokens = response.json()
    # Save tokens to file
    with open("strava_tokens.json", "w") as outfile:
        json.dump(strava_tokens, outfile)
    # Open JSON file and print the file contents
    # to check it's worked properly
    with open("strava_tokens.json") as check:
        data = json.load(check)
    print(data)


def get_tokens():
    """Gets token either from file or by using refresh token if old one is expired.

    :return: Active tokens for use with Strava API
    :rtype: JSON Object
    """
    # USER PROOFING make sure that strava_tokens.json exists with proper
    # refresh token and if not prompt user to use get_initial_token()
    # Get the tokens from file to connect to Strava
    with open("strava_tokens.json") as json_file:
        strava_tokens = json.load(json_file)
    # If access_token has expired then
    # use the refresh_token to get the new access_token
    if strava_tokens["expires_at"] < time.time():
        # Make Strava auth API call with current refresh token
        response = requests.post(
            url="https://www.strava.com/oauth/token",
            data={
                "client_id": os.getenv("CLIENT_ID"),
                "client_secret": os.getenv("CLIENT_SECRET"),
                "grant_type": "refresh_token",
                "refresh_token": strava_tokens["refresh_token"],
            },
        )
        # Save response as json in new variable
        new_strava_tokens = response.json()
        # Save new tokens to file
        with open("strava_tokens.json", "w") as outfile:
            json.dump(new_strava_tokens, outfile)
        # Use new Strava tokens from now
        strava_tokens = new_strava_tokens
    return strava_tokens


def initial_activity_download():
    """Conducts the first download of activities from strava.
    """
    strava_tokens = get_tokens()

    page = 1
    url = "https://www.strava.com/api/v3/activities"
    access_token = strava_tokens['access_token']
    
    while True:
        # get page of activities ffrom Strava
        r = requests.get(url + '?access_token=' + access_token + '&per_page=200' + '&page=' + str(page))
        r = r.json()

        # if no more results, break loop
        if (not r):
            break

        # otherwise add new data to db
        for x in range(len(r)):
            db = get_db()
            db.execute(
                'INSERT INTO activities (strava_activity_id, type, start_date)'
                ' VALUES (?, ?, ?)',
                (r[x]['id'], r[x]['type'], r[x]['start_date'])
            )
            db.commit()
        
        # increment page
        page += 1


def subsequent_activity_download(last_activity_date):
    """Downloads all new activities in strava.

    :param last_activity_date: Start time of most recent activity in activities table.
    :type last_activity_date: DateTime
    """
    strava_tokens = get_tokens()

    url = "https://www.strava.com/api/v3/activities"
    access_token = strava_tokens['access_token']
    # TODO make sure this date is accurate. is my computer converting the times right?
    # it got one new activity but it didn't get a second one when I added it right afterwards.
    tstamp = int(datetime.strptime(last_activity_date, "%Y-%m-%dT%H:%M:%SZ").timestamp())

    r = requests.get(url + '?access_token=' + access_token + '&after=' + str(tstamp))
    r = r.json()

    # if no results, break
    if r:
        # add new data to db
        for x in range(len(r)):
            db = get_db()
            db.execute(
                'INSERT INTO activities (strava_activity_id, type, start_date)'
                ' VALUES (?, ?, ?)',
                (r[x]['id'], r[x]['type'], r[x]['start_date'])
            )
            db.commit()


def download_activities():
    """
    What will this function do:

    1. Download all activities until activity date of the last activity in the database (all time if db empty)
        i. If the type is walk or hike, store the activity id in a dict
    2. Call the detailed description for each activity id in dict.
        i. Add db row with important info for each activity id
    
    For now:
    1. Same.
        i. Insert type, id, date in db
    """

    # get id of last activity in db
    db = get_db()
    last_activity_date = db.execute(
        'SELECT MAX(start_date) FROM activities'
    ).fetchone()[0]

    if last_activity_date is None:
        # get all activities
        initial_activity_download()
    else:
        subsequent_activity_download(last_activity_date)
