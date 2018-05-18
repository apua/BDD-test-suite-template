"""
Define data type for communication between high-level and low-level keywords.

The idea "model" comes from Django ORM.
It could be improved with Python3.7 data class (PEP 557).
"""

import collections

Reservation = collections.namedtuple('Reservation', ('id', 'hw_id', 'start', 'end', 'desc', 'rrule'))
Hardware = collections.namedtuple('Hardware', ('id', 'name', 'desc', 'type'))
