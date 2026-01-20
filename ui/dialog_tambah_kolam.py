from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from database.query import QueryDatabase

class DialogTambahKolam(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = QueryDatabase()
        self.setWindowTitle("Tambah Kolam Baru")
        self.setMinimumWidth(350)
        self._buat_tampilan()

    def _buat_tampilan(self):
        layout = QVBoxLayout(self)

        label_nama = QLabel("Nama Kolam:")
        self.input_nama = QLineEdit()
        self.input_nama.setPlaceholderText("Contoh: Kolam 04")

        layout.addWidget(label_nama)
        layout.addWidget(self.input_nama)

        layout_tombol = QHBoxLayout()
        self.tombol_simpan = QPushButton("Simpan")
        self.tombol_batal = QPushButton("Batal")
        layout_tombol.addWidget(self.tombol_simpan)
        layout_tombol.addWidget(self.tombol_batal)

        layout.addLayout(layout_tombol)

        self.tombol_simpan.clicked.connect(self.simpan)
        self.tombol_batal.clicked.connect(self.reject)

    def simpan(self):
        nama = self.input_nama.text().strip()
        if not nama:
            QMessageBox.warning(self, "Peringatan", "Nama kolam tidak boleh kosong.")
            return

        hasil = self.db.tambah_kolam(nama)
        if hasil:
            QMessageBox.information(self, "Sukses", f"Kolam '{nama}' berhasil ditambahkan.")
            self.accept()
        else:
            QMessageBox.critical(self, "Gagal", "Gagal menambah kolam.")