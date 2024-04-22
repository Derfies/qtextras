import logging
import sys

import qdarktheme

from appskeleton.application import Application
from appskeleton.mainwindow import MainWindow


logger = logging.getLogger(__name__)


DEFAULT_COMPANY_NAME = 'Enron'
DEFAULT_APP_NAME = 'Application Skeleton'


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app = Application(sys.argv)
    qdarktheme.setup_theme()
    window = MainWindow(DEFAULT_COMPANY_NAME, DEFAULT_APP_NAME)
    window.show()
    sys.exit(app.exec())
