"""Grabbing My Activity Data From Strava"""

import os
from dotenv import load_dotenv
import requests
import json
import time
from datetime import datetime
from application.db import get_db
from application.internal_api import insert_activity, parse_description, handle_manual_activity_errors

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
        response = refresh_tokens(strava_tokens)
        print(response)
        print(response.status_code)
        # Save response as json in new variable
        new_strava_tokens = response.json()
        # Save new tokens to file
        with open("strava_tokens.json", "w") as outfile:
            json.dump(new_strava_tokens, outfile)
        # Use new Strava tokens from now
        strava_tokens = new_strava_tokens
    return strava_tokens


def refresh_tokens(strava_tokens):
    """Uses strava refresh token to get a new set of tokens."""
    r = requests.post(
        url="https://www.strava.com/oauth/token",
        data={
            "client_id": os.getenv("CLIENT_ID"),
            "client_secret": os.getenv("CLIENT_SECRET"),
            "grant_type": "refresh_token",
            "refresh_token": strava_tokens["refresh_token"],
            },
        )
    print(dir(r))
    print(r.ok)
    return r


def get_detailed_activity(activity_id, strava_tokens):
    """Strava request for detailed summary of {activity}.

    :param activity: Strava Activity id
    :type activity: int

    :param strava_tokens: Active tokens for use with Strava API
    :type: JSON Object

    :return: Reponse object with Strava DetailedActivity object
    :rtype: Response object
    """
    url = "https://www.strava.com/api/v3/activities"
    access_token = strava_tokens["access_token"]

    # get response object with activity from Strava
    return requests.get(url + "/" + str(activity_id) + "?access_token=" + access_token)


def get_page_of_activities(last_activity_date, page, strava_tokens):
    """Downloads specified page of strava activities.

    :param last_activity_date: Start time of most recent activity in activities table. None if table is empty.
    :type last_activity_date: DateTime str or None

    :param page: Page number for activities to get.
    :type page: int

    :param strava_tokens: Active tokens for use with Strava API
    :type: JSON Object

    :return: Response object with JSON dict of activities.
    :rtype: Response Object
    """

    url = "https://www.strava.com/api/v3/activities"
    access_token = strava_tokens["access_token"]

    if last_activity_date:
        tstamp = int(
            (
                datetime.strptime(last_activity_date, "%Y-%m-%dT%H:%M:%SZ")
                - datetime(1970, 1, 1)
            ).total_seconds()
        )

        return requests.get(
            url
            + "?access_token="
            + access_token
            + "&after="
            + str(tstamp)
            + "&per_page=200"
            + "&page="
            + str(page)
        )
    else:
        return requests.get(
            url
            + "?access_token="
            + access_token
            + "&per_page=200"
            + "&page="
            + str(page)
        )


def download_new_activities():
    """Downloads all new activities from strava (activities added after most recent activity in DB)."""
    strava_tokens = get_tokens()

    # get id of last downloaded activity in db
    last_activity_date = get_last_activity_date()

    page = 1

    while True:
        r = get_page_of_activities(last_activity_date, page, strava_tokens)
        if r.status_code != 200:
            print("Was not able to fetch summary activity array.")
            break
        print("r: ", r)
        r = r.json()
        print("r.json:", r)
        print("page: ", page)
        if not r:
            break
        print("length: ", len(r), "\n")
        for x in range(len(r)):
            print("im here")
            if r[x]["type"] == "Hike" or r[x]["type"] == "Walk":
                detailed_activity = get_detailed_activity(r[x]["id"], strava_tokens)
                if detailed_activity.status_code == 200:
                    activity = detailed_activity.json()
                    parse_description(activity)
                    handle_manual_activity_errors(activity)
                    insert_activity(activity)
                    print("activity inserted")
                else:
                    print(f"Not able to fetch detailed summary for activity {r[x]['id']}")

        page += 1


def get_last_activity_date():
    """Returns last start_date of last activity downloaded from Strava (not manual upload)"""
    db = get_db()
    return db.execute(
        "SELECT MAX(start_date) FROM activities WHERE strava_id IS NOT NULL"
    ).fetchone()[0]
