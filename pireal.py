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

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (
    QLocale,
    QTranslator,
    QLibraryInfo,
    QT_VERSION_STR
)
from src.core import (
    settings,
    logger
)
log = logger.get_logger(__name__)
DEBUG = log.debug
INFO = log.info


def __get_versions():
    """ Version information for components used by Pireal """

    import platform

    # OS
    if sys.platform.startswith('linux'):
        system, name = platform.uname()[:2]
    else:
        system = platform.uname()[0]
        name = platform.uname()[2]
    # Python version
    python_version = platform.python_version()

    return {
        'python': python_version,
        'os': system,
        'name': name,
        'qt': QT_VERSION_STR  # Qt version
    }


def detect_language(system_lang):
    languages = {'es': 'Spanish'}
    return languages.get(system_lang, None)


if __name__ == "__main__":

    # Create dir
    settings.create_dir()
    info = __get_versions()
    DEBUG("Executing Pireal from source")
    INFO("Python {0} - Qt {1} on {2} {3}".format(
         info['python'], info['qt'], info['os'], info['name']))
    DEBUG("Loading settings...")
    settings.load_settings()

    # Import resources
    from src import resources  # lint:ok

    qapp = QApplication(sys.argv)
    # Stylesheet
    stylesheet = settings.PSettings.THEME
    if stylesheet:
        with open(settings.STYLESHEET) as f:
            style = f.read()
    else:
        style = None
    qapp.setStyleSheet(style)
    # Icon
    qapp.setWindowIcon(QIcon(":img/icon"))
    # System language
    local = QLocale.system().name()

    translator = QTranslator()
    translator.load("qt_" + local, QLibraryInfo.location(
                    QLibraryInfo.TranslationsPath))
    qapp.installTranslator(translator)
    # App language
    ptranslator = QTranslator()
    language = settings.PSettings.LANGUAGE
    if not language:
        language = detect_language(local[:2])
        if language is not None:
            ptranslator.load(os.path.join(settings.LANG_PATH, language + '.qm'))
            qapp.installTranslator(ptranslator)
    # Load services
    from src.gui import central_widget  # lint:ok
    from src.gui.main_window import Pireal
    from src.gui import status_bar  # lint:ok
    from src.gui import container  # lint:ok
    from src.gui import table_widget  # lint:ok
    from src.gui.query_editor import query_widget  # lint:ok
    from src.gui import lateral_widget  # lint:ok

    INFO("Loading GUI...")
    gui = Pireal()
    gui.show()
    gui.showMaximized()
    INFO("Pireal ready!")
    sys.exit(qapp.exec_())
