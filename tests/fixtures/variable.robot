*** Settings ***
Library     LowLevel
Variables   settings.py

*** Test Cases ***
Check variables
    Set service context to sut
    Variable PATH: contains "usr"
    Variable PATH: contains not Python
    Variable NGINX_VERSION: is 1.13.12-1~stretch

