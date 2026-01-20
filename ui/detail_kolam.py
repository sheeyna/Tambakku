from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt
from database.query import QueryDatabase

class DetailKolam(QMainWindow):
    def __init__(self, id_user, id_kolam, nama_kolam, parent=None):
        super().__init__()
        self.id_user = id_user
        self.id_kolam = id_kolam
        self.nama_kolam = nama_kolam
        self.query = QueryDatabase(id_user)

        self.setWindowTitle(f"Detail Kolam - {nama_kolam}")
        self.resize(1200, 720)

        self._buat_tampilan()
        self.muat_detail()
        self.muat_riwayat_ringkas()

    # TAMPILAN
    def _buat_tampilan(self):
        # ===== ROOT =====
        root_widget = QWidget()
        self.setCentralWidget(root_widget)

        root_layout = QHBoxLayout(root_widget)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(24)

        # SIDEBAR KIRI
        sidebar = QVBoxLayout()
        sidebar.setSpacing(16)

        self.btn_tambah = QPushButton("Tambahkan\nData")
        self.btn_pindah = QPushButton("Pindahkan Ikan")
        self.btn_riwayat = QPushButton("Riwayat")
        self.btn_hapus = QPushButton("Hapus")
        self.btn_kembali = QPushButton("Kembali")

        self.btn_tambah.clicked.connect(self.tambah_data)
        self.btn_pindah.clicked.connect(self.pindahkan_ikan)
        self.btn_riwayat.clicked.connect(self.buka_riwayat)
        self.btn_hapus.clicked.connect(self.hapus_data)
        self.btn_kembali.clicked.connect(self.close)

        sidebar.addWidget(self.btn_tambah)
        sidebar.addWidget(self.btn_pindah)
        sidebar.addWidget(self.btn_riwayat)
        sidebar.addWidget(self.btn_hapus)
        sidebar.addStretch()
        sidebar.addWidget(self.btn_kembali)

        root_layout.addLayout(sidebar, 1)

        # KONTEN KANAN
        konten = QVBoxLayout()
        konten.setSpacing(16)

        # ---------- HEADER ----------
        header = QHBoxLayout()
        judul = QLabel(self.nama_kolam)
        judul.setStyleSheet("font-size: 26px; font-weight: bold;")

        self.btn_jual = QPushButton("Jual")
        self.btn_jual.clicked.connect(self.jual_ikan)

        header.addWidget(judul)
        header.addStretch()
        header.addWidget(self.btn_jual)

        konten.addLayout(header)

        # ---------- TABEL ----------
        self.tabel = QTableWidget()
        self.tabel.setColumnCount(5)
        self.tabel.setHorizontalHeaderLabels([
            "ID Detail",
            "Ukuran Ikan",
            "Jumlah Ikan",
            "Berat Ikan (Kg)",
            "Tanggal Pembaruan"
        ])

        self.tabel.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabel.setSelectionMode(QTableWidget.SingleSelection)
        self.tabel.setEditTriggers(QTableWidget.NoEditTriggers)

        header_tbl = self.tabel.horizontalHeader()
        header_tbl.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_tbl.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header_tbl.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header_tbl.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header_tbl.setSectionResizeMode(4, QHeaderView.Stretch)

        konten.addWidget(self.tabel, 1)

        # ---------- SUMMARY ----------
        summary = QHBoxLayout()

        self.lbl_jumlah = QLabel("Jumlah Ikan")
        self.lbl_berat = QLabel("Berat Ikan")

        self.lbl_jumlah.setAlignment(Qt.AlignCenter)
        self.lbl_berat.setAlignment(Qt.AlignCenter)

        self.lbl_jumlah.setMinimumHeight(80)
        self.lbl_berat.setMinimumHeight(80)

        summary.addWidget(self.lbl_jumlah)
        summary.addWidget(self.lbl_berat)

        konten.addLayout(summary)

        root_layout.addLayout(konten, 4)

    # DATA
    def muat_detail(self):
        data = self.query.ambil_detail_kolam(self.id_kolam)
        self.tabel.setRowCount(len(data))

        total_ikan = 0
        total_berat = 0

        for row, d in enumerate(data):
            self._isi(row, 0, str(d["id_detail"]), "tengah")
            self._isi(row, 1, d["jenis_ukuran"], "tengah")
            self._isi(row, 2, str(d["jumlah_ikan"]), "kanan")
            self._isi(row, 3, str(d["jumlah_berat"] or "-"), "kanan")
            self._isi(row, 4, d["tanggal_pembaruan"])

            total_ikan += int(d["jumlah_ikan"])
            total_berat += float(d["jumlah_berat"] or 0)

        self.lbl_jumlah.setText(f"Jumlah Ikan\n{total_ikan}")
        self.lbl_berat.setText(f"Berat Ikan\n{total_berat} Kg")

    def muat_riwayat_ringkas(self):
        pass

    # AKSI
    def tambah_data(self):
        from ui.dialog_tambah_data import DialogTambahData
        dialog = DialogTambahData(self.id_kolam, self)
        if dialog.exec():
            self.muat_detail()

    def pindahkan_ikan(self):
        from ui.dialog_pindah_ikan import DialogPindahIkan
        dialog = DialogPindahIkan(self.id_kolam, self.nama_kolam, self)
        if dialog.exec():
            self.muat_detail()

    def jual_ikan(self):
        from ui.dialog_jual_ikan import DialogJualIkan
        dialog = DialogJualIkan(self.id_user, self.id_kolam, self.nama_kolam, self)
        if dialog.exec():
            self.muat_detail()

    def hapus_data(self):
        from ui.dialog_hapus_ikan import DialogHapusIkan

        dialog = DialogHapusIkan(
            self.id_kolam,
            self.nama_kolam,
            self
        )

        if dialog.exec():
            self.muat_detail()


    def buka_riwayat(self):
        from ui.dialog_riwayat_kolam import DialogRiwayatKolam
        dialog = DialogRiwayatKolam(self.id_kolam, self)
        dialog.exec()

    # HELPER
    def _isi(self, baris, kolom, teks, rata=None):
        item = QTableWidgetItem(teks)
        if rata == "tengah":
            item.setTextAlignment(Qt.AlignCenter)
        elif rata == "kanan":
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tabel.setItem(baris, kolom, item)
