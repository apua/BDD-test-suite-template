*** Settings ***

Library     ${CURDIR}/../resources/cirrus   https://${CIRRUS_IP}    WITH NAME   api
Library     ${CURDIR}/../resources/cirrus/keywords.py               WITH NAME   cirrus_keywords


*** Variables ***

&{INFRASTRUCTURE ADMIN}     user_name=administrator     password=Compaq123
&{TEST ADMIN}               user_name=test_admin        password=Compaq123


*** Keywords ***

# Basic wrapper

login as ${who}
    api.login   &{${who}}[user_name]    &{${who}}[password]

logout
    api.logout

create generic hardware
    [Arguments]     ${name}     ${desc}=${EMPTY}    ${credential}=${None}
    [Return]        ${hardware id}  ${hardware}
    ${hardware}=    cirrus_keywords.create hardware data
    ...     type=generic
    ...     name=${name}
    ...     desc=${desc}

    ${hardware id}=     api.add hardware    ${hardware}     credential=${credential}

reserve hardware
    [Arguments]     ${hardware id}  ${start}    ${end}  ${credential}=${None}
    [Return]        ${reservation id}   ${reservation}
    ${reservation}=     cirrus_keywords.create reservation data
    ...     ${hardware id}
    ...     ${start}    ${end}
    ${reservation id}=  api.create reservation  ${reservation}  credential=${credential}

release hardware
    [Arguments]     ${reservation id}   ${credential}=${None}
    api.release reservation     ${reservation id}   credential=${credential}

convert time range to start/end
    [Arguments]     ${slot}
    [Return]        ${start}    ${end}
    ${start}    ${end}=
    ...     run keyword if    "${slot}" == "the nearest minimal range"
    ...         cirrus_keywords.convert slice to time slot  0   1
    ...     ELSE IF           "${slot}" == "the next minimal range"
    ...         cirrus_keywords.convert slice to time slot  1   2
    log     Take start time "${start}" and end time "${end}"

reservations should be equal
    [Arguments]     ${first}    ${second}
    no operation

reservation should not exist
    [Arguments]     ${reservations id}
    run keyword and expect error    *404*
    ...     api.detail reservation  ${reservation id}

edit reservation
    [Arguments]     ${reservations id}  ${steps}=${0}
    [Return]        ${reservation id}   ${reservation}
    no operation


# BDD style

a generic hardware is created by ${who}
    ${time}=    get time
    ${hardware id}  ${hardware}=
    ...     run keyword if  "${who}" == "myself"
    ...         create generic hardware     name=${time}
    ...     ELSE
    ...         create generic hardware     name=${time}    credential=&{${who}}
    set test variable   ${hardware id}

the hardware is reserved for ${slot} by ${who}
    ${start}    ${end}=     convert time range to start/end     ${slot}
    ${reservation id}   ${reservation}=
    ...     run keyword if  "${who}" == "myself"
    ...         reserve hardware    ${hardware id}  ${start}    ${end}
    ...     ELSE
    ...         reserve hardware    ${hardware id}  ${start}    ${end}    credential=&{${who}}
    set test variable   ${reservation id}

I reserve the hardware for ${slot}
    ${start}    ${end}=     convert time range to start/end     ${slot}
    ${reservation id}   ${reservation}=
    ...     reserve hardware    ${hardware id}  ${start}    ${end}
    set test variable   ${reservation id}
    set test variable   ${reservation}

the hardware should be reserved as expected
    ${fetched reservation} =    api.detail reservation  ${reservation id}
    reservations should be equal    ${reservation}  ${fetched reservation}

I release the hardware from the reservation
    release hardware    ${reservation id}

the reservation should not exist
    reservation should not exist    ${reservation id}

I ${adjust} the reservation with ${#} unit
    ${reservation id}   ${reservation}=
    ...     run keyword if  "${adjust}" == "extend"
    ...         edit reservation    ${reservation id}   ${+${#}}
    ...     ELSE IF         "${adjust}" == "shrink"
    ...         edit reservation    ${reservation id}   ${-${#}}
    set test variable   ${reservation id}
    set test variable   ${reservation}

the reservation should be adjusted as expected
    ${fetched reservation} =    api.detail reservation  ${reservation id}
    reservations should be equal    ${reservation}  ${fetched reservation}
