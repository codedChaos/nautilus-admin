# Nautilus Admin - Extension for Nautilus to do administrative operations
# Copyright (C) 2015-2017 Bruno Nova <brunomb.nova@gmail.com>
#               2016 frmdstryr <frmdstryr@gmail.com>
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, subprocess
from typing import Any, List

from gi import require_version
require_version('Gtk', '3.0')
require_version('Nautilus', '3.0')

from gi.repository import Nautilus, GObject, Gdk, Gtk
from gettext import gettext, bindtextdomain, textdomain

try:
	# python 8
	from gettext import locale
except ImportError:
	# python 9
	import locale

ROOT_UID = 0
NAUTILUS_PATH="@NAUTILUS_PATH@"
GEDIT_PATH="@GEDIT_PATH@"


class NautilusAdmin(Nautilus.MenuProvider, GObject.GObject):
	"""Simple Nautilus extension that adds some administrative (root) actions to
	the right-click menu, using GNOME's new admin backend."""
	def __init__(self) -> None:
		pass

	def get_file_items(self, window, files) -> Any:
		"""Returns the menu items to display when one or more files/folders are
		selected."""
		# Don't show when already running as root, or when more than 1 file is selected
		if os.geteuid() == ROOT_UID or len(files) != 1:
			return
		file = files[0]

		# Add the menu items
		items = []
		self._setup_gettext();
		self.window = window
		if file.get_uri_scheme() == "file": # must be a local file/directory
			if file.is_directory():
				if os.path.exists(NAUTILUS_PATH):
					items += [self._create_nautilus_item(file)]
			else:
				if os.path.exists(GEDIT_PATH):
					items += [self._create_gedit_item(file)]

		return items

	def get_background_items(self, window, file) -> List | None:
		"""Returns the menu items to display when no file/folder is selected
		(i.e. when right-clicking the background)."""
		# Don't show when already running as root
		if os.geteuid() == ROOT_UID:
			return

		# Add the menu items
		items = []
		self._setup_gettext();
		self.window = window
		if file.is_directory() and file.get_uri_scheme() == "file":
			if os.path.exists(NAUTILUS_PATH):
				items += [self._create_nautilus_item(file)]

		return items

	def _setup_gettext(self) -> None:
		"""Initializes gettext to localize strings."""
		try: # prevent a possible exception
			locale.setlocale(locale.LC_ALL, "")
		except:
			pass
		bindtextdomain("nautilus-admin", "@CMAKE_INSTALL_PREFIX@/share/locale")
		textdomain("nautilus-admin")

    def _create_nautilus_item(self, file) -> Nautilus.MenuItem:
        item = Nautilus.MenuItem(name="NautilusAdmin::Nautilus",
                                label=gettext("Copy path"),
                                tip=gettext("Copy File path to clipboard"))
        item.connect("activate", self._nautilus_run, file)
        return item

    def _nautilus_run(self, menu, file) -> None:
        """'Copy File path' menu item callback."""
        uri = file.get_uri()
        file_path = uri.replace("file://", "")
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(file_path, -1)
        clipboard.store()

