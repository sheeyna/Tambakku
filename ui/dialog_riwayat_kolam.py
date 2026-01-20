from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QDateEdit
)
from PySide6.QtCore import Qt, QDate
from database.query import QueryDatabase


class DialogRiwayatKolam(QDialog):
    def __init__(self, id_kolam, nama_kolam, parent=None):
        super().__init__(parent)
        self.db = QueryDatabase()
        self.id_kolam = id_kolam
        self.nama_kolam = nama_kolam

        self.setWindowTitle(f"Riwayat Aksi - {self.nama_kolam}")
        self.resize(900, 500)

        self._buat_tampilan()
        self.muat_data()  # default: semua riwayat kolam

    def _buat_tampilan(self):
        layout = QVBoxLayout(self)

        # Filter tanggal
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("Tanggal:"))
        self.input_tanggal = QDateEdit()
        self.input_tanggal.setCalendarPopup(True)
        self.input_tanggal.setDate(QDate.currentDate())
        filter_layout.addWidget(self.input_tanggal)

        tombol_filter = QPushButton("Cari")
        tombol_filter.clicked.connect(self.cari)
        filter_layout.addWidget(tombol_filter)

        tombol_reset = QPushButton("Tampilkan Semua")
        tombol_reset.clicked.connect(self.tampilkan_semua)
        filter_layout.addWidget(tombol_reset)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Tabel riwayat
        self.tabel = QTableWidget()
        self.tabel.setColumnCount(5)
        self.tabel.setHorizontalHeaderLabels([
            "Tanggal",
            "Jenis Ukuran",
            "Jumlah Ikan",
            "Jumlah Berat",
            "Keterangan"
        ])
        self.tabel.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabel.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.tabel)

        tombol_tutup = QPushButton("Tutup")
        tombol_tutup.clicked.connect(self.close)
        layout.addWidget(tombol_tutup)

    def muat_data(self, data=None):
        if data is None:
            data = self.db.ambil_riwayat_per_kolam(self.id_kolam)

        self.tabel.setRowCount(len(data))

        for baris, r in enumerate(data):
            self._isi(baris, 0, str(r.get("tanggal_aksi", "")))
            self._isi(baris, 1, r.get("jenis_ukuran", ""))
            self._isi(baris, 2, str(r.get("jumlah_ikan", 0)), kanan=True)
            self._isi(baris, 3, str(r.get("jumlah_berat", "")), kanan=True)
            self._isi(baris, 4, r.get("keterangan", ""))

    def cari(self):
        tanggal = self.input_tanggal.date().toString("yyyy-MM-dd")
        data = self.db.ambil_riwayat_per_kolam(self.id_kolam, tanggal=tanggal)
        self.muat_data(data)

    def tampilkan_semua(self):
        self.muat_data(None)

    def _isi(self, baris, kolom, teks, kanan=False):
        item = QTableWidgetItem(teks)
        if kanan:
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tabel.setItem(baris, kolom, item)