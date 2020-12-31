DROP TABLE IF EXISTS activities;

CREATE TABLE activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    strava_activity_id INTEGER NOT NULL
);