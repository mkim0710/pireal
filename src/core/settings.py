# -*- coding: utf-8 -*-
#
# Copyright 2015 - Gabriel Acosta <acostadariogabriel@gmail.com>
#
# This file is part of Pireal.
#
# Pireal is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# Pireal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pireal; If not, see <http://www.gnu.org/licenses/>.

"""
Pireal settings
"""

import sys
import os
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QSettings


# Operating System
LINUX, WINDOWS = False, False
if sys.platform.startswith('linux'):
    LINUX = True
else:
    WINDOWS = True


# Supported files
SUPPORTED_FILES = ("Pireal Database File (*.pdb);;Pireal Query File (*.pqf);;"
                   "Pireal Relation File (*.prf)")

# Paths used by Pireal
# Create folder (settings and logging)
if getattr(sys, 'frozen', ''):
    PATH = os.path.realpath(os.path.dirname(sys.argv[0]))
else:
    PATH = os.path.join(os.path.realpath(
        os.path.dirname(__file__)), "..", "..")
HOME = os.path.expanduser("~")
PIREAL_DIR = os.path.join(HOME, ".pireal")
PIREAL_PROJECTS = os.path.join(HOME, "PirealDatabases")
LOG_FILE_PATH = os.path.join(PIREAL_DIR, "pireal_log.log")
SETTINGS_PATH = os.path.join(PIREAL_DIR, "pireal_settings.ini")
LANG_PATH = os.path.join(PATH, "src", "lang")
QML_FILES = os.path.join(PATH, "src", "gui", "qml")


class PSettings:
    SHOW_START_PAGE = True
    CHECK_UPDATES = True
    MAX_RECENT_FILES = 5
    LANGUAGE = ""
    THEME = "Fusion"  # Default style
    LAST_OPEN_FOLDER = ""
    CONSOLE = False  # For dev
    RECENT_DB = []
    HIGHLIGHT_CURRENT_LINE = False
    MATCHING_PARENTHESIS = False
    if LINUX:
        FONT = QFont("Monospace", 12)
    else:
        FONT = QFont("Courier", 10)


def create_dir():
    for path in (PIREAL_DIR, PIREAL_PROJECTS):
        if not os.path.isdir(path):
            os.mkdir(path)


def get_setting(key, default):
    psettings = QSettings(SETTINGS_PATH, QSettings.IniFormat)
    return psettings.value(key, default)


def set_setting(key, value):
    psettings = QSettings(SETTINGS_PATH, QSettings.IniFormat)
    psettings.setValue(key, value)


def load_settings():
    """ Load settings from .ini file """

    settings = QSettings(SETTINGS_PATH, QSettings.IniFormat)
    PSettings.SHOW_START_PAGE = settings.value('show-start-page',
                                               True, type=bool)
    PSettings.LANGUAGE = settings.value('language', "", type='QString')
    PSettings.THEME = settings.value('theme', "Fusion", type='QString')
    PSettings.LAST_OPEN_FOLDER = settings.value("last_open_folder", "",
                                                type='QString')
    PSettings.RECENT_DB = settings.value("recentDB", [])
    PSettings.HIGHLIGHT_CURRENT_LINE = settings.value("highlight_current_line",
                                                      False, type=bool)
    PSettings.MATCHING_PARENTHESIS = settings.value("matching_parenthesis",
                                                    False, type=bool)
    font = settings.value("font", None)
    if font is not None:
        PSettings.FONT = font
