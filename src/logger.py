# logger.py
#
# Copyright 2026 PinkAvocadoDev
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later


from proglog import ProgressBarLogger
from gi.repository import GLib

class GTKProgressLogger(ProgressBarLogger):
    def __init__(self, update_callback):
        super().__init__()
        self.update_callback = update_callback

    def bars_callback(self, bar, attr, value, old_value=None): #Override bars_callback from proglog
        #@param bar: progress bar
        #@param attr: attribute, what kind of prog bar
        #@param value: where we are in the progress bar
        #@param old_value: previous position in the prog bar

        if attr == 'index': #progress
            total = self.bars[bar].get('total', 0)
            if total > 0:
                percentage = (value / total) * 100
                GLib.idle_add(self.update_callback, value, total, percentage)
