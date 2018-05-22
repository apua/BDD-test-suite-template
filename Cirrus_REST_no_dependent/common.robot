*** Variables ***

&{INFRASTRUCTURE ADMIN}     user_name=administrator     password=Compaq123
&{TEST ADMIN}               user_name=test_admin        password=Compaq123


*** Keywords ***
# common.util

convert time range to start/end
    [Arguments]     ${range}
    [Return]        ${start}    ${end}
    @{slice}=   set variable if
    ...     "${range}" == "the nearest minimal range"   ${0, 1}
    ...     "${range}" == "the next minimal range"      ${1, 2}
    #${start}    ${end}=     cirrus.convert_slice_to_time_slot   @{slice}
    ${start}=           set variable    "datetime start"
    ${end}=             set variable    "datetime end"

logout if any
    #${api}=     get library instance    api
    #run keyword if  ${api.client.token}     api.logout
    no operation

# common.hardware management

create generic hardware
    [Arguments]     ${credential}=${None}
    [Return]        ${hardware id}  ${hardware}
    log to console  create generic hardware -->
    log to console  \tcredential: ${credential}
    ${name}=    get time
    #${hardware}=        cirrus.create_hardware_data     ${name}     generic
    #${hardware id}=     api.add_hardware    ${hardware}     ${credential}
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
    #${reservation}=     cirrus.create_reservation_data  ${hardware id}  ${start}    ${end}
    #${reservation id}=  api.create_reservation  ${reservation}  ${credential}
    ${reservation id}=  set variable    2
    ${reservation}=     set variable    "reservation data"

release hardware
    [Arguments]     ${reservation id}   ${credential}=${None}
    log to console  release hardware -->
    log to console  \treservation id: ${reservation id}
    log to console  \tcredential: ${credential}
    #api.release_reservation     ${reservation id}   ${credential}

adjust reservation
    [Arguments]     ${reservation id}   ${delta}    ${credential}=${None}
    [Return]        ${adjusted}
    log to console  adjust reservation -->
    log to console  \treservation id: ${reservation id}
    log to console  \tdelta: ${delta}
    #${origin}=      api.detail_reservation  ${reservation id}   ${credential}
    #${adjusted}=    cirrus.adjust_reservation   ${origin}   ${delta}
    ${adjusted}=    set variable    "reservation data - adjusted"

reservation should be as expected
    [Arguments]     ${reservation id}   ${expect}  ${credential}=${None}
    log to console  reservation should be as expected -->
    log to console  \treservation id: ${reservation id}
    log to console  \texpected reservation: ${expect}
    log to console  \tcredential: ${credential}
    #run keyword if  ${expect}
    #...         run keywords
    #...         ${current}=     api.detail_reservation  ${reservation id}   ${credential}
    #...         cirrus.reservations_should_be_equal     ${current}  ${expect}
    #...     ELSE
    #...         cirrus.reservations_should_not_exist    ${reservation id}   ${credential}
