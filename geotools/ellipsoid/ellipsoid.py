#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: ellipsoid.py
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
Main code for geotools.ellipsoid

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging

import numpy


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
LOGGER_BASENAME = '''ellipsoid'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


ELLIPSOIDS = {'WGS84': (6378137., 298.257223563),
              'PZ90': (6378136., 298.257839303),
              'GRS80': (6378137., 298.257222101),
              'Bessel': (6377397.155, 299.1528128),
              'Hayford': (6378388., 297.),              # International 1924
              'WGS72': (6378135., 298.26),
              'sphere': (6370997., 0.)}


class CoreEllipsoid(object):
    """Defines the ellipsoid parameters."""

    # def __init__(self, name, major_semiaxis, flattening):
    def __init__(self, major_semiaxis, flattening):
        """Default constructor."""
        # basic parameters
        # self._name = name
        self._major_semiaxis = numpy.float64(major_semiaxis)
        self._inverse_flattening = numpy.float64(flattening)
        # rest of the parameters
        self._flattening = None
        self._minor_semiaxis = None
        self._first_eccentricity_squared = None
        self._second_eccentricity_squared = None

    # @property
    # def name(self):
    #     """Return the name."""
    #     return self._name

    @property
    def major_semiaxis(self):
        """Return the major semiaxis."""
        return self._major_semiaxis

    @property
    def flattening(self):
        """Return the flattening."""
        if not self._flattening:
            try:
                self._flattening = 1. / self._inverse_flattening
            except ZeroDivisionError:
                self._flattening = numpy.float64(0)
        return self._flattening

    @property
    def minor_semiaxis(self):
        """Return the minor semiaxis."""
        if not self._minor_semiaxis:
            self._minor_semiaxis = self.major_semiaxis * (1. - self.flattening)
        return self._minor_semiaxis

    @property
    def first_eccentricity_squared(self):
        """Return the first eccentricity squared."""
        if not self._first_eccentricity_squared:
            self._first_eccentricity_squared = 2. * self.flattening - \
                self.flattening ** 2
        return self._first_eccentricity_squared

    @property
    def second_eccentricity_squared(self):
        """Return the second eccentricity squared."""
        if not self._second_eccentricity_squared:
            self._second_eccentricity_squared = \
                self.first_eccentricity_squared / \
                (1. - self.first_eccentricity_squared)
        return self._second_eccentricity_squared


class Ellipsoid(object):
    """Factory for ellipsoids."""

    def __new__(cls, name=None):
        default = ELLIPSOIDS.get('WGS84')
        major_semiaxis, flattening = ELLIPSOIDS.get(name, default)
        return CoreEllipsoid(major_semiaxis, flattening)
