import sys
import os
from PySide6.QtWidgets import QApplication, QDialog
from ui.login import LoginDialog
from ui.dashboard import DashboardKolam
from PySide6.QtGui import QIcon


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def main():
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(resource_path("app_icon.ico")))

    # ===== LOAD STYLE =====
    with open(resource_path("style/login.qss"), encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    login = LoginDialog()
    if login.exec() != QDialog.Accepted:
        sys.exit()

    with open(resource_path("style/dashboard.qss"), encoding="utf-8") as f:
        app.setStyleSheet(app.styleSheet() + f.read())

    dashboard = DashboardKolam(login.id_user)
    dashboard.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()