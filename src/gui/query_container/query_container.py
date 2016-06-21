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

import re

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QStackedWidget,
    QMessageBox,
    QDialog,
    QPushButton,
    QAction
)
from PyQt5.QtGui import QStandardItem
from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QSettings
)

from src.core.logger import PirealLogger
from src.core.interpreter import (
    scanner,
    lexer,
    parser
)
from src.gui import (
    custom_table,
    lateral_widget,
    fader_widget
)
from src.gui.main_window import Pireal
from src.gui.query_container import (
    editor,
    tab_widget
)
from src.core import settings

# Logger
logger = PirealLogger(__name__)
DEBUG = logger.debug
ERROR = logger.error


class QueryContainer(QWidget):
    saveEditor = pyqtSignal('PyQt_PyObject')

    def __init__(self):
        super(QueryContainer, self).__init__()
        box = QVBoxLayout(self)
        box.setContentsMargins(0, 0, 0, 0)

        # Regex for validate variable name
        self.__validName = re.compile(r'^[a-z_]\w*$')

        self.__nquery = 1

        # Tab
        self._tabs = tab_widget.TabWidget()
        box.addWidget(self._tabs)

        self.relations = {}

        self.__hide()

        # Connections
        self._tabs.tabCloseRequested.connect(self.__hide)
        self._tabs.saveEditor['PyQt_PyObject'].connect(
            self.__on_save_editor)

    def set_focus_editor_tab(self, index):
        self._tabs.setCurrentIndex(index)

    def current_index(self):
        """ This property holds the index position of the current tab page """

        return self._tabs.currentIndex()

    def tab_text(self, index):
        """
        Returns the label text for the tab on the page at position index
        """

        return self._tabs.tabText(index)

    def __hide(self):
        if self.count() == 0:
            self.hide()
            # Disable query actions
            pireal = Pireal.get_service("pireal")
            pireal.set_enabled_query_actions(False)
            pireal.set_enabled_editor_actions(False)

    def _add_operator_to_editor(self):
        data = self.sender().data()
        widget = self._tabs.currentWidget()
        tc = widget.get_editor().textCursor()
        tc.insertText(data + ' ')

    def get_unsaved_queries(self):
        weditors = []
        for index in range(self.count()):
            weditor = self._tabs.widget(index).get_editor()
            if weditor.modified:
                weditors.append(weditor)
        return weditors

    def count(self):
        return self._tabs.count()

    def add_tab(self, widget, title):
        if not self.isVisible():
            self.show()

        index = self._tabs.addTab(widget, title)
        # Focus editor
        weditor = widget.get_editor()
        weditor.setFocus()
        self._tabs.setCurrentIndex(index)
        self._tabs.setTabToolTip(index, weditor.filename)

        widget.editorModified[bool].connect(
            lambda value: self._tabs.tab_modified(self.sender(), value))

        return widget

    def is_open(self, id_):
        for index in range(self._tabs.count()):
            weditor = self._tabs.widget(index).get_editor()
            if weditor.filename == id_:
                return index
        return -1

    def currentWidget(self):
        return self._tabs.currentWidget()

    def __on_save_editor(self, editor):
        self.saveEditor.emit(editor)

    def execute_queries(self, query=''):
        if not query:
            # Get the text from editor
            weditor = self.currentWidget().get_editor()
            text = weditor.toPlainText()
            query = text

        relations = self.currentWidget().relations
        central = Pireal.get_service("central")
        table_widget = central.get_active_db().table_widget

        # Restore
        relations.clear()
        self.currentWidget().clear_results()

        for i in query.split(';'):
            if i:
                p = i.split(':=', 1)
                if len(p) == 2 and self.__validName.match(p[0].strip()):
                    relation_name = p[0].strip()
                    q = p[1].strip() + ';'
                else:
                    relation_name = "query_{}".format(self.__nquery)
                    self.__nquery += 1
                try:
                    # Parse
                    sc = scanner.Scanner(q)
                    lex = lexer.Lexer(sc)
                    par = parser.Parser(lex)
                    interprete = parser.Interpreter(par)
                    expression = interprete.to_python()
                    relations.update(table_widget.relations)
                    rela = eval(expression, {}, relations)
                    print(rela)
                except Exception as reason:
                    QMessageBox.critical(self,
                                         self.tr("Query Error"),
                                         reason.__str__())
                    return

                if relation_name in relations:
                    QMessageBox.critical(self,
                                         self.tr("Query Error"),
                                         self.tr("<b>{}</b> is a duplicate "
                                                 "relation name.<br><br> "
                                                 "Please choose a unique name "
                                                 "and re-execute the "
                                                 "queries.".format(
                                                     relation_name)))
                    return

                relations[relation_name] = rela
                self.__add_table(rela, relation_name)

    def __add_table(self, rela, rname):
        self.currentWidget().add_table(rela, rname)

    def undo(self):
        weditor = self.currentWidget().get_editor()
        if weditor.hasFocus():
            weditor.undo()

    def redo(self):
        weditor = self.currentWidget().get_editor()
        if weditor.hasFocus():
            weditor.redo()

    def cut(self):
        weditor = self.currentWidget().get_editor()
        if weditor.hasFocus():
            weditor.cut()

    def copy(self):
        weditor = self.currentWidget().get_editor()
        if weditor.hasFocus():
            weditor.copy()

    def paste(self):
        weditor = self.currentWidget().get_editor()
        if weditor.hasFocus():
            weditor.paste()

    def zoom_in(self):
        weditor = self.currentWidget().get_editor()
        if weditor.hasFocus():
            weditor.zoom_in()

    def zoom_out(self):
        weditor = self.currentWidget().get_editor()
        if weditor.hasFocus():
            weditor.zoom_out()


