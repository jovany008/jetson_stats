# -*- coding: UTF-8 -*-
# This file is part of the jetson_stats package (https://github.com/rbonghi/jetson_stats or http://rnext.it).
# Copyright (c) 2019 Raffaello Bonghi.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import re

REGEXP = re.compile(r'(.+?): ((.*))')

class cpuinfo():
    """
    Find in cpuinfo information about the board
    """
    @staticmethod
    def load():
        cpus = [{}]
        counter = 0
        with open("/proc/cpuinfo", "r") as fp:
            for line in fp:
                # Search line
                match = REGEXP.search(line)
                if match:
                    key = match.group(1).rstrip()
                    value = match.group(2).rstrip()
                    # Load cpu info
                    cpus[counter][key] = value
                else:
                    counter += 1
                    cpus += [{}]
        # If empty remove the last one in list
        if not cpus[-1]:
            del cpus[-1]
        return cpus

    @staticmethod
    def models():
        # Load cpuinfo
        cpus = cpuinfo.load()
        models = {}
        # Find all models
        for cpu in cpus:
            model = cpu.get("model name", "")
            if model not in models:
                models[model] = 1
            else:
                models[model] += 1
        return models
# EOF