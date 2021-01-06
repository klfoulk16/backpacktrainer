"""Internal API calls."""

from application.db import get_db
import re
import datetime


def get_all_activities():
    """Return all the existing activities.

    :return: List of activities
    :rtype: list
    """
    db = get_db()
    activities = db.execute(
        'SELECT * FROM activities ORDER BY start_date DESC'
    ).fetchall()
    return activities


def get_specific_activity(id):
    db = get_db()
    activity = db.execute(
        'SELECT * FROM activities WHERE id=?', (id,)
    ).fetchone()
    return activity


def prepare_activities_for_display(activities):
    """Takes dict of activities stored in db and formats their values so they're easier to read."""
    finished_activities = []
    for activity in activities:
        activity = dict(activity)
        # format speeds/times in seconds
        activity["moving_time"] = str(datetime.timedelta(seconds = activity["moving_time"]))
        activity["elapsed_time"] = str(datetime.timedelta(seconds = activity["elapsed_time"]))
        activity["average_speed"] = str(datetime.timedelta(seconds = activity["average_speed"]))
        date = datetime.datetime.strptime(activity["start_date"], "%Y-%m-%dT%H:%M:%SZ")
        activity["start_date"] = date.strftime("%b %d %Y")
        finished_activities.append(activity)
    return finished_activities

def insert_activity(activity):
    """Inserts a prepared Activity dict into the activities table."""
    db = get_db()
    db.execute(
        'INSERT INTO activities (id, distance, moving_time, elapsed_time, total_elevation_gain, elev_high, elev_low, type, start_date, average_speed, gear_id, weight, knee_pain, ground_type, comments)'
        ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (activity['id'], activity["distance"], activity["moving_time"], activity["elapsed_time"], activity["total_elevation_gain"], activity["elev_high"], activity["elev_low"], activity["type"], activity["start_date"], activity["average_speed"], activity["gear_id"], activity["weight"], activity["knee_pain"], activity["ground_type"], activity["comments"])
    )
    db.commit()


def prepare_detailedactivity_object(activity):
    """Prepares a Strava DetailedActivity Object for insertion into the activities table."""
    activity["average_speed"] = convert_speed(activity["average_speed"])
    activity["distance"] = meters_to_miles(activity["distance"])
    activity["total_elevation_gain"] = meters_to_feet(activity["total_elevation_gain"])
    try:
        activity["elev_low"] = meters_to_feet(activity["elev_low"])
        activity["elev_high"] = meters_to_feet(activity["elev_high"])
    except Exception as e:
        # this must be a manually added activity
        activity["elev_low"] = 0
        activity["elev_high"] = 0
    activity = parse_description(activity)
    return activity


def convert_speed(speed):
    """Convert speed from meters per second to seconds per mile."""
    if speed and speed > 0:
        return round(1609.34/speed)
    else:
        return 0


def meters_to_miles(distance):
    """Converts meters to miles"""
    if distance:
        return round(distance/1609.34, 2)
    else:
        return 0


def meters_to_feet(distance):
    """Converts meters to feet"""
    if distance:
        return round(distance*3.281, 2)
    else:
        return 0


def parse_description(activity):
    """Takes an detailed activity object and parses the description key to pull out the various bits of information I need."""
    # parse ground type, lbs, knee pain, other comments
    if not activity["description"]:
        activity["weight"] = 0
        activity["knee_pain"] = 0
        activity['ground_type'] = "trail"
        activity['comments'] = None
        return activity
    else:
        comments = activity["description"]

        weight_format = re.compile(r"\d+[\.]?\d*\s?(lbs|pounds|lb)\s?(pack|bag)?")
        weight = weight_format.search(activity["description"])
        if weight:
            weight = weight.group()
            activity["weight"] = float(re.sub(r"^0|[^0-9\.]", "", weight))
            comments = re.sub(weight, "", comments)
        else:
            activity["weight"] = 0
        
        knee_pain_format = re.compile("(knee pain|Knee Pain|Knee pain):\s?\d+")
        knee_pain = knee_pain_format.search(comments)
        if knee_pain:
            knee_pain = knee_pain.group()
            activity["knee_pain"] = int(re.sub("[^0-9]", "", knee_pain))
            comments = re.sub(knee_pain, "", comments)
        else:
            activity["knee_pain"] = 0

        ground_format = re.compile("(snow|Snow|Rocky|rocky|pavement|Pavement|off-trail|Off-trail)")
        ground = ground_format.search(comments)
        if ground:
            activity['ground_type'] = ground.group().lower()
        else:
            activity['ground_type'] = "trail"

        comment_format = re.compile(r"\w.*")
        comments = comment_format.search(comments)
        if comments:
            activity['comments'] = comments.group()
        else:
            activity['comments'] = None
        return activity
