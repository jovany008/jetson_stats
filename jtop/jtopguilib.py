# -*- coding: UTF-8 -*-
# Copyright (C) 2019, Raffaello Bonghi <raffaello@rnext.it>
# All rights reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# control command line
import curses
# System
import os
from math import ceil
# Functions and decorators
from functools import wraps


def check_curses(func):
    """ Check curses write """
    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except curses.error:
            pass
    return wrapped


@check_curses
def draw_chart(stdscr, size_x, size_y, value, line="*"):
    # Get Max value and unit from value to draw
    max_val = 100 if "max_val" not in value else value["max_val"]
    unit = "%" if "max_val" not in value else value["unit"]
    # Evaluate Diplay X, and Y size
    displayX = size_x[1] - size_x[0] + 1
    displayY = size_y[1] - size_y[0] - 1
    val = float(displayX - 2) / float(len(value["idle"]))
    points = []
    for n in value["idle"]:
        points += [n] * int(ceil(val))
    # Plot chart shape and labels
    for point in range(displayY):
        value = max_val / float(displayY - 1) * float(displayY - point - 1)
        stdscr.addstr(1 + size_y[0] + point, size_x[1], "-")
        stdscr.addstr(1 + size_y[0] + point, size_x[1] + 2,
                      "{value:3d}{unit}".format(value=int(value), unit=unit),
                      curses.A_BOLD)
    for point in range(displayX):
        stdscr.addstr(size_y[1], size_x[0] + point, "-")
    # Plot values
    delta = displayX - len(points)
    for idx, point in enumerate(points):
        if delta + idx >= size_x[0]:
            x_val = (delta + idx + 1)
        else:
            x_val = -1
        y_val = size_y[1] - 1 - ((float(displayY - 1) / max_val) * point)
        stdscr.addstr(int(y_val), x_val, line, curses.color_pair(2))
    # Debug value
    # stdscr.addstr( 5, 5, "{}".format(delta), curses.color_pair(1))


def make_gauge_from_percent(data):
    gauge = {'name': data['name']}
    if data["status"] != "OFF":
        gauge['value'] = int(data['idle'][-1])
    if data["status"] == "ON":
        freq = data['frequency'][-1]
        if freq >= 1000:
            gauge['label'] = "{0:2.1f}GHz".format(freq / 1000.0)
        else:
            gauge['label'] = str(int(freq)) + "MHz"
    return gauge


@check_curses
def linear_percent_gauge(stdscr, gauge, max_bar, offset=0, start=0, type_bar="|", color_name=6):
    # Evaluate size withuout short name
    size_bar = max_bar - 8
    if 'value' in gauge:
        value = gauge['value']
        # Show short name linear gauge
        stdscr.addstr(offset, start + 0, ("{short_name:4}").format(short_name=gauge['name']), curses.color_pair(color_name))
        # Show bracket linear gauge and label and evaluate size withuout size labels and short name
        size_bar -= (len(gauge['label']) + 1) if 'label' in gauge else 0
        stdscr.addstr(offset, start + 5, "[" + " " * size_bar + "]", curses.A_BOLD)
        if 'label' in gauge:
            stdscr.addstr(offset, start + 5 + size_bar + 3, gauge['label'])
        # Show progress value linear gauge
        n_bar = int(float(value) * float(size_bar) / 100.0)
        progress_bar = type_bar * n_bar
        # Build progress barr string
        str_progress_bar = ("{n_bar:" + str(size_bar) + "}").format(n_bar=progress_bar)
        percent_label = gauge['percent'] if 'percent' in gauge else str(value) + "%"
        str_progress_bar = str_progress_bar[:size_bar - len(percent_label)] + percent_label
        # Split string in green and grey part
        green_part = str_progress_bar[:n_bar]
        grey_part = str_progress_bar[n_bar:]
        stdscr.addstr(offset, start + 6, green_part, curses.color_pair(2))
        stdscr.addstr(offset, start + 6 + size_bar - len(grey_part), grey_part, curses.A_DIM)
    else:
        # Show short name linear gauge
        stdscr.addstr(offset, start + 0, ("{short_name:4}").format(short_name=gauge['name']), curses.color_pair(color_name))
        # Show bracket linear gauge and label
        stdscr.addstr(offset, start + 5, ("[{value:>" + str(size_bar) + "}]").format(value=" "))
        # Show bracket linear gauge and label
        stdscr.addstr(offset, start + 7, "OFF", curses.color_pair(1))


@check_curses
def plot_dictionary(stdscr, offset, data, name, start=0):
    # Plot title
    stdscr.addstr(offset, start, name + ":", curses.A_BOLD)
    counter = 1
    for key, value in data.items():
        if 'text' in value:
            stdscr.addstr(offset + counter, start, " {0:<10} {1}".format(key, value['text']))
        else:
            stdscr.addstr(offset + counter, start, " {0:<10} {1}".format(key, value))
        counter += 1


@check_curses
def plot_name_info(stdscr, offset, start, name, value):
    stdscr.addstr(offset, start, name + ":", curses.A_BOLD)
    stdscr.addstr(offset, start + len(name) + 2, value)
# EOF
