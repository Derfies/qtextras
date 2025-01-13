from unittest import TestCase

from PySide6.QtWidgets import QLineEdit

from applicationframework.application import Application
from applicationframework.preferencesdialog import PreferencesDialog, PreferenceWidgetBase

# noinspection PyUnresolvedReferences
from __feature__ import snake_case


class TestPreferenceWidget(PreferenceWidgetBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.baz = QLineEdit()
        self.qux = QLineEdit()

    def preferences(self):
        return {
            'baz': self.baz.text(),
            'qux': self.qux.text(),
        }

    def set_preferences(self, data: dict):
        self.baz.set_text(data['baz'])
        self.qux.set_text(data['qux'])


class TestPreferencesDialog(PreferencesDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_widget(TestPreferenceWidget('foo'))


class PreferencesDialogTestCase(TestCase):

    def setUp(self):
        """
        Set up a new QApplication instance before each test.

        """
        self.app = Application.instance()
        if self.app is None:
            self.app = Application('mycompany', 'Test Application')

    def tearDown(self):
        """
        Destroy the QApplication instance after each test.

        """
        self.app.quit()
        del self.app

    def test_save_preferences(self):

        # Set up test data.
        dialog = TestPreferencesDialog()
        dialog.widgets['foo'].baz.set_text('test1')
        dialog.widgets['foo'].qux.set_text('test2')

        # Start test.
        dialog.save_preferences()

        # Assert results.
        self.assertDictEqual({'foo': {'baz': 'test1', 'qux': 'test2'}}, dialog.preferences)

    def test_load_preferences(self):

        # Set up test data.
        dialog = TestPreferencesDialog()

        # Start test.
        dialog.load_preferences(
            {
                'foo': {
                    'baz': 'test1',
                    'qux': 'test2',
                },
            }
        )

        # Assert results.
        self.assertEqual('test1', dialog.widgets['foo'].baz.text())
        self.assertEqual('test2', dialog.widgets['foo'].qux.text())
