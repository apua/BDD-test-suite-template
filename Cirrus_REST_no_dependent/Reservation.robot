*** Settings ***

Resource    common.robot
Test teardown   logout if any


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