class QueryWidget(QWidget):
    editorModified = pyqtSignal(bool)

    def __init__(self):
        super(QueryWidget, self).__init__()
        box = QVBoxLayout(self)
        box.setContentsMargins(0, 0, 0, 0)

        self._vsplitter = QSplitter(Qt.Vertical)
        self._hsplitter = QSplitter(Qt.Horizontal)

        self._result_list = lateral_widget.LateralWidget()
        self._result_list.header().hide()
        self._hsplitter.addWidget(self._result_list)

        self._stack_tables = StackedWidget()
        self._hsplitter.addWidget(self._stack_tables)

        self.relations = {}

        self._query_editor = editor.Editor()
        # Editor connections
        self._query_editor.customContextMenuRequested.connect(
            self.__show_context_menu)
        self._query_editor.modificationChanged[bool].connect(
            self.__editor_modified)
        self._query_editor.undoAvailable[bool].connect(
            self.__on_undo_available)
        self._query_editor.redoAvailable[bool].connect(
            self.__on_redo_available)
        self._query_editor.copyAvailable[bool].connect(
            self.__on_copy_available)
        self._vsplitter.addWidget(self._query_editor)

        self._vsplitter.addWidget(self._hsplitter)
        box.addWidget(self._vsplitter)

        # Connections
        self._result_list.itemClicked.connect(
            lambda index: self._stack_tables.show_display(
                self._result_list.row()))
        self._result_list.itemDoubleClicked.connect(
            self.show_relation)

    def __show_context_menu(self, point):
        popup_menu = self._query_editor.createStandardContextMenu()

        undock_editor = QAction(self.tr("Undock"), self)
        popup_menu.insertAction(popup_menu.actions()[0],
                                undock_editor)
        popup_menu.insertSeparator(popup_menu.actions()[1])
        undock_editor.triggered.connect(self.__undock_editor)

        popup_menu.exec_(self.mapToGlobal(point))

    def __undock_editor(self):
        new_editor = editor.Editor()
        actual_doc = self._query_editor.document()
        new_editor.setDocument(actual_doc)
        new_editor.resize(900, 400)
        # Set text cursor
        tc = self._query_editor.textCursor()
        new_editor.setTextCursor(tc)
        # Set title
        db = Pireal.get_service("central").get_active_db()
        qc = db.query_container
        new_editor.setWindowTitle(qc.tab_text(qc.current_index()))
        new_editor.show()

    def __on_undo_available(self, value):
        """ Change state of undo action """

        pireal = Pireal.get_service("pireal")
        action = pireal.get_action("undo_action")
        action.setEnabled(value)

    def __on_redo_available(self, value):
        """ Change state of redo action """

        pireal = Pireal.get_service("pireal")
        action = pireal.get_action("redo_action")
        action.setEnabled(value)

    def __on_copy_available(self, value):
        """ Change states of cut and copy action """

        cut_action = Pireal.get_action("cut_action")
        cut_action.setEnabled(value)
        copy_action = Pireal.get_action("copy_action")
        copy_action.setEnabled(value)

    def show_relation(self, item):
        central_widget = Pireal.get_service("central")
        table_widget = central_widget.get_active_db().table_widget
        rela = self.relations[item.name]
        dialog = QDialog(self)
        dialog.resize(700, 500)
        dialog.setWindowTitle(item.name)
        box = QVBoxLayout(dialog)
        box.setContentsMargins(5, 5, 5, 5)
        table = table_widget.create_table(rela)
        box.addWidget(table)
        hbox = QHBoxLayout()
        btn = QPushButton(self.tr("Ok"))
        btn.clicked.connect(dialog.close)
        hbox.addStretch()
        hbox.addWidget(btn)
        box.addLayout(hbox)
        dialog.show()

    def save_sizes(self):
        """ Save sizes of Splitters """

        qsettings = QSettings(settings.SETTINGS_PATH, QSettings.IniFormat)
        qsettings.setValue('hsplitter_query_sizes',
                           self._hsplitter.saveState())
        qsettings.setValue('vsplitter_query_sizes',
                           self._vsplitter.saveState())

    def get_editor(self):
        return self._query_editor

    def __editor_modified(self, modified):
        self.editorModified.emit(modified)

    def showEvent(self, event):
        super(QueryWidget, self).showEvent(event)
        self._hsplitter.setSizes([1, self.width() / 3])

    def clear_results(self):
        self._result_list.clear_items()
        i = self._stack_tables.count()
        while i >= 0:
            widget = self._stack_tables.widget(i)
            self._stack_tables.removeWidget(widget)
            if widget is not None:
                widget.deleteLater()
            i -= 1

    def add_table(self, rela, rname):
        wtable = custom_table.Table()

        # wtable.setColumnCount(len(rela.fields))
        wtable.model().setHorizontalHeaderLabels(rela.header)

        for data in rela.content:
            nrow = wtable.model().rowCount()
            # wtable.insertRow(nrow)
            for col, text in enumerate(data):
                item = QStandardItem(text)
                wtable.model().setItem(nrow, col, item)

        index = self._stack_tables.addWidget(wtable)
        self._stack_tables.setCurrentIndex(index)

        self._result_list.add_item(rname, rela.count())


class StackedWidget(QStackedWidget):

    def setCurrentIndex(self, index):
        self.fader_widget = fader_widget.FaderWidget(self.currentWidget(),
                                                     self.widget(index))
        QStackedWidget.setCurrentIndex(self, index)

    def show_display(self, index):
        self.setCurrentIndex(index)
