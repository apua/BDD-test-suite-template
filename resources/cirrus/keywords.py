# TODO: make this module not be imported directly, and fix below to relative import
from cirrus.utils import to_timedelta, parse_isoformat, ceil
from cirrus.models import Reservation, Hardware

import collections
import datetime


def should_be_an_editable_reservation(rsv, lifetime=0):
    now = datetime.datetime.utcnow()
    lifetime = to_timedelta(lifetime)

    if rsv.end - now <= lifetime:
        raise AssertionError(
                "Reservation is not editable since it has not enough lifetime for \"{lifetime}\""
                " with end time \"{rsv.end}\" in current time \"{now}\"".format(**locals())
                )


def extend_reservation(rsv, duration):
    return rsv._replace(end=rsv.end+to_timedelta(duration))


def shrink_reservation(rsv, duration):
    return rsv._replace(end=rsv.end-to_timedelta(duration))


def find_available_start(members, duration):
    duration = to_timedelta(duration)

    now = datetime.datetime.utcnow()
    buff = datetime.timedelta(seconds=60)
    min_start = ceil(now+buff)

    Rsv = collections.namedtuple('Rsv', ('id', 'start', 'end'))
    rsvs = [
        Rsv(
            id=int(m['attributes']['id']),
            start=parse_isoformat(m['attributes']['start_time']),
            end=parse_isoformat(m['attributes']['end_time']),
        ) for m in members
        ]
    sorted_rsvs = sorted(rsvs, key=lambda d: d.start)
    avail_rsvs = [rsv for rsv in sorted_rsvs if rsv.end >= min_start]

    if not avail_rsvs:
        return min_start

    if avail_rsvs[0].start - min_start >= duration:
        return min_start

    if len(avail_rsvs) == 1:
        return avail_rsvs[0].end

    for a,b in zip(avail_rsvs[:-1], avail_rsvs[1:]):
        if b.start - a.end >= duration:
            return a.end
    else:
        return b.end


def create_hardware(name, desc, type):
    """
    :rtype: namedtuple('Hardware', ('id', 'name', 'desc', 'type'))
    """
    import collections

    Hardware = collections.namedtuple('Hardware', ('id', 'name', 'desc', 'type'))
    return Hardware(None, name, desc, type)


#------------------------------------------------------------------------------- 

def create_hardware_data(name, type, desc='', id=None):
    return Hardware(**locals())

def create_reservation_data(hw_id, start, end, desc='', rrule='', id=None):
    return Reservation(**locals())

def convert_slice_to_time_slot(a, b):
    return datetime.datetime.utcnow(), datetime.datetime.utcnow()
