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

import os
import gc
import threading
import yaml
from pathlib import Path
from gi.repository import Adw
from gi.repository import Gtk, Gio, GLib
from moviepy import VideoFileClip
from .logger import GTKProgressLogger

@Gtk.Template(resource_path='/io/github/PinkAvocadoDev/Animated/window.ui')
class AnimatedWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'AnimatedWindow'

    label = Gtk.Template.Child()

    toast_overlay = Gtk.Template.Child("toast_overlay")

    button_select = Gtk.Template.Child()
    button_go = Gtk.Template.Child()
    height_input = Gtk.Template.Child()
    fps_input = Gtk.Template.Child()
    duration = Gtk.Template.Child()

    terminal_output = Gtk.Template.Child()

    f_name=''
    filepath=None


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.button_select.connect("clicked", lambda *_: self.open_file())
        self.button_go.connect("clicked", lambda *_: self.do_conversion())

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

        self.filepath = file.get_path()

        if self.filepath and self.filepath.lower().endswith(".mp4"):
            self.f_name = file.get_basename()
            source_path = Path(self.filepath)
            self.label.set_label(self.f_name)
        else:
            self.show_toast('Please select a valid .mp4 file')

    def do_conversion(self):
        if not self.f_name:
            self.show_toast("Select a video first")
            return -1

        full_filename = self.path_to_disk()

        def run_task():
            try:
                custom_logger = GTKProgressLogger(self.update_progress_ui)

                clip = VideoFileClip(str(self.filepath)).subclipped(0, self.duration.get_value()).resized(height=self.height_input.get_value())
                clip.write_gif(full_filename, fps=self.fps_input.get_value(), logger=custom_logger)

                clip.close()

                gc.collect()

                GLib.idle_add(self.append_log, f"Done! Saved to: {full_filename}")
                GLib.idle_add(self.show_toast, "GIF generated successfully!")
            except Exception as e:
                GLib.idle_add(self.show_toast, f"{e}")
        threading.Thread(target=run_task, daemon=True).start()


    def path_to_disk(self):
        if self.read_conf() != 'default':
            videos_dir = self.read_conf()
        else:
            videos_dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_VIDEOS)

            # Fallback if GLib returns None for any reason
            if not videos_dir:
                videos_dir = os.path.expanduser("~/Videos")
                if not videos_dir:
                    self.show_toast("Error finding ~/Videos, specify in Preferences")
                    return -1

        output_file = os.path.join(videos_dir, "output.gif")
        return output_file


    def show_toast(self, message):
        toast = Adw.Toast.new(message)
        toast.set_timeout(5)
        self.toast_overlay.add_toast(toast)

    def ui_disable(self):
        self.button_select.set_sensitive(False)
        self.button_go.set_sensitive(False)

    def ui_enable(self):
        self.button_select.set_sensitive(True)
        self.button_go.set_sensitive(True)

    def append_log(self, text):
        buffer = self.terminal_output.get_buffer()
        end_iter = buffer.get_end_iter()
        buffer.insert(end_iter, text + "\n") #gen new line

        mark = buffer.create_mark(None, buffer.get_end_iter(), False) #text cursor
        self.terminal_output.scroll_to_mark(mark, 0.0, True, 0.0, 1.0) #scroll to mark
        return False

    def update_progress_ui(self, current, total, percentage):
        msg = f"Rendering frame {current}/{total} ({percentage:.0f}%)" #.0f rounds the float
        self.append_log(msg)

    def read_conf(self):
        config_path = self.get_config_path()

        if not os.path.exists(config_path):
            default_data = {"path": "default"}

            with open(config_path, "w", encoding="utf-8") as file:
                yaml.dump(default_data, file)

            return default_data["path"]
        else:
            with open(config_path, "r", encoding="utf-8") as file:
                load_path = yaml.safe_load(file)
                if isinstance(load_path, dict):
                    return load_path.get("path", "default")
                return "default"

    def get_config_path(self):
        base_config_dir = GLib.get_user_config_dir()
        app_config_dir = os.path.join(base_config_dir, "Animated")

        # Create the directory if it doesn't exist yet
        os.makedirs(app_config_dir, exist_ok=True)

        return os.path.join(app_config_dir, "config.yaml")


class PreferencesDialog(Adw.PreferencesWindow):

    def __init__(self, parent):
        super().__init__()

        self.set_title("Preferences")
        #self.set_transient_for(parent)
        self.set_default_size(300, 400)
        self.set_resizable(False)

        page = Adw.PreferencesPage()
        self.main_group = Adw.PreferencesGroup(title="General settings")

        self.config_entry_row = Adw.EntryRow()
        self.config_entry_row.set_title("Custom output path (remember to end with /)")

        is_custom_path = Adw.SwitchRow()
        is_custom_path.set_title("Use custom path for Output.gif")
        switch = is_custom_path.get_activatable_widget()
        switch.connect("notify::active", self.on_switch_toggled)

        self.save_config_btn = Adw.ButtonRow()
        self.save_config_btn.set_name("saveConfig")
        self.save_config_btn.set_title("Save Path")
        self.save_config_btn.connect("activated", self.on_click)

        self.main_group.add(is_custom_path)
        page.add(self.main_group)

        is_default = True
        if self.read_conf() != "default":
            is_default = False
            self.config_entry_row.set_text(self.read_conf())

        is_custom_path.set_active(not is_default)
        self.normalize_toggle(is_custom_path.get_active())

        self.add(page)
        #log("PreferencesDialog initialized")

    def normalize_toggle(self, state):
        if state:
            self.main_group.add(self.config_entry_row)
            self.main_group.add(self.save_config_btn)
        else:
            self.set_conf("default")
            self.main_group.remove(self.config_entry_row)
            self.main_group.remove(self.save_config_btn)

    def on_switch_toggled(self, switch, param):
        state = switch.get_active()
        self.normalize_toggle(state)

    def on_click(self, button):
        while GLib.MainContext.default().pending():
            GLib.MainContext.default().iteration(True)
        self.set_conf(self.config_entry_row.get_text())

    def get_config_path(self):
        base_config_dir = GLib.get_user_config_dir()
        app_config_dir = os.path.join(base_config_dir, "Animated")

        # Create the directory if it doesn't exist yet
        os.makedirs(app_config_dir, exist_ok=True)

        return os.path.join(app_config_dir, "config.yaml")

    def read_conf(self):
        config_path = self.get_config_path()

        if not os.path.exists(config_path):
            default_data = {"path": "default"}

            with open(config_path, "w", encoding="utf-8") as file:
                yaml.dump(default_data, file)

            return default_data["path"]
        else:
            with open(config_path, "r", encoding="utf-8") as file:
                load_path = yaml.safe_load(file)
                if isinstance(load_path, dict):
                    return load_path.get("path", "default")
                return "default"

    def set_conf(self, data):
        config_dict = {"path": data}
        with open(self.get_config_path(), "w", encoding="utf-8") as file:
            yaml.dump(config_dict, file, default_flow_style=False)

