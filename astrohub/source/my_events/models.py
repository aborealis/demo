"""Event table structure in the database"""
from datetime import datetime
from pytz import all_timezones, timezone
from django.db import models
from my_profile.models import Entity


def get_now_with_offsets(tz: str):
    """Returns the current time considering the specified time zone"""
    _tz = timezone(tz)
    return datetime.now(_tz)


def get_gmt_offset(date_time: datetime):
    """Returns the time zone by time zone name"""
    offset = date_time.strftime('%z')
    return offset[:3] + ':' + offset[3:]


def tz_offset(dt: datetime) -> float:
    """Returns the time zone offset in seconds"""
    offset = dt.utcoffset()
    return offset.total_seconds() if offset else 0


EVENT_TYPE = (
    ('conference', 'Conference'),
    ('webinar', 'Webinar'),
    ('course', 'Course'),
    ('other', 'Other')
)

TIMEZONES = [get_now_with_offsets(tz) for tz in all_timezones]
TIMEZONES.sort(key=tz_offset)
TIMEZONES = [get_gmt_offset(tz) for tz in TIMEZONES]
TIMEZONES = {key: key for key in TIMEZONES}.items()

DURATION = (
    ('oneday', 'One-day event'),
    ('multiday', 'Multi-day event'),
)

FORMAT = (
    ('online', 'Online'),
    ('in_person', 'In-person'),
    ('hybrid', 'Online & in-person')
)

AUDIENCE = (
    ('newbies', 'Newbies in astrology'),
    ('advanced', 'Advanced astrologers'),
    ('any', 'Any level'),
)


class Event(models.Model):
    """Event model"""
    entity = models.ForeignKey(Entity, on_delete=models.DO_NOTHING)
    date = models.DateTimeField()
    timezone = models.CharField(
        max_length=32,
        choices=TIMEZONES,
        default='+00:00'
    )
    type = models.CharField(choices=EVENT_TYPE, max_length=100)
    image = models.ImageField(upload_to="static/img/event/", blank=False)
    title = models.CharField(max_length=100)
    seo_title = models.CharField(max_length=100)
    seo_description = models.CharField(max_length=200)
    description = models.TextField()
    abstract = models.TextField(max_length=150)
    registration_url = models.CharField(max_length=200)
    duration = models.CharField(
        max_length=50,
        choices=DURATION,
        default='oneday'
    )
    format = models.CharField(
        max_length=50,
        choices=FORMAT,
        default='online'
    )
    audience = models.CharField(
        max_length=50,
        choices=AUDIENCE,
        default='any'
    )

    def __str__(self) -> str:
        return f'{self.title}'

    def get_absolute_url(self):
        """Returns the absolute path to the page"""
        return f"/events/{self.pk}/"
