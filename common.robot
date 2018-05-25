*** Settings ***

Library     cirrus
Library     cirrus.RestApi  https://${host}     WITH NAME   api


*** Variables ***

&{INFRASTRUCTURE ADMIN}     user_name=administrator     password=Compaq123
&{TEST ADMIN}               user_name=test_admin        password=Compaq123


*** Keywords ***

# util

convert time range to start/end
    [Arguments]     ${range}
    [Return]        ${start}    ${end}
    @{slice}=   set variable if
    ...     "${range}" == "the nearest minimal range"   ${0, 1}
    ...     "${range}" == "the next minimal range"      ${1, 2}
    ${start}    ${end}=     cirrus.convert_slice_to_time_slot   @{slice}

    should be equal     ${start}    datetime start
    should be equal     ${end}      datetime end

logout if any
    api.logout_if_any

# hardware management

create generic hardware
    [Arguments]     ${credential}=${None}
    [Return]        ${hardware id}  ${hardware}
    log to console  create generic hardware -->
    log to console  \tcredential: ${credential}
    ${name}=    get time
    ${hardware}=        cirrus.create_hardware_data     ${name}     generic
    ${hardware id}=     api.add_hardware    ${hardware}     ${credential}

    should be equal     ${hardware}     hardware data
    should be equal     ${hardware id}  ${1}

# reservation

reserve hardware
    [Arguments]     ${hardware id}  ${start}    ${end}  ${credential}=${None}
    [Return]        ${reservation id}   ${reservation}
    log to console  reserve hardware -->
    log to console  \thardware id: ${hardware id}
    log to console  \tstart / end: ${start} / ${end}
    log to console  \tcredential: ${credential}
    ${reservation}=     cirrus.create_reservation_data  ${hardware id}  ${start}    ${end}
    ${reservation id}=  api.create_reservation  ${reservation}  ${credential}

    should be equal     ${reservation}  reservation data
    should be equal     ${reservation id}   ${2}

release hardware
    [Arguments]     ${reservation id}   ${credential}=${None}
    log to console  release hardware -->
    log to console  \treservation id: ${reservation id}
    log to console  \tcredential: ${credential}
    api.release_reservation     ${reservation id}   ${credential}

detail reservation
    [Arguments]     ${reservation id}   ${credential}=${None}
    [Return]        ${reservation}
    log to console  detail reservation -->
    log to console  \treservation id: ${reservation id}
    log to console  \tcredential: ${credential}
    ${reservation}=     api.detail_reservation  ${reservation id}   ${credential}

adjust reservation
    [Arguments]     ${reservation id}   ${delta}    ${credential}=${None}
    [Return]        ${adjusted}
    log to console  adjust reservation -->
    log to console  \treservation id: ${reservation id}
    log to console  \tdelta: ${delta}
    ${origin}=      api.detail_reservation  ${reservation id}   ${credential}
    ${adjusted}=    cirrus.adjust_reservation   ${origin}   ${delta}

    should be equal     ${adjusted}     reservation data - adjusted

reservations should be equal
    [Arguments]     ${rsv1}     ${rsv2}
    log to console  reservations should be equal -->
    log to console  \trsv1: ${rsv1}
    log to console  \trsv2: ${rsv2}
    #should be equal     ${rsv1.hw_id}   ${rsv2.hw_id}
    #should be equal     ${rsv1.start}   ${rsv2.start}
    #should be equal     ${rsv1.end}     ${rsv2.end}

reservation should not exist
    [Arguments]     ${reservation id}   ${credential}=${None}
    log to console  reservation should not exist-->
    log to console  \treservation id: ${reservation id}
    log to console  \tcredential: ${credential}

    ${reservation id}=  set variable    ${3}

    run keyword and expect error    *404*
    ...     api.detail_reservation  ${reservation id}   ${credential}
