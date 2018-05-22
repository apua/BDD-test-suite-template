*** Settings ***

#Resource    common.robot
Test teardown   logout if any


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


*** Keywords ***

${who:they|\w+ admin|and} create a generic hardware
    log to console  who: ${who}

    ${credential}=  set variable if     "${who}" in ("they", "and")     ${None}     &{${who}}
    ${hardware id}  ${hardware}=    create generic hardware     ${credential}
    set test variable   ${hardware id}
    set test variable   ${hardware}

${who:they|\w+ admin|and} reserve the hardware for ${range}
    log to console  who: ${who}
    log to console  range: ${range}
    log to console  the hardware ID: ${hardware id}

    ${start}    ${end}=     convert time range to start/end     ${range}
    ${credential}=  set variable if     "${who}" in ("they", "and")     ${None}     &{${who}}
    ${reservation id}   ${reservation}=
    ...     reserve hardware    ${hardware id}  ${start}    ${end}  ${credential}
    set test variable   ${reservation id}
    set test variable   ${reservation}

they ${adjust:extend|shrink} the reservation with ${#} unit
    log to console  adjust: ${adjust}
    log to console  number: ${#}
    log to console  the reservation ID: ${reservation id}

    ${delta}=    set variable if
    ...     "${adjust}" == "extend"     ${+${#}}
    ...     "${adjust}" == "shrink"     ${-${#}}
    ${adjusted reservation}=    adjust reservation  ${reservation id}   ${delta}
    set test variable   ${adjusted reservation}

they release the hardware from the reservation
    log to console  the reservation ID: ${reservation id}

    release hardware    ${reservation id}

they should see the reservation as expected
    log to console  the reservation ID: ${reservation id}
    log to console  the reservation: ${reservation}

    reservation should be as expected   ${reservation id}   expect=${reservation}

both test admin and infrastructure admin should see the reservation as expected
    log to console  the reservation ID: ${reservation id}
    log to console  the reservation: ${reservation}

    reservation should be as expected   ${reservation id}   ${reservation}  ${test admin}
    reservation should be as expected   ${reservation id}   ${reservation}  ${infrastructure admin}

they should see the reservation does not exist
    log to console  the reservation ID: ${reservation id}

    reservation should be as expected   ${reservation id}   expect=${None}

they should see the reservation has been adjusted as expected
    log to console  the reservation ID: ${reservation id}
    log to console  the adjusted reservation: ${adjusted reservation}

    reservation should be as expected   ${reservation id}   expect=${adjusted reservation}


*** Test Cases ***

# Reserve Hardware 1

Infrastructure admin reserves an own newly added hardware
    [Tags]  RAT

    Given infrastructure admin create a generic hardware
    When they reserve the hardware for the nearest minimal range
    Then they should see the reservation as expected

Test admin reserves an own newly added hardware
    [Tags]  RAT

    Given test admin create a generic hardware
    When they reserve the hardware for the nearest minimal range
    Then they should see the reservation as expected

# Reserve Hardware 2

Test admin reserves others' newly added hardware
    [Documentation]
    ...     Take infrastructure admin as the other user
    [Tags]  RAT

    Given infrastructure admin create a generic hardware
    When test admin reserve the hardware for the nearest minimal range
    Then both test admin and infrastructure admin should see the reservation as expected

# Reserve Hardware 3

Test admin reserves others' reserved hardware
    [Tags]  FAST

    Given infrastructure admin create a generic hardware
    and reserve the hardware for the nearest minimal range
    When test admin reserve the hardware for the next minimal range
    Then both test admin and infrastructure admin should see the reservation as expected

# Release Hardware

Infrastructure administrator releases hardware reserved by himself
    [Documentation]
    ...     Note: in this test, take the next minimal range to reserve the hardware,
    ...     which is long enough to assure the reservation will be cleaned up
    ...     after released.
    [Tags]  RAT

    Given infrastructure admin create a generic hardware
    and reserve the hardware for the next minimal range
    When they release the hardware from the reservation
    Then they should see the reservation does not exist

Test administrator releases hardware reserved by himself
    [Documentation]
    ...     Note: in this test, take the next minimal range to reserve the hardware,
    ...     which is long enough to assure the reservation will be cleaned up
    ...     after released.
    [Tags]  RAT

    Given test admin create a generic hardware
    and reserve the hardware for the next minimal range
    When they release the hardware from the reservation
    Then they should see the reservation does not exist

# Edit Hardware Reservation

Infrastructure administrator extends/shortens hardware reservation time
    [Tags]  RAT

    Given infrastructure admin create a generic hardware
    and reserve the hardware for the nearest minimal range

    When they extend the reservation with 1 unit
    Then they should see the reservation has been adjusted as expected

    When they shrink the reservation with 1 unit
    Then they should see the reservation has been adjusted as expected

Test administrator extends/shortens hardware reservation time
    [Tags]  RAT

    Given test admin create a generic hardware
    and reserve the hardware for the nearest minimal range

    When they extend the reservation with 1 unit
    Then they should see the reservation has been adjusted as expected

    When they shrink the reservation with 1 unit
    Then they should see the reservation has been adjusted as expected
