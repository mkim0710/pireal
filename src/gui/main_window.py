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

""" Pireal Main Window """

from collections import Callable
from PyQt5.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QToolBar
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (
    QFileInfo,
    QSize
)
from src.core import settings
from src import translations as tr


class Pireal(QMainWindow):

    """
    Main Window class

    This class is responsible for installing all application services.
    The services are in a dictionary that can be accessed
    from the class methods.

    """

    __SERVICES = {}
    __ACTIONS = {}

    # The name of items is the connection text
    TOOLBAR_ITEMS = [
        'create_database',
        'save_data_base',
        'new_query',
        '',  # Is a separator!
        'open_file',
        'save_file',
        '',
        'undo_action',
        'redo_action',
        'cut_action',
        'copy_action',
        'paste_action',
        '',
        'create_new_relation',
        'remove_relation',
        #'insert_tuple',
        #'remove_tuple',
        '',
        'execute_queries'
    ]

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle(self.tr("Pireal"))
        self.showMaximized()

        # Toolbar
        self.toolbar = QToolBar(self)
        self.toolbar.setIconSize(QSize(22, 22))
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        # Menu bar
        menubar = self.menuBar()
        self.__load_menubar(menubar)

        # Central widget
        central_widget = self.__load_ui()
        self.setCentralWidget(central_widget)

        # Status bar
        #status_bar = Pireal.get_service("status")
        #status_bar.hide()
        #self.setStatusBar(status_bar)

        # Install service
        Pireal.load_service("pireal", self)

    @classmethod
    def get_service(cls, service):
        """ Return the instance of a loaded service """

        return cls.__SERVICES.get(service, None)

    @classmethod
    def load_service(cls, name, instance):
        """ Load a service providing the service name and the instance """

        cls.__SERVICES[name] = instance

    @classmethod
    def get_action(cls, name):
        """ Return the instance of a loaded QAction """

        return cls.__ACTIONS.get(name, None)

    @classmethod
    def load_action(cls, name, action):
        """ Load a QAction """

        cls.__ACTIONS[name] = action

    def __load_menubar(self, menubar):
        """
        This method installs the menubar and toolbar, menus and QAction's,
        also connects to a slot each QAction.
        """

        from src.gui import menu_actions
        from src import keymap

        # Keymap
        kmap = keymap.KEYMAP
        # Toolbar items
        toolbar_items = {}

        central = Pireal.get_service("central")

        # Settings action on menu bar
        qaction = menubar.addAction(tr.TR_SETTINGS_MENUBAR)
        qaction.triggered.connect(central.show_settings)

        # Load menu bar
        for item in menu_actions.MENU:
            menubar_item = menu_actions.MENU[item]
            menu_name = menubar_item['name']
            items = menubar_item['items']
            menu = menubar.addMenu(menu_name)
            for menu_item in items:
                if isinstance(menu_item, str):
                    # Is a separator
                    menu.addSeparator()
                else:
                    action = menu_item['name']
                    obj, connection = menu_item['slot'].split(':')
                    if obj.startswith('central'):
                        obj = central
                    else:
                        obj = self

                    # Load recent files
                    #if action is None:
                        #files = settings.get_setting('recentFiles', [])
                        #nrfiles = min(len(files),
                                      #settings.PSettings.MAX_RECENT_FILES)
                        #for i in range(nrfiles):
                            #name = QFileInfo(files[i]).fileName()
                            #text = "&%d %s" % (i + 1, name)
                            #qaction = menu.addAction(text)
                            #qaction.setData(files[i])
                            #qaction.triggered.connect(
                                #central.open_recent_database)
                        #continue
                    qaction = menu.addAction(action)
                    # Icon name is connection
                    icon = QIcon(":img/%s" % connection)
                    qaction.setIcon(icon)

                    # Install shortcuts
                    shortcut = kmap.get(connection, None)
                    if shortcut is not None:
                        qaction.setShortcut(shortcut)

                    # Items for toolbar
                    if connection in Pireal.TOOLBAR_ITEMS:
                        toolbar_items[connection] = qaction

                    # The name of QAction is the connection
                    Pireal.load_action(connection, qaction)
                    slot = getattr(obj, connection, None)
                    if isinstance(slot, Callable):
                        qaction.triggered.connect(slot)

        # Install toolbar
        for action in Pireal.TOOLBAR_ITEMS:
            qaction = toolbar_items.get(action, None)
            if qaction is not None:
                self.toolbar.addAction(qaction)
            else:
                self.toolbar.addSeparator()

        self.enable_disable_db_actions(False)
        self.enable_disable_relation_actions(False)
        self.enable_disable_query_actions(False)

    def __load_ui(self):
        central_widget = Pireal.get_service("central")

        if settings.PSettings.SHOW_START_PAGE:
            central_widget.add_start_page()
        #central_widget.load_lateral_widget(lateral)
        #central_widget.load_table_widget(container)
        #central_widget.load_editor_widget(query_widget)

        #container.currentFileSaved['QString'].connect(
            #self.__show_status_message)

        return central_widget

    def __show_status_message(self, msg):
        status = Pireal.get_service("status")
        status.show_message(msg)

    def change_title(self, title):
        self.setWindowTitle("Pireal " + '[' + title + ']')

    def enable_disable_db_actions(self, enable=True):
        """ Public method. Enables or disables db QAction """

        actions = [
            'new_query',
            'save_file',
            #'save_query',
            #'save_query_as',
            #'save_database_as',
            #'close_query',
            #'execute_queries',
            'create_new_relation',
            'remove_relation',
            'close_database',
            'load_relation'
        ]

        for action in actions:
            qaction = Pireal.get_action(action)
            qaction.setEnabled(enable)

    def enable_disable_relation_actions(self, enable=True):
        """ Public method. Enables or disables relation's QAction """

        actions = [
            'insert_tuple',
            'remove_tuple',
        ]

        for action in actions:
            qaction = Pireal.get_action(action)
            qaction.setEnabled(enable)

    def enable_disable_query_actions(self, enable=True):
        """ Public method. Enables or disables queries QAction """

        actions = [
            'undo_action',
            'redo_action',
            'copy_action',
            'cut_action',
            'paste_action',
            'execute_queries'
        ]

        for action in actions:
            qaction = Pireal.get_action(action)
            qaction.setEnabled(enable)

    def show_hide_lateral(self):
        lateral = Pireal.get_service("lateral")
        if lateral.isVisible():
            lateral.hide()
        else:
            lateral.show()

    def about_qt(self):
        """ Show about qt dialog """

        QMessageBox.aboutQt(self)

    def about_pireal(self):
        """ Show the bout Pireal dialog """

        from src.gui.dialogs import about_dialog
        dialog = about_dialog.AboutDialog(self)
        dialog.exec_()

    def show_settings(self):
        from src.gui.dialogs import preferences
        container = Pireal.get_service("container")
        dialog = preferences.Preferences(self)
        container.show_dialog(dialog)

        dialog.valueChanged['QString', 'PyQt_PyObject'].connect(
            self._update_settings)

    def _update_settings(self, key, value):
        pass

    def closeEvent(self, event):
        pass
        #main_container = Pireal.get_service("main")
        #last_open_folder = main_container.get_last_open_folder()
        #settings.set_setting("last_open_folder", last_open_folder)
        #container = Pireal.get_service("container")
        #if not container.check_opened_query_files():
            #event.ignore()
        #if container.modified:
            #db_name = container.get_db_name()
            #flags = QMessageBox.Yes
            #flags |= QMessageBox.No
            #flags |= QMessageBox.Cancel

            #result = QMessageBox.question(self,
                                          #tr.TR_CONTAINER_DB_UNSAVED_TITLE,
                                          #tr.TR_CONTAINER_DB_UNSAVED.format(
                                              #db_name), flags)
            #if result == QMessageBox.Cancel:
                #event.ignore()
            #if result == QMessageBox.Yes:
                #container.save_data_base()
