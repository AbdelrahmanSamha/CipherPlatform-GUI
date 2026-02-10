import sys
from PySide6.QtWidgets import QApplication
from ui.splash_screen import SplashScreen
from controller.app_controller import AppController

def main():
    app = QApplication(sys.argv)

    # Central controller (the "brain")
    controller = AppController()

    # Splash screen shown first
    splash = SplashScreen()
    splash.start_requested.connect(controller.show_main_window)

    splash.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
