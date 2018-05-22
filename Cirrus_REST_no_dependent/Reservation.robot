*** Settings ***

#Resource    common.robot
Test teardown   logout if any


*** Keywords ***

${who:they|\w+ admin|and} create a generic hardware
    log to console  who: ${who}

${who:they|\w+ admin|and} reserve the hardware for ${range}
    log to console  who: ${who}
    log to console  range: ${range}

they should see the reservation as expected
    no operation

they ${operate:extend|shrink} the reservation with ${#} unit
    log to console  operate: ${operate}
    log to console  quantity: ${#}

they release the hardware from the reservation
    no operation

both test admin and infrastructure admin should see the reservation as expected
    no operation

they should see the reservation does not exist
    no operation

they should see the reservation has been adjusted as expected
    no operation

logout if any
    no operation


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
