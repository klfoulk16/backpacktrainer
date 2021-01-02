DROP TABLE IF EXISTS activities;

CREATE TABLE activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strava_activity_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    start_date DATETIME NOT NULL
);