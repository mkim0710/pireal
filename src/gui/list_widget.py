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

from PyQt5.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QMenu,
    QAbstractItemView,
    #QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import (
    Qt,
    pyqtSignal
)
from src.gui.main_window import Pireal
from src import translations as tr


class LateralWidget(QListWidget):

    itemRemoved = pyqtSignal(int)
    showEditRelation = pyqtSignal('QModelIndex')

    def __init__(self):
        super(LateralWidget, self).__init__()
        # Multiple selection
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        # Connections
        self.customContextMenuRequested['const QPoint'].connect(
            self.__show_context_menu)

    def __show_context_menu(self, point):
        """ Context menu """

        menu = QMenu()
        edit_action = menu.addAction(tr.TR_MENU_RELATION_EDIT_RELATION)
        remove_action = menu.addAction(QIcon(":img/remove-rel"),
                                        tr.TR_MENU_RELATION_DELETE_RELATION)

        remove_action.triggered.connect(self._remove)
        edit_action.triggered.connect(self._edit)

        menu.exec_(self.mapToGlobal(point))

    def current_text(self):
        return self.currentItem().text()

    def _edit(self):
        item = self.currentItem()
        index = self.indexFromItem(item)
        self.showEditRelation.emit(index)

    def add_item(self, text):
        item = QListWidgetItem(text)
        item.setTextAlignment(Qt.AlignHCenter)
        self.addItem(item)

    def text_item(self, index):
        return self.item(index).text().split()[0]

    def _remove(self):
        central = Pireal.get_service("central")
        central.remove_relation()

    def clear_items(self):
        """ Remove all items and selections in the view """

        self.clear()