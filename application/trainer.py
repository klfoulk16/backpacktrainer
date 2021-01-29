"""Defines app URLS that relate to the training portion of the app."""
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from application.internal_api import get_all_activities, activity_index
from application.strava_api import download_new_activities

bp = Blueprint('trainer', __name__)

# TODO create test for download activities
# TODO create tests for the previous things - tokens working, responses good,
# getting all activities added after __ time, db insertions working properly
# TODO let's put a nice refresh activities button in upper right hand corner
# so we're not making calls every time we go to index
@bp.route('/')
def index():
    """Show all the activities."""
    #download_new_activities()
    activities = activity_index()
    return render_template('trainer/index.html', activities=activities)


@bp.route('/weekly-summary')
def weekly_summary():
    """Shows summary of weekly stats."""
    import pandas as pd
    from application.db import get_db
    from application.internal_api import convert_meters_miles
    db = get_db()
    df = pd.read_sql_query("SELECT * from activities", db)
    df.start_date = pd.to_datetime(df.start_date, format="%Y-%m-%dT%H:%M:%SZ")
    df.distance = df.distance.apply(convert_meters_miles)
    totals = df[["distance", "total_elevation_gain", "start_date"]]
    totals = totals.groupby(pd.Grouper(key='start_date', freq='W')).sum()

    ave = df[["start_date", "knee_pain"]]
    ave = ave.groupby(pd.Grouper(key='start_date', freq='W')).mean().round(2)

    weekly = totals.join(ave).fillna(0)

    # figure out average weight per mile
    df['ave_weight'] = (df['weight']*df['distance'])
    # group by week
    weight = df[['ave_weight', 'start_date']].groupby(pd.Grouper(key='start_date', freq='W')).sum()
    # divide by total distance that week to get ave weight carried per mile
    weekly['weight'] = (weight['ave_weight']/weekly['distance']).fillna(0)


    # get values for graph before stringifying
    date = list(weekly.index.strftime('%Y-%m-%d'))
    distance = list(weekly.distance)
    elevation = list(weekly.total_elevation_gain)
    weight = list(weekly.weight)
    knee_pain = list(weekly.knee_pain)
    #stringify values to make decimals nicer
    def decimal_display(value):
        return f'{value:.2f}'

    weekly.distance = weekly.distance.apply(decimal_display)
    weekly.total_elevation_gain = weekly.total_elevation_gain.apply(decimal_display)
    weekly.weight = weekly.weight.apply(decimal_display)
    return render_template('trainer/weekly_summary.html', weekly=weekly.sort_index(ascending=False), date=date, distance=distance, elevation=elevation, weight=weight, knee_pain=knee_pain)

    # totals:
    # miles hiked that week
    # elevation gained

    # averages:
    # knee pain
    # miles/day
    # speed (elapsed)
    # speed (walking)

    # how to measure weights?
    # ave weight/mile 
    # ave weight/day??

    # I think averages should be per mile to get a fair 
    # account. Aka average knee pain per mile walked that week
    # versus (total knee pain / walks that week)

    # Let's tackle that later


@bp.route('/graphs')
def graphs():
    import pandas as pd
    from application.db import get_db
    from application.internal_api import convert_meters_miles
    db = get_db()
    df = pd.read_sql_query("SELECT start_date, distance from activities", db)
    date = list(df.start_date)
    distance = list(convert_meters_miles(i) for i in df.distance)
    return render_template('trainer/graphs.html', date=date, distance=distance)
