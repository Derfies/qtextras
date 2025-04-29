import sys

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ListEditor(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Main layout.
        layout = QVBoxLayout(self)

        # List widget to hold items.
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        # Input field + Add button.
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText('Enter item...')
        self.add_button = QPushButton('+')
        self.add_button.setFixedWidth(30)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.add_button)
        layout.addLayout(input_layout)

        # Remove button.
        self.remove_button = QPushButton('Remove Selected')
        layout.addWidget(self.remove_button)

        # Connect buttons.
        self.add_button.clicked.connect(self.add_item)
        self.remove_button.clicked.connect(self.remove_item)
        self.input_field.returnPressed.connect(self.add_item)

    def add_item(self):
        text = self.input_field.text().strip()
        if text:
            self.list_widget.addItem(text)
            self.input_field.clear()

    def remove_item(self):
        selected_items = self.list_widget.selectedItems()
        for item in selected_items:
            self.list_widget.takeItem(self.list_widget.row(item))

    def items(self):
        return [self.list_widget.item(i).text() for i in range(self.list_widget.count())]

    def set_items(self, items: list[str]):
        for item in items:
            self.list_widget.addItem(item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = ListEditor()
    editor.show()
    sys.exit(app.exec())
