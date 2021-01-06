Hi I'm designing a web app to help track my backpacking rehab process.

Problem/Solution:
1. Don't understand authentication explanation in strava docs.
    a. Found simple medium article to help
    https://medium.com/swlh/using-python-to-connect-to-stravas-api-and-analyse-your-activities-dummies-guide-5f49727aac86
2. Listing all activities doesn't include the description. My plan was to parse the description for the weight and potentially other factors.
    a. Could list weight in title.
    b. Could specifically call all 'hike' activities using their id to get descriptions.

# MVP

# Create function that tests that strava_api.get_token() returns an active non-expired token

# go through activities in strava and see how many comments mention shoes. 
# Potentially parse that out if no shoe was specifically specified

# create data visualizations using the data
    # weight vs distance
    # weight vs speed
    # weight vs height
    # can I combine all of these?
    # create list that displays all walks and flags a hike if it is abnormal 
    # meaning I upped weight, elevation, speed, distance, etc
    # parse out shoes and pain to flag hikes that got pain and see if anything was a big jump

# Put the new things on the website to show.




#Part 2:

# create background celery worker that checks to see if a new activity was added (and for new activities instead of all)
    # then add new activity to db
    