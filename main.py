import sys
from PyQt5.QtWidgets import QApplication
from tracker_app import MainWindow

def main():
    # setup PyQt env
    app = QApplication(sys.argv)

    window = MainWindow()

    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()