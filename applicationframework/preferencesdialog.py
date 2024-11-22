from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QStackedWidget,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


class PreferenceWidgetBase(QWidget):

    """
    Should define a panel that can easily be added to the preference dialog, and
    a dict that can be passed when the dialog is dismissed.

    """

    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO: Pass default dict in.
        self.name = name
        self.layout = QVBoxLayout(self)

    def get_preferences(self):
        ...


class PreferencesDialog(QDialog):

    """
    TODO: Figure out where to save this (QSettings or json blob)
    TODO: Figure out if these are project-centric or application centric (maybe both)?
    TODO: Initial selection
    TODO: Initial values

    """

    def __init__(self):
        super().__init__()
        self.set_window_title("Preferences")
        self.resize(600, 400)

        self.widgets = {}

        # Dictionary to store preferences
        # TODO: Expose this to pass in and populate all panes.
        # self.preferences = {
        #     "username": "",
        #     "notifications": False,
        #     "theme": "",
        #     "font_size": "",
        #     "proxy_server": "",
        #     "port": "",
        #     "use_https": False,
        # }

        # Create the main layout
        main_layout = QVBoxLayout(self)

        # Create a horizontal layout for the content
        #content_layout = QHBoxLayout()
        self.hsplitter = QSplitter(Qt.Orientation.Horizontal)

        # Create the tree view for categories
        self.tree_view = QTreeView()
        self.tree_view.set_header_hidden(True)
        self.tree_model = QStandardItemModel()
        self.tree_view.set_model(self.tree_model)

        # Create a stacked widget to show the content of each category
        self.stacked_widget = QStackedWidget()

        # Connect the tree selection to the stacked widget
        self.tree_view.selection_model().selectionChanged.connect(self.on_selection_changed)

        # Add the tree view and stacked widget to the content layout
        self.hsplitter.add_widget(self.tree_view)
        self.hsplitter.add_widget(self.stacked_widget)

        # Add content layout to the main layout
        main_layout.add_widget(self.hsplitter)

        # Add OK and Cancel buttons in a horizontal layout
        self.ok_button = QPushButton('OK')
        self.cancel_button = QPushButton('Cancel')
        self.ok_button.clicked.connect(self.save_preferences)
        self.cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.add_spacer_item(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        button_layout.add_widget(self.ok_button)
        button_layout.add_widget(self.cancel_button)

        # Anchor the button layout to the bottom
        main_layout.add_layout(button_layout)

    def add_widget(self, widget: PreferenceWidgetBase):
        item = QStandardItem(widget.name)
        item.set_editable(False)
        self.tree_model.append_row(item)
        self.stacked_widget.add_widget(widget)
        self.widgets[widget.name] = widget

    def on_selection_changed(self, selected, deselected):
        """Handle changes in the tree view selection."""
        index = self.tree_view.selection_model().current_index()
        self.stacked_widget.set_current_index(index.row())

    def save_preferences(self):
        """Save the preferences when OK is pressed."""
        self.preferences = {}
        for key, widget in self.widgets.items():
            self.preferences[key] = widget.get_preferences()
        print("Preferences saved:", self.preferences)
        self.accept()  # Close the dialog
