'''Initialize stashboard docker-status with docker registry service.

      python initialize-docker-status.py'''

import oauth2 as oauth
import json
import urllib
import random
import requests
from time import sleep

stashboard_server = 'docker-ci-report.dotcloud.com'
app_id = "stashboard-hrd"    # Stashboard application id

# These keys can be found at /admin/credentials
consumer_key = 'anonymous'
consumer_secret = 'anonymous'
oauth_key = 'ACCESS_TOKEN'
oauth_secret = 'ACCESS_SECRET'
admin_login = 'gi@example.com'

# Create your consumer with the proper key/secret.
# If you register your application with google, these values won't be
# anonymous and anonymous.
consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
token = oauth.Token(oauth_key, oauth_secret)

# Create our client.
client = oauth.Client(consumer, token=token)

# Base url for all rest requests
#base_url = "https://%s.appspot.com/admin/api/v1" % app_id
base_url = "http://{}:8080/admin/api/v1".format(stashboard_server)

# Login as admin prompts stashboard to initialize itself
r = requests.session()
r.get('http://{}:8080/_ah/login?email={}&admin=True&action=Login&'
    'continue=http://localhost:8080/admin'.format(
    stashboard_server, admin_login))
r.get('http://{}:8080/admin'.format(stashboard_server))
r.post('http://{}:8080/admin/setup'.format(stashboard_server))

# CREATE a new service
data = urllib.urlencode({
    "name": "registry",
    "description": "Docker registry service",
})

resp, content = client.request(base_url + "/services",
                               "POST", body=data)
service = json.loads(content)

# GET the list of possible status images
resp, content = client.request(base_url + "/status-images", "GET")
data = json.loads(content)
images = data["images"]

# Pick a random image for our status
image = random.choice(images)

# POST to the Statuses Resources to create a new Status
data = urllib.urlencode({
    "name": "Maintenance",
    "description": "The web service is under-going maintenance",
    "image": image["name"],
    "level": "WARNING",
})

resp, content = client.request(base_url + "/statuses", "POST", body=data)
status = json.loads(content)

# Ensure the new maintenance status gets updated
for l in range(5):
    resp, content = client.request(base_url + "/statuses/maintenance", "GET")
    if resp.get('status') == '200':
        break
    sleep(1)

# Create a new event with the given status and given service
data = urllib.urlencode({
    "message": "Our first event! So exciting",
    "status": status["id"].lower(),
})

print service["url"] + "/events"
resp, content = client.request(service["url"] + "/events", "POST", body=data)
print json.loads(content)
