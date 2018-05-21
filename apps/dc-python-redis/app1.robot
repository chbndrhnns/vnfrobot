*** Settings ***
Library   VnfValidator

*** Variables ***
${DESCRIPTOR}     docker-compose.yml


*** Test Cases ***
We have the services: app, redis
  [Documentation]  According to the architecture of the application, two services are required. We validate that they exist.
  [Tags]  deployment_context

  Set deployment context
  Service "app": exists
  Service "redis": exists

Check service "app"
  [Tags]  app1
  Set service context to app

Check that the image for the service 'app' contains the correct application code
  [Documentation]  We would like the correct version of the app to be in the Docker image
  ...  (side note: putting the code directly next to the image might be bad)

  Set service context to app
  File 'app.py': contains 'I have been seen'

Check version of Python (3.5+)
  [Documentation]  As Python2 is no longer known not to work with every piece of software, we want to validate that Python3.5
  ...  is in place.

  Set service context to app
  Command "python --version": stdout contains "3.5"

Redis instance is reachable from the app
  [Documentation]  We need to be able to reach Redis via the 'redis' hostname (see the environment variable)

  Set service context to app
  Address "redis:6379": is reachable

App instance is reachable from redis
  [Documentation]  The app service needs to be reachable from the redis service
  ...  TODO: add DNS resolution for checking availability of hostnames

  Set service context to redis
  Address "app:5000": is reachable

Redis: Persistency is enabled
  [Documentation]  Redis keeps entries in memory by default. We want to store the votes, so persistency needs to be
  ...  enabled. Writes should happen every second, not instantly.
  [Tags]  redis

  Set service context to redis
  Command "redis-cli CONFIG GET appendfsync": stdout contains "appendfsync"
  Command "redis-cli CONFIG GET appendfsync": stdout contains "everysec"
  Command "redis-cli CONFIG GET appendfsync": stdout contains not "always"

Volume for redis is empty after deployment
  [Documentation]  A volume is mounted for redis. It should be empty (contain no files).
  [Tags]  redis

  Set service context to redis
  Command "ls -1 /data | wc -l": stdout contains 0

REDIS_HOST is set to "redis" for application
  [Documentation]  The variable is used to make the Python app aware of the redis hostname.
  [Tags]  kw_variable  app

  set service context to app
  Variable REDIS_HOST: is "redis"

App is listening on port 5000
  [Documentation]  The app exposes port 5000 to the public. We make sure that the port is actually open.

  Set service context to app
  Port 5000: state is open

Redis service is not reachable from a public network
  [Documentation]  Communication between redis and app happens in private, so there is no need to reach redis from the
  ...  public network.
  [Tags]  redis

  Set network context to public
  Address "redis:6379": is not reachable

In the network m2m, there are two services
  [Documentation]  Make sure there are only two services at all.

#  Set network context to m2m
#  ${services}=

The redis counter increases after sending an HTTP GET to the web server at http://<app>:5000/
  [Documentation]  Validates that the visits to the web site are actually recorded in the redis database.

  Set service context to redis
  Command "redis-cli get hits": stdout is empty

  Retrieve website

  set service context to redis
  Command "redis-cli get hits": stdout is 1


*** Keywords ***
Retrieve website
  set service context to app
  Command "wget -qO/dev/null app:5000": stderr is empty

