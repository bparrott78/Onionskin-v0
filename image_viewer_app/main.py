import sys
from PyQt5.QtWidgets import QApplication
from image_viewer_app.gui.main_window import MainWindow # Corrected import path

def main():
    """
    Main function to run the Image Series Viewer application.
    """
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
