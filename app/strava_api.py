"""Starting to play with Strava API following this article: 
https://medium.com/swlh/using-python-to-connect-to-stravas-api-and-analyse-your-activities-dummies-guide-5f49727aac86"""

import os
from dotenv import load_dotenv

# Get environment variables
load_dotenv()


def get_initial_token(code):
    """Creates strava_tokens.json with initial authorization token.

    :param code: Initial code to get token with.
    To get this code paste
    http://www.strava.com/oauth/authorize?client_id=[REPLACE_WITH_YOUR_CLIENT_ID]&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:read_all,activity:read_all
    into your browser with your client ID. Click authorize and you will be redirected to a page with the following URL:
    http://localhost/exchange_token?state=&code=[THIS_IS_THE_CODE_YOU_NEED_TO_COPY]&scope=read,activity:read_all,profile:read_all
    Pull the code from that second URL and pass it to this function.
    :type body: str
    """
    import requests
    import json

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


def get_activities():
    import requests
    import json
    import time
    from pandas import json_normalize

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
    # Loop through all activities
    url = "https://www.strava.com/api/v3/activities"
    access_token = strava_tokens["access_token"]
    # Get first page of activities from Strava with all fields
    r = requests.get(url + "?access_token=" + access_token)
    r = r.json()

    df = json_normalize(r)
    df.to_csv("strava_activities_all_fields.csv")


get_activities()
