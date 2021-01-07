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
    """Returns the activity with {id} from activities table in database"""
    db = get_db()
    activity = db.execute(
        'SELECT * FROM activities WHERE id=?', (id,)
    ).fetchone()
    return activity


def activity_index():
    """Fetches all activities from the activities table and prepares them for easy reading."""
    activities = get_all_activities()
    formated_activities = []
    for activity in activities:
        formated_activities.append(format_activity_for_view(activity))
    return formated_activities


def format_activity_for_view(activity):
    """Takes an activity sqllite thing?? and formats all values for easy human interpretation"""
    # format speeds/times in seconds
    formated_activity = dict(activity)
    formated_activity["moving_time"] = convert_seconds_h_m_s(activity["moving_time"])
    formated_activity["elapsed_time"] = convert_seconds_h_m_s(activity["elapsed_time"])
    formated_activity["start_date"] = convert_date(activity["start_date"])
    formated_activity["average_speed"] = convert_average_speed(activity["average_speed"])
    formated_activity["distance"] = convert_meters_miles(activity["distance"])
    formated_activity["total_elevation_gain"] = convert_meters_feet(activity["total_elevation_gain"])
    formated_activity["elev_low"] = convert_meters_feet(activity["elev_low"])
    formated_activity["elev_high"] = convert_meters_feet(activity["elev_high"])
    return formated_activity


def convert_average_speed(speed):
    """Converts average speed from meters per second to hours:minutes:seconds per mile."""
    # def convert_speed(speed):
    if speed and speed > 0:
        speed = round(1609.34/speed)
    else:
        speed = 0
    return convert_seconds_h_m_s(speed)


def convert_seconds_h_m_s(time):
    """Converts time from seconds into H:M:S string."""
    return str(datetime.timedelta(seconds=time))


def convert_meters_miles(distance):
    """Converts meters to miles i.e. for activity["distance"]"""
    if distance:
        return round(distance/1609.34, 2)
    else:
        return 0


def convert_meters_feet(distance):
    """Converts meters to feet i.e. for activity elevations"""
    if distance:
        return round(distance*3.281, 2)
    else:
        return 0


def convert_date(date):
    """Converts date to format Jan 01 2021"""
    date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
    return date.strftime("%b %d %Y")


def insert_activity(activity):
    """Inserts a prepared Activity dict into the activities table."""
    db = get_db()
    db.execute(
        'INSERT INTO activities (id, distance, moving_time, elapsed_time, total_elevation_gain, elev_high, elev_low, type, start_date, average_speed, gear_id, weight, knee_pain, ground_type, comments)'
        ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (activity['id'], activity["distance"], activity["moving_time"], activity["elapsed_time"], activity["total_elevation_gain"], activity["elev_high"], activity["elev_low"], activity["type"], activity["start_date"], activity["average_speed"], activity["gear_id"], activity["weight"], activity["knee_pain"], activity["ground_type"], activity["comments"])
    )
    db.commit()


def parse_description(activity):
    """Takes an detailed activity object and parses the description key to pull out the various bits of information I need."""
    # parse ground type, lbs, knee pain, other comments
    if not activity["description"]:
        activity["weight"] = 0
        activity["knee_pain"] = 0
        activity['ground_type'] = "trail"
        activity['comments'] = None
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


def handle_manual_activity_errors(activity):
    """Handles errors thrown when an activity is missing key:value pairs."""
    if "elev_high" not in activity:
        activity["elev_high"] = 0
    if "elev_low" not in activity:
        activity["elev_low"] = 0
