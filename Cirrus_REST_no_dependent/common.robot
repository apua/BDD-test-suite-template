*** Variables ***

&{INFRASTRUCTURE ADMIN}     user_name=administrator     password=Compaq123
&{TEST ADMIN}               user_name=test_admin        password=Compaq123


*** Keywords ***
# common.util

convert time range to start/end
    [Arguments]     ${range}
    [Return]        ${start}    ${end}
    ${start}=           set variable    "datetime start"
    ${end}=             set variable    "datetime end"

logout if any
    no operation

# common.hardware management

create generic hardware
    [Arguments]     ${credential}=${None}
    [Return]        ${hardware id}  ${hardware}
    log to console  create generic hardware -->
    log to console  \tcredential: ${credential}
    ${name}=    get time
    ${hardware id}=     set variable    1
    ${hardware}=        set variable    "hardware data"

# common.reservation

reserve hardware
    [Arguments]     ${hardware id}  ${start}    ${end}  ${credential}=${None}
    [Return]        ${reservation id}   ${reservation}
    log to console  reserve hardware -->
    log to console  \thardware id: ${hardware id}
    log to console  \tstart / end: ${start} / ${end}
    log to console  \tcredential: ${credential}
    ${reservation id}=  set variable    2
    ${reservation}=     set variable    "reservation data"

release hardware
    [Arguments]     ${reservation id}   ${credential}=${None}
    log to console  release hardware -->
    log to console  \treservation id: ${reservation id}
    log to console  \tcredential: ${credential}

adjust reservation
    [Arguments]     ${reservation id}   ${delta}
    [Return]        ${reservation}
    log to console  adjust reservation -->
    log to console  \treservation id: ${reservation id}
    log to console  \tdelta: ${delta}
    ${reservation}=     set variable    "reservation data - adjusted"

reservation should be as expected
    [Arguments]     ${reservation id}   ${reservation}  ${credential}=${None}
    log to console  reservation should be as expected -->
    log to console  \treservation id: ${reservation id}
    log to console  \treservation: ${reservation}
    log to console  \tcredential: ${credential}
    ${reservation_}=    set variable    ${reservation}
    should be true      ${True}
