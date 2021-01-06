DROP TABLE IF EXISTS activities;

CREATE TABLE activities (
    id INTEGER PRIMARY KEY,
    /* Given in meters */
    distance FLOAT,
    /* The activity's moving time, in seconds */
    moving_time INTEGER,
    /* The activity's elapsed time, in seconds */
    elapsed_time INTEGER,
    total_elevation_gain FLOAT,
    elev_high FLOAT NULL NULL,
    elev_low FLOAT,
    type TEXT,
    start_date DATETIME,
    average_speed FLOAT,
    gear_id STRING,
    weight FLOAT,
    knee_pain INTEGER,
    ground_type STRING,
    comments STRING
);


DROP TABLE IF EXISTS gear;

CREATE TABLE gear (
    strava_id STRING PRIMARY KEY NOT NULL,
    name STRING NOT NULL
)