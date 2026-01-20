from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox
)
from database.query import QueryDatabase


class DialogTambahData(QDialog):
    def __init__(self, id_kolam, parent=None):
        super().__init__(parent)
        self.id_kolam = id_kolam
        self.db = QueryDatabase()

        # Ambil ukuran kolam tujuan (jika sudah ada data)
        detail = self.db.ambil_detail_kolam(id_kolam)
        self.ukuran_tujuan = detail[0]["jenis_ukuran"] if detail else None

        self.setWindowTitle("Tambah Data Detail Kolam")
        self.setMinimumWidth(420)
        self._buat_tampilan()

    def _buat_tampilan(self):
        layout = QVBoxLayout(self)

        # Sumber ikan
        layout.addWidget(QLabel("Sumber Ikan:"))
        self.input_sumber = QComboBox()
        self.input_sumber.addItem("🐟 Bibit Baru / Ikan Baru", None)

        # Filter kolam berdasarkan ukuran yang sama
        if self.ukuran_tujuan:
            semua_kolam = self.db.ambil_dashboard_kolam()
            for k in semua_kolam:
                if (
                    k["id_kolam"] != self.id_kolam and
                    k["ukuran_ikan"] == self.ukuran_tujuan and
                    k["total_ikan"] > 0
                ):
                    self.input_sumber.addItem(
                        f'{k["nama_kolam"]} ({k["total_ikan"]} ekor)',
                        k["id_kolam"]
                    )

        layout.addWidget(self.input_sumber)

        # Jenis ukuran (dikunci jika kolam sudah punya ukuran)
        layout.addWidget(QLabel("Jenis Ukuran:"))
        self.input_ukuran = QComboBox()
        self.input_ukuran.addItems(["Bibit", "Ukuran 1", "Ukuran 2", "Ukuran 3"])

        if self.ukuran_tujuan:
            self.input_ukuran.setCurrentText(self.ukuran_tujuan)
            self.input_ukuran.setEnabled(False)

        layout.addWidget(self.input_ukuran)

        # Jumlah ikan
        layout.addWidget(QLabel("Jumlah Ikan:"))
        self.input_jumlah = QLineEdit()
        self.input_jumlah.setPlaceholderText("misal: 500")
        layout.addWidget(self.input_jumlah)

        # Berat (khusus Ukuran 3)
        layout.addWidget(QLabel("Jumlah Berat (Kg) [hanya Ukuran 3]:"))
        self.input_berat = QLineEdit()
        self.input_berat.setPlaceholderText("misal: 120.5")
        layout.addWidget(self.input_berat)

        # Tombol
        tombol_layout = QHBoxLayout()
        btn_simpan = QPushButton("Simpan")
        btn_batal = QPushButton("Batal")

        btn_simpan.clicked.connect(self.simpan)
        btn_batal.clicked.connect(self.reject)

        tombol_layout.addWidget(btn_simpan)
        tombol_layout.addWidget(btn_batal)
        layout.addLayout(tombol_layout)

    # SIMPAN
    def simpan(self):
        ukuran = self.input_ukuran.currentText()
        sumber = self.input_sumber.currentData()

        if not self.input_jumlah.text().isdigit():
            QMessageBox.warning(self, "Peringatan", "Jumlah ikan harus angka.")
            return

        jumlah = int(self.input_jumlah.text())
        berat = self.input_berat.text().strip()
        berat_val = float(berat) if berat else None

        if ukuran == "Ukuran 3" and berat_val is None:
            QMessageBox.warning(self, "Peringatan", "Ukuran 3 wajib mengisi berat.")
            return

        # JIKA DARI KOLAM LAIN (SORTIR)
        if sumber:
            berhasil = self.db.sortir_ikan(
                sumber,
                self.id_kolam,
                ukuran,
                jumlah,
                berat_val
            )
            if berhasil:
                QMessageBox.information(self, "Sukses", "Ikan berhasil dipindahkan.")
                self.accept()
            else:
                QMessageBox.critical(self, "Gagal", "Gagal memindahkan ikan.")
            return

        # BIBIT BARU
        hasil = self.db.tambah_detail_kolam(
            self.id_kolam,
            ukuran,
            jumlah,
            berat_val
        )

        if hasil:
            QMessageBox.information(self, "Sukses", "Data berhasil ditambahkan.")
            self.accept()
        else:
            QMessageBox.critical(self, "Gagal", "Gagal menambahkan data.")