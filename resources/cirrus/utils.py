# NOTE: python2.x support, since RF takes unicode string only
import sys
if sys.version_info[0] == 2:
    str = unicode


def to_timedelta(seconds):
    """
    Convert to :type:`timedelta`

    :type secondes: Robot Framework supports time format, integer, float, or timedelta
    """
    from robot.libraries.DateTime import convert_time
    import datetime
    import numbers

    if isinstance(seconds, str):
        seconds = datetime.timedelta(seconds=convert_time(seconds))
    elif isinstance(seconds, numbers.Real):
        seconds = datetime.timedelta(seconds=seconds)
    elif isinstance(seconds, datetime.timedelta):
        pass
    else:
        type_seconds = type(seconds)
        raise TypeError(
                "Type of :arg:`seconds` should be str, int, float, or timedelta."
                " Got {type_seconds}".format(**locals())
                )
    return seconds


def ceil(dt):
    """
    Ceil `datetime` based on unit 30 min, according to Cirrsu reservation policy

    :type dt: datetime
    :rtype: datetime
    """
    import datetime

    # NOTE: hard code `unit = 30min`
    if dt.second > 0 or dt.microsecond > 0:
        dt = dt.replace(second=0).replace(microsecond=0) + datetime.timedelta(minutes=1)

    if dt.minute < 30:
        return dt.replace(minute=30)
    else:
        return (dt+datetime.timedelta(hours=1)).replace(minute=0)


utc_isoformat = '%Y-%m-%dT%H:%M:%S.%fZ'


def parse_isoformat(s):
    import datetime
    return datetime.datetime.strptime(s, utc_isoformat)


def to_isoformat(dt):
    return dt.strftime(utc_isoformat)
