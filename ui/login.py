from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from database.query import QueryDatabase
from utils.session import Session
import hashlib
import os
import sys
from PySide6.QtGui import QIcon


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon(resource_path("app_icon.ico")))
        try:
            with open(resource_path("style/login.qss"), encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print("Gagal load login.qss:", e)

        self.db = QueryDatabase()
        self.setWindowTitle("Login")
        self.setFixedSize(1000, 600)
        self._buat_ui()

    def _buat_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # PANEL KIRI
        panel_kiri = QLabel()
        panel_kiri.setFixedWidth(420)

        bg_pixmap = QPixmap(resource_path("assets/login_bg.png"))
        panel_kiri.setPixmap(
            bg_pixmap.scaled(
                panel_kiri.size(),
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation
            )
        )
        panel_kiri.setScaledContents(True)

        root.addWidget(panel_kiri)

        # PANEL KANAN
        panel_kanan = QWidget()
        layout_kanan = QVBoxLayout(panel_kanan)
        layout_kanan.setContentsMargins(80, 60, 80, 60)
        layout_kanan.setSpacing(18)

        # LOGO
        logo = QLabel()
        logo_pix = QPixmap(resource_path("assets/logo.png"))
        logo.setPixmap(
            logo_pix.scaled(
                100, 100,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )
        logo.setAlignment(Qt.AlignCenter)
        layout_kanan.addWidget(logo)

        # TITLE
        title = QLabel("WELCOME")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold;")
        layout_kanan.addWidget(title)

        layout_kanan.addSpacing(20)

        # USERNAME
        layout_kanan.addWidget(QLabel("Username"))
        self.input_user = QLineEdit()
        self.input_user.setFixedHeight(38)
        layout_kanan.addWidget(self.input_user)

        # PASSWORD
        layout_kanan.addWidget(QLabel("Password"))
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.Password)
        self.input_pass.setFixedHeight(38)
        layout_kanan.addWidget(self.input_pass)

        layout_kanan.addSpacing(24)

        # BUTTON LOGIN
        btn_login = QPushButton("Mulai")
        btn_login.setFixedHeight(42)
        layout_kanan.addWidget(btn_login)

        # SIGN UP
        btn_signup = QPushButton("Sign Up")
        btn_signup.setFixedHeight(36)
        layout_kanan.addWidget(btn_signup)

        layout_kanan.addStretch()
        root.addWidget(panel_kanan)

        btn_login.clicked.connect(self.login)
        btn_signup.clicked.connect(self.daftar)

    # LOGIKA LOGIN 
    def _hash(self, text):
        return hashlib.sha256(text.encode()).hexdigest()

    def login(self):
        username = self.input_user.text().strip()
        password = self.input_pass.text().strip()
        user = self.db.login_user(username, password)

        if not user:
            QMessageBox.warning(self, "Gagal", "Username atau password salah.")
            return

        Session.id_user = user["id_user"]
        Session.username = user["username"]
        self.id_user = user["id_user"]
        self.accept()

    def daftar(self):
        username = self.input_user.text().strip()
        password = self.input_pass.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Peringatan", "Username & password wajib diisi.")
            return

        berhasil = self.db.daftar_user(username, self._hash(password))
        if berhasil:
            QMessageBox.information(
                self, "Sukses",
                "Akun berhasil dibuat. Silakan login."
            )
        else:
            QMessageBox.warning(
                self, "Gagal",
                "Username sudah digunakan."
            )
