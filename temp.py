import sys

import functools
from PySide6.QtWidgets import QApplication

from PySide6.QtWidgets import QLabel

from PySide6.QtWidgets import QPushButton

from PySide6.QtWidgets import QVBoxLayout

from PySide6.QtWidgets import QWidget


def greeting(who):
    """Slot function."""
    if msg.text():
        msg.setText('')
    else:
        msg.setText(f'Hello {who}')



app = QApplication(sys.argv)

window = QWidget()

window.setWindowTitle('Signals and slots')

layout = QVBoxLayout()


btn = QPushButton('Greet')

# btn.clicked.connect(greeting)  # Connect clicked to greeting()
# btn.clicked.connect(functools.partial(greeting, 'World!'))
btn.clicked.connect(lambda: greeting('World!'))


layout.addWidget(btn)

msg = QLabel('')

layout.addWidget(msg)

window.setLayout(layout)

window.show()

sys.exit(app.exec_())