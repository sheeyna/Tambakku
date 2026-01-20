from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QMessageBox, QRadioButton
)
from database.query import QueryDatabase

class DialogPindahIkan(QDialog):
    URUTAN_UKURAN = ["Bibit", "Ukuran 1", "Ukuran 2", "Ukuran 3"]

    def __init__(self, id_kolam_asal, nama_kolam_asal, parent=None):
        super().__init__(parent)
        self.db = QueryDatabase()
        self.id_kolam_asal = id_kolam_asal
        self.nama_kolam_asal = nama_kolam_asal

        detail = self.db.ambil_detail_kolam(id_kolam_asal)
        self.ukuran_asal = detail[0]["jenis_ukuran"].strip() if detail else None

        self.setWindowTitle("Pindahkan Ikan")
        self.setMinimumWidth(450)
        self._buat_tampilan()
        self._update_tujuan()

    # HELPER UKURAN
    def _ukuran_naik(self, ukuran):
        try:
            idx = self.URUTAN_UKURAN.index(ukuran)
            return self.URUTAN_UKURAN[idx + 1] if idx < len(self.URUTAN_UKURAN) - 1 else None
        except ValueError:
            return None

    # TAMPILAN
    def _buat_tampilan(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"Kolam Asal: {self.nama_kolam_asal}"))

        # ================= MODE UKURAN =================
        layout.addWidget(QLabel("Mode Ukuran:"))
        self.rb_tetap = QRadioButton("Tetap Ukuran")
        self.rb_naik = QRadioButton("Naik Ukuran (1 tingkat)")
        self.rb_tetap.setChecked(True)

        layout.addWidget(self.rb_tetap)
        layout.addWidget(self.rb_naik)

        layout.addWidget(QLabel("Kolam Tujuan (sesuai ukuran):"))
        self.combo_tujuan = QComboBox()
        layout.addWidget(self.combo_tujuan)

        layout.addWidget(QLabel("Jumlah ikan yang dipindahkan:"))
        self.input_jumlah = QLineEdit()
        self.input_jumlah.setPlaceholderText("misal: 100")
        layout.addWidget(self.input_jumlah)

        # Berat khusus Ukuran 3
        self.label_berat = QLabel("Jumlah Berat (Kg) (khusus Ukuran 3):")
        self.input_berat = QLineEdit()
        self.input_berat.setPlaceholderText("misal: 12.5")
        layout.addWidget(self.label_berat)
        layout.addWidget(self.input_berat)

        tombol = QHBoxLayout()
        btn_pindah = QPushButton("Pindahkan")
        btn_batal = QPushButton("Batal")

        btn_pindah.clicked.connect(self.pindahkan)
        btn_batal.clicked.connect(self.reject)

        tombol.addWidget(btn_pindah)
        tombol.addWidget(btn_batal)
        layout.addLayout(tombol)

        # Event
        self.rb_tetap.toggled.connect(self._update_tujuan)

    # UPDATE TUJUAN
    def _update_tujuan(self):
        self.combo_tujuan.clear()

        if not self.ukuran_asal:
            return

        ukuran_tujuan = (
            self._ukuran_naik(self.ukuran_asal)
            if self.rb_naik.isChecked()
            else self.ukuran_asal
        )

        semua_kolam = self.db.ambil_dashboard_kolam()

        for k in semua_kolam:
            if k.get("id_kolam") == self.id_kolam_asal:
                continue

            ukuran_k = (k.get("ukuran_ikan") or "").strip()
            total_ikan = int(k.get("total_ikan", 0) or 0)

            if ukuran_k == ukuran_tujuan or total_ikan == 0:
                self.combo_tujuan.addItem(
                    k.get("nama_kolam", "-"),
                    k.get("id_kolam")
                )

        if self.combo_tujuan.count() == 0:
            self.combo_tujuan.addItem("- Tidak ada kolam tujuan -", None)
            self.combo_tujuan.setEnabled(False)
        else:
            self.combo_tujuan.setEnabled(True)

        # Berat hanya jika tujuan Ukuran 3
        is_u3 = (ukuran_tujuan == "Ukuran 3")
        self.label_berat.setVisible(is_u3)
        self.input_berat.setVisible(is_u3)
        if not is_u3:
            self.input_berat.clear()

        # Disable naik ukuran jika sudah Ukuran 3
        self.rb_naik.setEnabled(self.ukuran_asal != "Ukuran 3")

    # AKSI PINDAHKAN
    def pindahkan(self):
        if not self.ukuran_asal:
            QMessageBox.warning(self, "Peringatan", "Kolam asal belum punya data.")
            return

        if not self.input_jumlah.text().isdigit():
            QMessageBox.warning(self, "Peringatan", "Jumlah ikan harus berupa angka.")
            return

        jumlah = int(self.input_jumlah.text())
        if jumlah <= 0:
            QMessageBox.warning(self, "Peringatan", "Jumlah ikan harus > 0.")
            return

        ukuran_tujuan = (
            self._ukuran_naik(self.ukuran_asal)
            if self.rb_naik.isChecked()
            else self.ukuran_asal
        )

        berat = None
        if ukuran_tujuan == "Ukuran 3":
            try:
                berat = float(self.input_berat.text())
            except ValueError:
                QMessageBox.warning(self, "Peringatan", "Berat wajib diisi dan berupa angka.")
                return

        id_tujuan = self.combo_tujuan.currentData()
        if id_tujuan is None:
            QMessageBox.warning(self, "Peringatan", "Tidak ada kolam tujuan yang valid.")
            return

        berhasil = self.db.sortir_ikan(
            self.id_kolam_asal,
            id_tujuan,
            ukuran_tujuan,
            jumlah,
            berat
        )

        if berhasil:
            QMessageBox.information(self, "Sukses", "Ikan berhasil dipindahkan.")
            self.accept()
        else:
            QMessageBox.critical(self, "Gagal", "Gagal memindahkan ikan.")
