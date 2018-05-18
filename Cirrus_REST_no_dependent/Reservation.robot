*** Settings ***

Resource    common.robot


*** Test Cases ***

# Reserve Hardware 1

Infrastructure admin reserves an own newly added hardware
    [Tags]  RAT
    [Setup]
    ...     Login as infrastructure admin

    Given a generic hardware is created by myself
    When I reserve the hardware for the nearest minimal range
    Then the hardware should be reserved as expected

    [Teardown]
    ...     Logout

Test admin reserves an own newly added hardware
    [Tags]  RAT
    [Setup]
    ...     Login as test admin

    Given a generic hardware is created by myself
    When I reserve the hardware for the nearest minimal range
    Then the hardware should be reserved as expected

    [Teardown]
    ...     Logout

# Reserve Hardware 2

Test admin reserves others' newly added hardware
    [Tags]  RAT
    [Setup]
    ...     Login as test admin

    Given a generic hardware is created by infrastructure admin
    When I reserve the hardware for the nearest minimal range
    Then the hardware should be reserved as expected

    [Teardown]
    ...     Logout

# Reserve Hardware 3

Test admin reserves others' reserved hardware
    [Tags]  FAST
    [Setup]
    ...     Login as test admin

    Given a generic hardware is created by infrastructure admin
    and the hardware is reserved for the nearest minimal range by infrastructure admin
    When I reserve the hardware for the next minimal range
    Then the hardware should be reserved as expected

    [Teardown]
    ...     Logout

# Release Hardware

Infrastructure administrator releases hardware reserved by himself
    [Documentation]
    ...     Note: in this test, take the next minimal range to reserve the hardware,
    ...     which is long enough to assure the reservation will be cleaned up
    ...     after released.
    [Tags]  RAT
    [Setup]
    ...     Login as infrastructure admin

    Given a generic hardware is created by myself
    and the hardware is reserved for the next minimal range by myself
    When I release the hardware from the reservation
    Then the reservation should not exist

    [Teardown]
    ...     Logout

Test administrator releases hardware reserved by himself
    [Documentation]
    ...     Note: in this test, take the next minimal range to reserve the hardware,
    ...     which is long enough to assure the reservation will be cleaned up
    ...     after released.
    [Tags]  RAT
    [Setup]
    ...     Login as test admin

    Given a generic hardware is created by myself
    and the hardware is reserved for the next minimal range by myself
    When I release the hardware from the reservation
    Then the reservation should not exist

# Edit Hardware Reservation

Infrastructure administrator extends/shortens hardware reservation time
    [Tags]  RAT
    [Setup]
    ...     Login as infrastructure admin

    Given a generic hardware is created by myself
    and the hardware is reserved for the nearest minimal range by myself

    When I extend the reservation with 1 unit
    Then the reservation should be adjusted as expected

    When I shrink the reservation with 1 unit
    Then the reservation should be adjusted as expected

    [Teardown]
    ...     Logout

Test administrator extends/shortens hardware reservation time
    [Tags]  RAT
    [Setup]
    ...     Login as test admin

    Given a generic hardware is created by myself
    and the hardware is reserved for the nearest minimal range by myself

    When I extend the reservation with 1 unit
    Then the reservation should be adjusted as expected

    When I shrink the reservation with 1 unit
    Then the reservation should be adjusted as expected

    [Teardown]
    ...     Logout
