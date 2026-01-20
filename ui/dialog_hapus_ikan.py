from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QLineEdit, QPushButton, QMessageBox
)
from database.query import QueryDatabase

class DialogHapusIkan(QDialog):
    def __init__(self, id_kolam, nama_kolam, parent=None):
        super().__init__(parent)
        self.db = QueryDatabase()
        self.id_kolam = id_kolam
        self.setWindowTitle(f"Hapus Ikan - {nama_kolam}")
        self.setMinimumWidth(400)

        detail = self.db.ambil_detail_kolam(id_kolam)
        self.detail = detail[0] if detail else None
        self._buat_tampilan()

    def _buat_tampilan(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Jenis Penghapusan:"))
        self.combo_jenis = QComboBox()
        self.combo_jenis.addItems(["Hapus Berkala", "Hapus Semua"])
        layout.addWidget(self.combo_jenis)

        layout.addWidget(QLabel("Jumlah Ikan:"))
        self.input_ikan = QLineEdit()
        layout.addWidget(self.input_ikan)

        layout.addWidget(QLabel("Jumlah Berat (Kg) [Ukuran 3]:"))
        self.input_berat = QLineEdit()
        layout.addWidget(self.input_berat)

        tombol = QHBoxLayout()
        btn_hapus = QPushButton("Hapus")
        btn_batal = QPushButton("Batal")
        tombol.addWidget(btn_hapus)
        tombol.addWidget(btn_batal)
        layout.addLayout(tombol)

        self.combo_jenis.currentTextChanged.connect(self._ubah_mode)
        btn_hapus.clicked.connect(self.hapus)
        btn_batal.clicked.connect(self.reject)

        self._ubah_mode(self.combo_jenis.currentText())

    def _ubah_mode(self, mode):
        if not self.detail:
            return

        if mode == "Hapus Semua":
            self.input_ikan.setText(str(self.detail.get("jumlah_ikan", 0)))
            self.input_ikan.setEnabled(False)

            if self.detail.get("jenis_ukuran") == "Ukuran 3":
                self.input_berat.setText(str(self.detail.get("jumlah_berat", 0)))
                self.input_berat.setEnabled(False)
            else:
                self.input_berat.clear()
                self.input_berat.setEnabled(False)
        else:
            self.input_ikan.clear()
            self.input_ikan.setEnabled(True)
            self.input_berat.clear()
            self.input_berat.setEnabled(True)

    def hapus(self):
        if not self.detail:
            QMessageBox.warning(self, "Peringatan", "Tidak ada data ikan.")
            return

        mode = self.combo_jenis.currentText()

        try:
            if mode == "Hapus Semua":
                jumlah_ikan = self.detail.get("jumlah_ikan", 0)
                jumlah_berat = (
                    self.detail.get("jumlah_berat", 0)
                    if self.detail.get("jenis_ukuran") == "Ukuran 3"
                    else None
                )
            else:
                jumlah_ikan = int(self.input_ikan.text())
                jumlah_berat = (
                    float(self.input_berat.text())
                    if self.detail.get("jenis_ukuran") == "Ukuran 3"
                    else None
                )
        except ValueError:
            QMessageBox.warning(self, "Peringatan", "Input tidak valid.")
            return

        berhasil = self.db.hapus_ikan(
            self.id_kolam,
            jumlah_ikan,
            jumlah_berat,
            mode=mode 
        )

        if berhasil:
            QMessageBox.information(self, "Sukses", "Ikan berhasil dihapus.")
            self.accept()
        else:
            QMessageBox.critical(self, "Gagal", "Gagal menghapus ikan.")
