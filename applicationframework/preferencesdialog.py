from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QStackedWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


class PreferenceWidgetBase(QWidget):

    """
    Should define a panel that can easily be added to the preference dialog, and
    a dict that can be passed when the dialog is dismissed.

    TODO: Maybe use name / label so we can have pretty user string and the string
    to use to same values against.

    TODO: Would be cool to use marshmallow to do type conversion similar to
    Django forms.

    """

    def __init__(self, title: str, name: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title = title
        if name is None:
            name = self.title.lower().replace(' ', '_')
        self.name = name
        self.layout = QVBoxLayout(self)

    def preferences(self) -> dict[str, Any]:
        ...

    def set_preferences(self, data):
        ...


class PreferencesDialog(QDialog):

    """
    TODO: Figure out where to save this (QSettings or json blob)
    TODO: Figure out if these are project-centric or application centric (maybe both)?

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_window_title('Preferences')
        self.resize(600, 400)

        self.widgets = {}
        self.preferences = {}

        # Create the main layout
        main_layout = QVBoxLayout(self)

        # Create a horizontal layout for the content.
        self.hsplitter = QSplitter(Qt.Orientation.Horizontal)

        # Create the tree view for categories.
        self.tree_view = QTreeWidget()
        self.tree_view.set_header_hidden(True)
        #self.tree_model = QStandardItemModel()
        #self.tree_view.set_model(self.tree_model)

        # Create a stacked widget to show the content of each category.
        self.stacked_widget = QStackedWidget()

        # Connect the tree selection to the stacked widget.
        self.tree_view.selection_model().selectionChanged.connect(self.on_selection_changed)

        # Add the tree view and stacked widget to the content layout.
        self.hsplitter.add_widget(self.tree_view)
        self.hsplitter.add_widget(self.stacked_widget)

        # Add content layout to the main layout.
        main_layout.add_widget(self.hsplitter)

        # Add OK and Cancel buttons in a horizontal layout.
        self.ok_button = QPushButton('OK')
        self.cancel_button = QPushButton('Cancel')
        self.ok_button.clicked.connect(self.save_preferences)
        self.cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.add_spacer_item(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        button_layout.add_widget(self.ok_button)
        button_layout.add_widget(self.cancel_button)

        # Anchor the button layout to the bottom.
        main_layout.add_layout(button_layout)

    # def show_event(self, event: QEvent):
    #     """Select the first listbox item if there is one."""
    #     root_index = self.tree_view.root_index()
    #     first_item_index = self.tree_model.index(0, 0, root_index)  # First item under the root index
    #     self.tree_view.set_current_index(first_item_index)

    # def get_absolute_row(self, item):
    #     """ Computes the absolute row of the given QTreeWidgetItem """
    #
    #     def count_items(root_item, target_item, count=0):
    #         """ Recursively count items to find the absolute row. """
    #         for i in range(root_item.child_count()):
    #             child = root_item.child(i)
    #             count += 1
    #             if child == target_item:
    #                 return count
    #             count = count_items(child, target_item, count)
    #         return count
    #
    #     if item is None:
    #         return -1  # Invalid item
    #
    #     count = 0
    #     for i in range(self.tree_view.top_level_item_count()):
    #         root_item = self.tree_view.top_level_item(i)
    #         if root_item == item:
    #             return count
    #         count += 1
    #         result = count_items(root_item, item, count)
    #         if result > count:
    #             return result
    #         count = result
    #
    #     return -1  # Not found

    def add_widget(self, widget: PreferenceWidgetBase, parent=None):
        if parent is None:
            parent = self.tree_view
        item = QTreeWidgetItem(parent)#idget.title)
        item.set_data(0, Qt.UserRole, widget)  # Qt.UserRole = 256

        item.set_text(0, widget.title)

        #item.set_editable(False)
        #self.tree_model.append_row(item)
        self.stacked_widget.add_widget(widget)
        self.widgets[widget.name] = widget

        return item

    def on_selection_changed(self, selected, deselected):
        """Handle changes in the tree view selection."""
        item = self.tree_view.selected_items()[0]

        widget = item.data(0, Qt.UserRole)
        #print(pane)
        #print(item, self.get_absolute_row(item))
        #print('SET:', index.row())
        self.stacked_widget.set_current_widget(widget)

    def load_preferences(self, data: dict):
        for key, value in data.items():
            self.widgets[key].set_preferences(value)

    def save_preferences(self):
        """Save the preferences when OK is pressed."""
        self.preferences = {}
        for key, widget in self.widgets.items():
            self.preferences[key] = widget.preferences()
        self.accept()  # Close the dialog
