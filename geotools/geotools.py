#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: geotools.py
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
Main code for geotools

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import logging

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
