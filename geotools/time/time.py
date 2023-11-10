#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: time.py
#
# Copyright (C) 2017 Vangelis Zacharis
#
# This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Main code for geotools.time

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging

import numpy as np


__author__ = '''Vangelis Zacharis <vangelis.zacharis@yandex.com>'''
__docformat__ = '''google'''
__date__ = '''2017-11-18'''
__copyright__ = '''Copyright 2017, Vangelis Zacharis'''
__credits__ = ["Vangelis Zacharis"]
__license__ = '''GNU GPL v3.0'''
__maintainer__ = '''Vangelis Zacharis'''
__email__ = '''<vangelis.zacharis@yandex.com>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


# This is the main prefix used for logging
LOGGER_BASENAME = '''geotools'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


class CoreGeoTime(object):
    """
Core class for time.

Provide methods to deal with time formats in Geodesy, using
numpy.datetime64 objects, up to nanosecond accuracy.
Knows:
    GPST: GPS Time (GPS week number, seconds of week),
    fYear: fractional Year,
    YD: year, doy (day of year), seconds of day,
    JD: Julian date
    MJD: Modified Julian Date (JD - 2400000.5),
    J2000: epoch in the J2000 time frame (seconds since noon 1/01/2000),
    """

    # constants; time origins
    J2000 = np.datetime64('2000-01-01T12Z', 'ns')
    GPST0 = np.datetime64('1980-01-06T00Z', 'ns')
    MJD0 = np.datetime64('1858-11-17T00Z', 'ns')
    MJD_J2000 = J2000 - MJD0                                    # 51544.5 days
    JD_MJD0 = np.timedelta64(2400000, 'D') + np.timedelta64(12, 'h')

    def __init__(self, timestamp=None, resolution=None):
        """
Generic constructor.

Requires a timestamp.  If not given, it defaults to None ('NaT').  Valid
resolutions are numpy.timedelta64 objects of time units, ie. 'D', 'h', 'm',
's', 'ms', 'us' and 'ns', or the time units themselves.  If the desired
resolution is not given, it is deducted from the timestamp.  If t is 'NaT',
resolution is set to '1 seconds'.
        """
        # core attributes
        self._timestamp = np.datetime64(timestamp)
        self._resolution = np.timedelta64(resolution)
        # more attributes
        self._unit = None
        self._as_string = None
        self._date = None
        self._time = None
        self._year = None
        self._month = None
        self._day = None
        self._is_leap = None
        self._days_of_year = None
        self._seconds_of_day = None
        self._fraction_of_seconds = None
        self._YD = [None, None, None]
        self._GPST = [None, None]
        self._J2000 = [None, None]
        self._JD = None
        self._MJD = None

        # set default resolution
        # self.time_unit = 's'
        # self.resolution = np.timedelta64(1, self.time_unit)
        # # set datetime
        # try:
        #     self.t = np.datetime64(timestamp)
        #     self._set_resolution(resolution)
        # except ValueError:
        #     # timestamp is invalid
        #     self.t = np.datetime64(None)

    def _set_resolution(self, resolution):
        """Set the resolution of the time object."""
        # set the appropriate attributes
        try:
            if type(resolution) is str:
                self.time_unit = resolution
                self.resolution = np.timedelta64(1, self.time_unit)
            elif type(resolution) is np.timedelta64:
                self.resolution = resolution
                self.time_unit = np.datetime_data(self.resolution)[0]
        except TypeError:
            self.time_unit = np.datetime_data(self.t)[0]
            self.resolution = np.timedelta64(1, self.time_unit)
        # fix the time at the given resolution
        self.t = np.datetime64(self.t, self.time_unit)

    def _round_time(self, round_to=np.timedelta64(1, 's')):
        """
Round to any time unit.

Adapted function 'roundTime' (Thierry Husson, 2012 and Stijn Nevens, 2014),
found on StackOverflow (SO), to work with numpy.datetime64 objects.
'round_to': numpy.timedelta64 object; we round to a multiple of this.
        """
        round_to /= np.timedelta64(1, 's')
        seconds = self._seconds_of_day() / np.timedelta64(1, 's')
        # // is a floor division, not a comment on following line:
        rounding = (seconds + round_to / 2) // round_to * round_to
        return self.t + self._seconds_of_day() - self._time() + \
            np.timedelta64(np.int(rounding - seconds), 's')
        # numpy.int64 is not working!
        #     np.timedelta64(np.int64(rounding - seconds), 's')

    @property
    def timestamp(self):
        """Return the timetamp."""
        return self._timestamp

    @property
    def resolution(self):
        """Return the resolution."""
        return self._resolution

    @property
    def unit(self):
        """Return the time unit."""
        return self._unit

    @property
    def as_string(self):
        """Return a string representation of the time object."""
        if not self._as_string:
            self._as_string = np.datetime_as_string(self.timestamp)
        return self._as_string

    @property
    def date(self):
        """Extract the date part."""
        if not self._date:
            self._date = np.datetime64(self.timestamp, 'D')
        return self._date

    @property
    def time(self):
        """Extract the time part."""
        if not self._time:
            self._time = self.timestamp - self.date
        return self._time

    @property
    def year(self):
        """Return the year."""
        if not self._year:
            self._year = np.int64(self.as_string[:4])
        return self._year

    @property
    def is_leap(self):
        """
Check for leap year.

The criterion is 'divisible by 4 and, either not divisible by 100 or divisible
by 400.
        """
        if not self._is_leap:
            self._is_leap = False
            d4 = np.fmod(self.year, 4)
            d100 = np.fmod(self.year, 100)
            d400 = np.fmod(self.year, 400)
            if not d4 and (d100 or not d400):
                self._is_leap = True
        return self._is_leap

    @property
    def days_of_year(self):
        """Return the count of days within the year."""
        if not self._days_of_year:
            self._days_of_year = self.date - \
                np.datetime64(self.timestamp, 'Y') + np.timedelta64(1, 'D')
        return self._days_of_year

    @property
    def seconds_of_day(self):
        """Return the count of seconds within the day."""
        if not self._seconds_of_day:
            self._seconds_of_day = np.timedelta64(self.time, 's')
        return self._seconds_of_day

    @property
    def fraction_of_seconds(self):
        """Return the fraction of seconds."""
        if not self._fraction_of_seconds:
            self._fraction_of_seconds = self.time - self.seconds_of_day
        return self._fraction_of_seconds

    @property
    def GPST(self):
        """Return (GPS week #, seconds of week and fraction of seconds)."""
        delta = self.timestamp - self.GPST0
        weeks = np.timedelta64(delta, 'W')
        seconds = np.timedelta64(delta - weeks, 's')
        decimal = np.float64(0.)
        if self.resolution < np.timedelta64(1, 's'):
            fraction = self._fraction_of_seconds()
            ms = np.timedelta64(fraction, 'ms')
            decimal += ms / np.timedelta64(1, 'ms') * 1e-3
            decimals = 3
            if self.resolution < np.timedelta64(1, 'ms'):
                us = np.timedelta64(fraction - ms, 'us')
                decimal += us / np.timedelta64(1, 'us') * 1e-6
                decimals = 6
                if self.resolution < np.timedelta64(1, 'us'):
                    ns = np.timedelta64(fraction - ms - us, 'ns')
                    decimal += ns / np.timedelta64(1, 'ns') * 1e-9
                    decimals = 9
        # return np.int64(weeks / np.timedelta64(1, 'W')), \
        #     np.int64(seconds / np.timedelta64(1, 's')) + \
        #     np.round(decimal, decimals=decimals)
        return np.int64(weeks / np.timedelta64(1, 'W')), \
            np.around(seconds / np.timedelta64(1, 's') + decimal,
                      decimals=decimals)

    def to_fYear(self):
        """Return fractional year, with '1 days' resolution."""
        return np.int64(self._as_string()[:4]) + \
            np.round(np.int64(self._days_of_year() / np.timedelta64(1, 'D')) /
                     (365. + self.is_leap()), decimals=8)

    def to_YD(self):
        """Return (year, day of year, seconds of day)."""
        return (self._year, self._days_of_year(), self._seconds_of_day() +
                self._nanosecond / 1e9)

    @property
    def J2000(self):
        """Return (seconds since J2000, fraction of seconds)."""
        delta = self.t - self.J2000
        seconds = np.timedelta64(delta, 's')
        fraction = np.timedelta64(delta - seconds, self.resolution)
        return seconds, fraction

    def to_MJD(self):
        """Return MJD."""
        return (self.MJD_J2000 + (self.t - self.J2000)) / \
            np.timedelta64(1, 'D')

    def to_JD(self):
        """Return JD."""
        return self.JD_MJD0 + self.to_MJD()

    def to_ISO(self):
        """Return string ISO format."""
        return self._as_string


