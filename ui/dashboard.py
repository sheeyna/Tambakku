from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QLabel, QHeaderView, QLineEdit, QDialog, QApplication
)
from PySide6.QtCore import Qt
from database.query import QueryDatabase
from utils.resource import resource_path
from utils.session import Session
from PySide6.QtGui import QIcon

class DashboardKolam(QMainWindow):
    def __init__(self, id_user):
        super().__init__()
        self.setWindowIcon(QIcon(resource_path("app_icon.ico")))
        self.id_user = id_user
        self.query = QueryDatabase(id_user)
        self._buat_tampilan()
        self.muat_data_dashboard()

    # TAMPILAN
    def _buat_tampilan(self):
        self.setWindowTitle("Dashboard Kolam Ikan")
        self.resize(1200, 720)

        root = QWidget()
        self.setCentralWidget(root)

        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(24)

        # ================= SIDEBAR =================
        sidebar = QVBoxLayout()
        sidebar.setSpacing(16)

        btn_tambah = QPushButton("Tambahkan\nKolam")
        btn_tambah.clicked.connect(self.tambah_kolam)

        btn_sortir = QPushButton("Sortir Ikan")
        btn_sortir.clicked.connect(self.buka_sortir_ikan)

        btn_hapus = QPushButton("Hapus Kolam")
        btn_hapus.clicked.connect(self.hapus_kolam)

        btn_logout = QPushButton("Logout")
        btn_logout.clicked.connect(self.logout)

        sidebar.addWidget(btn_tambah)
        sidebar.addWidget(btn_sortir)
        sidebar.addWidget(btn_hapus)
        sidebar.addStretch()
        sidebar.addWidget(btn_logout)

        root_layout.addLayout(sidebar, 1)

        # ================= KONTEN =================
        konten = QVBoxLayout()
        konten.setSpacing(16)

        header = QHBoxLayout()
        judul = QLabel("DASHBOARD")
        judul.setStyleSheet("font-size: 28px; font-weight: bold;")

        self.tombol_muat = QPushButton("Muat Ulang")
        self.tombol_muat.clicked.connect(self.muat_data_dashboard)

        self.tombol_jual = QPushButton("Jual")
        self.tombol_jual.clicked.connect(self.jual_ikan)

        header.addWidget(judul)
        header.addStretch()
        header.addWidget(self.tombol_muat)
        header.addWidget(self.tombol_jual)

        konten.addLayout(header)

        self.input_cari_kolam = QLineEdit()
        self.input_cari_kolam.setPlaceholderText("Pencarian")
        self.input_cari_kolam.textChanged.connect(self.filter_kolam_nama)
        konten.addWidget(self.input_cari_kolam)

        self.tabel = QTableWidget()
        self.tabel.setColumnCount(7)
        self.tabel.setHorizontalHeaderLabels([
            "ID", "Nama Kolam", "Ukuran Ikan",
            "Total Ikan", "Total Berat (Kg)",
            "Status", "Aksi"
        ])

        self.tabel.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabel.setSelectionMode(QTableWidget.SingleSelection)
        self.tabel.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabel.verticalHeader().setDefaultSectionSize(46)

        header_tbl = self.tabel.horizontalHeader()
        header_tbl.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_tbl.setSectionResizeMode(1, QHeaderView.Stretch)
        header_tbl.setSectionResizeMode(6, QHeaderView.Fixed)
        self.tabel.setColumnWidth(6, 100)

        konten.addWidget(self.tabel, 1)
        root_layout.addLayout(konten, 4)

    # DATA
    def muat_data_dashboard(self):
        data = self.query.ambil_dashboard_kolam()
        self.tabel.setRowCount(len(data))

        for baris, kolam in enumerate(data):
            self._isi(baris, 0, str(kolam["id_kolam"]), "tengah")
            self._isi(baris, 1, kolam["nama_kolam"])
            self._isi(baris, 2, kolam.get("ukuran_ikan", "-"), "tengah")
            self._isi(baris, 3, str(kolam.get("total_ikan", 0)), "kanan")
            self._isi(baris, 4, str(kolam.get("total_berat", 0)), "kanan")
            self._isi(baris, 5, kolam.get("status_kolam", "-"), "tengah")

            btn = QPushButton("Detail")
            btn.clicked.connect(
                lambda _, i=kolam["id_kolam"], n=kolam["nama_kolam"]:
                self.buka_detail_langsung(i, n)
            )

            w = QWidget()
            l = QHBoxLayout(w)
            l.setContentsMargins(0, 0, 0, 0)
            l.setAlignment(Qt.AlignCenter)
            l.addWidget(btn)

            self.tabel.setCellWidget(baris, 6, w)

    # AKSI
    def logout(self):
        if QMessageBox.question(
            self, "Logout", "Yakin ingin logout?"
        ) != QMessageBox.Yes:
            return

        Session.id_user = None
        Session.username = None
        self.close()

        from ui.login import LoginDialog
        login = LoginDialog()
        if login.exec() == QDialog.Accepted:
            DashboardKolam(login.id_user).show()
        else:
            QApplication.quit()

    def buka_detail_langsung(self, id_kolam, nama):
        from ui.detail_kolam import DetailKolam
        self.jendela_detail = DetailKolam(self.id_user, id_kolam, nama, self)
        self.jendela_detail.show()

    def filter_kolam_nama(self, teks):
        teks = teks.lower()
        for i in range(self.tabel.rowCount()):
            nama = self.tabel.item(i, 1).text().lower()
            self.tabel.setRowHidden(i, teks not in nama)

    def tambah_kolam(self):
        from ui.dialog_tambah_kolam import DialogTambahKolam
        if DialogTambahKolam(self).exec():
            self.muat_data_dashboard()

    def hapus_kolam(self):
        baris = self.tabel.currentRow()
        if baris < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih kolam.")
            return
        id_kolam = int(self.tabel.item(baris, 0).text())
        self.query.hapus_kolam(id_kolam)
        self.muat_data_dashboard()

    def buka_sortir_ikan(self):
        from ui.dialog_sortir_ikan import DialogSortirIkan
        if DialogSortirIkan(self.id_user, self).exec():
            self.muat_data_dashboard()

    def jual_ikan(self):
        baris = self.tabel.currentRow()
        if baris < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih kolam.")
            return
        id_kolam = int(self.tabel.item(baris, 0).text())
        nama = self.tabel.item(baris, 1).text()
        from ui.dialog_jual_ikan import DialogJualIkan
        if DialogJualIkan(self.id_user, id_kolam, nama, self).exec():
            self.muat_data_dashboard()

    # HELPER
    def _isi(self, baris, kolom, teks, rata=None):
        item = QTableWidgetItem(teks)
        if rata == "tengah":
            item.setTextAlignment(Qt.AlignCenter)
        elif rata == "kanan":
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tabel.setItem(baris, kolom, item)