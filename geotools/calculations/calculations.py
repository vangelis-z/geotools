#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: calculations.py
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
Main code for geotools.calculations

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging

import numpy

from geotools.ellipsoid import Ellipsoid


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


class Point():
    '''Defines points.'''

    def __init__(self, coordinates=(0., 0., 0.), is_geodetic=True,
                 ellipsoid=Ellipsoid('WGS84')):
        '''Default constructor.'''
        self.ellipsoid = ellipsoid
        if not is_geodetic:
            self.geodetic(coordinates)
        else:
            self.latitude = coordinates[0]
            self.longitude = coordinates[1]
            self.height = coordinates[2]

    # radii
    def meridian_radius(self):
        '''Return the radius of the meridian section.'''
        a = self.ellipsoid.a
        e12 = self.ellipsoid.e12
        return a * (1. - e12) / \
            numpy.sqrt(numpy.power(1. - e12 *
                                   numpy.power(numpy.sin(self.latitude), 2),
                                   3))

    def prime_vertical_section_radius(self):
        '''Return the radius of the prime vertical section.'''
        a = self.ellipsoid.a
        e12 = self.ellipsoid.e12
        return a / numpy.sqrt(1. - e12 * numpy.power(numpy.sin(self.latitude),
                                                     2))

    def Gauss_radius(self):
        '''Return the radius of the Gauss' sphere.'''
        return numpy.sqrt(self.meridian_radius() *
                          self.prime_vertical_section_radius())

    def parallel_radius(self):
        '''Return the radius of the parallel circle'''
        return self.prime_vertical_section_radius() * numpy.cos(self.latitude)

    def vertical_section_radius(self, azimuth=0.):
        '''Return the radius of the vertical section at that azimuth.'''
        mr = self.meridian_radius()
        pvsr = self.prime_vertical_section_radius()
        return mr * pvsr / (pvsr * numpy.power(numpy.cos(azimuth), 2) +
                            mr * numpy.power(numpy.sin(azimuth), 2))

    # compute arc length
    def meridian_arc(self):
        '''Return the length of the meridian arc from the equator.'''
        a = self.ellipsoid.a
        e12 = self.ellipsoid.e12
        # Μ coefficients
        M = numpy.zeros((9,))
        M[0] = 1. + (3. / 4. + (45. / 64. + (175. / 256. + 11025. / 16384. *
                                             e12) * e12) * e12) * e12
        M[2] = -(3. / 4. + (15. / 16. + (525. / 512. + 2205. / 2048. * e12) *
                            e12) * e12) * e12 / 2.
        M[4] = (15. / 64. + (105. / 256. + (2205. / 4096. * e12)) *
                e12) * e12 * e12 / 4.
        M[6] = -(35. / 512. + (315. / 2048. * e12)) * e12 * e12 * e12 / 6.
        M[8] = 315. / 16384. * e12 * e12 * e12 * e12 / 8.
        # sine factors
        s = numpy.array([numpy.sin(i * self.latitude)
                         for i in numpy.arange(9)])
        s[0] = self.latitude
        return a * (1. - e12) * numpy.dot(M, s)

    # compute cartesian coordinates
    def cartesian(self):
        '''Return the cartesian coordinates.'''
        e12 = self.ellipsoid.e12
        pvsr = self.prime_vertical_section_radius()
        p2 = (pvsr + self.height) * numpy.cos(self.latitude)
        x = p2 * numpy.cos(self.longitude)
        y = p2 * numpy.sin(self.longitude)
        z = (pvsr * (1. - e12) + self.height) * numpy.sin(self.latitude)
        return x, y, z

    # compute geodetic coordinates
    def geodetic(self, coordinates):
        '''Compute geodetic coordinates.'''
        a = self.ellipsoid.a
        f = self.ellipsoid.f
        b = self.ellipsoid.b
        e12 = self.ellipsoid.e12
        e22 = self.ellipsoid.e22

        x, y, z = coordinates
        p = numpy.sqrt(x * x + y * y)
        reduced = numpy.arctan2(z, (1. - f) * p)
        self.latitude = numpy.arctan2(z + e22 * b *
                                      numpy.power(numpy.sin(reduced), 3),
                                      p - a * e12 *
                                      numpy.power(numpy.cos(reduced), 3))
        self.longitude = numpy.arctan2(y, x)
        self.height = p / numpy.cos(self.latitude) - \
            self.prime_vertical_section_radius()
        return 0
