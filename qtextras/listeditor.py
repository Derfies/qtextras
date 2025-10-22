from typing import Iterable

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from applicationframework.mixins import HasAppMixin

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


class ItemDialog(QDialog):

    def __init__(self, headers, values=None, parent=None):
        super().__init__(parent)
        self.set_window_title('Edit Item' if values else 'New Item')

        self.inputs = {}
        form = QFormLayout(self)
        for i, header in enumerate(headers):
            line_edit = QLineEdit(values[i] if values else '')
            self.inputs[header] = line_edit
            form.add_row(header + ':', line_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.add_widget(buttons)

    def get_values(self):
        return [field.text() for field in self.inputs.values()]


class ListEditor(QWidget, HasAppMixin):

    def __init__(self, headers: Iterable[str], *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QVBoxLayout(self)
        layout.set_contents_margins(0, 0, 0, 0)

        # Buttons.
        button_layout = QHBoxLayout()
        button_layout.set_contents_margins(0, 0, 0, 0)
        button_layout.set_spacing(4)
        add_button = QPushButton()
        add_button.set_icon(self.app().get_icon('plus'))
        add_button.set_flat(True)
        remove_button = QPushButton()
        remove_button.set_icon(self.app().get_icon('minus'))
        remove_button.set_flat(True)
        edit_button = QPushButton()
        edit_button.set_icon(self.app().get_icon('pencil'))
        edit_button.set_flat(True)
        button_layout.add_widget(add_button)
        button_layout.add_widget(remove_button)
        button_layout.add_widget(edit_button)
        button_layout.add_stretch(1)
        layout.add_layout(button_layout)

        # Connect buttons
        add_button.clicked.connect(self.add_item)
        remove_button.clicked.connect(self.remove_item)
        edit_button.clicked.connect(self.edit_item)

        # TreeWidget used as a multi-column list view.
        self._headers = headers
        self._tree = QTreeWidget()
        self._tree.set_header_labels(self._headers)
        self._tree.set_root_is_decorated(False)
        self._tree.set_column_count(len(self._headers))
        layout.add_widget(self._tree)

    def add_item(self):
        dialog = ItemDialog(self._headers, parent=self)
        if dialog.exec():
            values = dialog.get_values()
            item = QTreeWidgetItem(values)
            self._tree.add_top_level_item(item)

    def edit_item(self):
        item = self._tree.current_item()
        if not item:
            return
        values = [item.text(i) for i in range(self._tree.column_count())]
        dialog = ItemDialog(self._headers, values, parent=self)
        if dialog.exec():
            new_values = dialog.get_values()
            for col, value in enumerate(new_values):
                item.set_text(col, value)

    def remove_item(self):
        item = self._tree.current_item()
        if not item:
            return
        index = self._tree.index_of_top_level_item(item)
        self._tree.take_top_level_item(index)

    def get_values(self):
        values = []
        for i in range(self._tree.top_level_item_count()):
            item = self._tree.top_level_item(i)
            values.append([item.text(col) for col in range(self._tree.column_count())])
        return values
