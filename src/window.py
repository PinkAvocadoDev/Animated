# window.py
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

from gi.repository import Adw
from gi.repository import Gtk, Gio

@Gtk.Template(resource_path='/io/github/PinkAvocadoDev/Animated/window.ui')
class AnimatedWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'AnimatedWindow'

    label = Gtk.Template.Child()

    button_select = Gtk.Template.Child()
    button_go = Gtk.Template.Child()
    width_input = Gtk.Template.Child()
    fps_input = Gtk.Template.Child()

    f_name=''


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.button_select.connect("clicked", lambda *_: self.open_file())

    # File picker methods
    def open_file(self):
        filter_mp4 = Gtk.FileFilter()
        filter_mp4.set_name("MP4 Videos")
        filter_mp4.add_mime_type("video/mp4")
        filter_mp4.add_pattern("*.mp4")

        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_mp4)

        dialog = Gtk.FileDialog(title='Select MP4 Video')
        dialog.set_filters(filters)
        dialog.set_default_filter(filter_mp4)
        dialog.open(self, None, self.on_file_opened)

    # dataload callback
    def on_file_opened(self, file_dialog, result):
        try:
            file = file_dialog.open_finish(result)
        except Exception:
            return

        filepath = file.get_path()

        if filepath and filepath.lower().endswith(".mp4"):
            self.f_name = file.get_basename()
            source_path = Path(filepath)
        else:
            self.show_toast('Please select a valid .mp4 file')