class GeoTime(CoreGeoTime):
    def __init__(self):
        # set default resolution
        self.time_unit = 's'
        self.resolution = np.timedelta64(1, self.time_unit)
        # set datetime
        try:
            self.t = np.datetime64(timestamp)
            self._set_resolution(resolution)
        except ValueError:
            # timestamp is invalid
            self.t = np.datetime64(None)


class GPST(CoreGeoTime):
    """Inherits from class GeoTime.  Input is (GPS week, seconds of week)."""

    def __init__(self, w, s):
        super(self, GPST).__init__()
        ns, s = np.modf(s)
        self.t = self.GPST0 + np.timedelta64(w, 'W') + \
            np.timedelta64(np.int64(s), 's') + \
            np.timedelta64(np.int64(ns * 1e9), 'ns')
        self._assign_values()


class fYear(CoreGeoTime):
    """Inherits from class GeoTime.  Input is fractional year."""

    def __init__(self, fy):
        d, y = np.modf(fy)
        y = '{}-01-01T00:00:00.0Z'.format(np.int64(y))
        self.t = np.datetime64(y, 'ns')
        self._assign_values()
        print('fYear:', d, type(d))
        d = d * (365. + self.is_leap())
        print('fYear:', d)
        s, d = np.modf(d)
        print('fYear:', s, d)
        ns, s = np.modf(s * 86400.)
        self.t += np.timedelta64(np.int64(d), 'D') + \
            np.timedelta64(np.int64(s), 's') + \
            np.timedelta64(np.int64(ns * 1e9), 'ns')
        self._assign_values()
