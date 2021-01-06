"""Grabbing My Activity Data From Strava"""

import os
from dotenv import load_dotenv
import requests
import json
import time
from datetime import datetime
from application.db import get_db
from application.internal_api import insert_activity, prepare_detailedactivity_object

# Get environment variables
load_dotenv()


def token_test():
    # learning how to use pytest mocker
    return get_tokens()

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


def download_activities():
    """
    What will this function do:

    1. Download all activities until activity date of the last activity in the database (all time if db empty)
        i. If the type is walk or hike, get detailed summary and insert values into activities table in db
    2. Call the detailed description for each activity id in dict.
        i. Add db row with important info for each activity id

    For now:
    1. Same.
        i. Insert type, id, date in db
    """
    strava_tokens = get_tokens()

    # get id of last activity in db
    db = get_db()
    last_activity_date = db.execute(
        "SELECT MAX(start_date) FROM activities"
    ).fetchone()[0]

    page = 1

    while True:
        r = strava_list_activities_page(last_activity_date, page, strava_tokens)
        if r.status_code != 200:
            print("Was not able to fetch summary activity array.")
            break
        r = r.json()
        if not r:
            break

        for x in range(len(r)):
            if r[x]["type"] == "Hike" or r[x]["type"] == "Walk":
                detailed_activity = get_detailed_activity(r[x]["id"], strava_tokens)
                if detailed_activity.status_code == 200:
                    activity = prepare_detailedactivity_object(detailed_activity.json())
                    insert_activity(activity)
                else:
                    print(f"Not able to fetch detailed summary for activity {x['id']}")

        page += 1


def strava_list_activities_page(last_activity_date, page, strava_tokens):
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


def see_what___returns():
    strava_tokens = get_tokens()
    last_activity_date = "2021-01-03T21:32:51Z"
    page = 1
    stuff = strava_list_activities_page(last_activity_date, page, strava_tokens)
    print(stuff.json())


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
