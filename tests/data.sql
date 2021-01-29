INSERT INTO activities(
  strava_id,
  distance,
  moving_time,
  elapsed_time,
  total_elevation_gain,
  elev_high,
  elev_low,
  type,
  start_date,
  average_speed,
  gear_id,
  weight,
  knee_pain,
  ground_type,
  comments
  )
VALUES
  (4526779165, 6626.1, 6293, 10888, 126.7, 446.6, 17.2, "Hike", "2020-12-27T19:45:05Z", 1.053, "b12345678987654321", 10, 2, "trail", NULL),
  (4526779166, 18349, 3209, 3421, 310, 246.2, 9.2, "Walk", "2020-10-06T22:13:31Z", 1.246, "b12345678987654321", 5, 0, "snow", "walked with Jack");



INSERT INTO gear (strava_id, name)
VALUES ("b12345678987654321", "Hiking Boots");