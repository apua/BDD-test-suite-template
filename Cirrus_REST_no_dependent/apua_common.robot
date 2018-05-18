*** Settings ***
#Library     ${CURDIR}/../resources/cirrus   https://${CIRRUS_IP}    WITH NAME   api
#Library     ${CURDIR}/../resources/cirrus/keywords.py               WITH NAME   cirrus_keywords

Library     cirrus  https://${CIRRUS_IP}    WITH NAME   api
#Suite setup     import library   cirrus  https://${CIRRUS_IP}    WITH NAME   api

*** keywords ***
login
    api.login   user_name=administrator   password=Compaq123

logout
    api.logout
