import asyncio
import sys

from PyQt5.QtWidgets import QApplication

from quamash import QEventLoop

from index import Index
from logger.logger import get_logger


logger = get_logger("logger")


def start():
    app = QApplication(sys.argv)
    event_loop = QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    try:
        index = Index()
        index.show()
        with event_loop:
            event_loop.run_forever()
        sys.exit(0)
    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    start()
