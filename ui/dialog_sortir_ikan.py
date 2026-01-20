from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QLineEdit, QPushButton, QMessageBox, QRadioButton
)
from database.query import QueryDatabase

class DialogSortirIkan(QDialog):
    URUTAN_UKURAN = ["Bibit", "Ukuran 1", "Ukuran 2", "Ukuran 3"]

    def __init__(self, id_user, parent=None):
        super().__init__(parent)
        self.id_user = id_user
        self.db = QueryDatabase(id_user)

        self.setWindowTitle("Sortir / Pindah Ikan Antar Kolam")
        self.setMinimumWidth(520)

        self.data_dashboard = self.db.ambil_dashboard_kolam()

        self._buat_tampilan()
        self._muat_kolam_asal()
        self._update_tujuan_dan_kg()

    # TAMPILAN
    def _buat_tampilan(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Kolam Asal:"))
        self.cb_asal = QComboBox()
        layout.addWidget(self.cb_asal)

        # ================= MODE UKURAN =================
        layout.addWidget(QLabel("Mode Ukuran:"))
        self.rb_tetap = QRadioButton("Tetap Ukuran")
        self.rb_naik = QRadioButton("Naik Ukuran (1 tingkat)")
        self.rb_tetap.setChecked(True)

        layout.addWidget(self.rb_tetap)
        layout.addWidget(self.rb_naik)

        layout.addWidget(QLabel("Kolam Tujuan (sesuai ukuran):"))
        self.cb_tujuan = QComboBox()
        layout.addWidget(self.cb_tujuan)

        layout.addWidget(QLabel("Jumlah ikan yang dipindahkan:"))
        self.in_jumlah = QLineEdit()
        self.in_jumlah.setPlaceholderText("misal: 100")
        layout.addWidget(self.in_jumlah)

        # === Berat (Kg) khusus Ukuran 3 ===
        self.lbl_kg = QLabel("Jumlah Berat (Kg) (khusus Ukuran 3):")
        self.in_kg = QLineEdit()
        self.in_kg.setPlaceholderText("misal: 12.5")
        layout.addWidget(self.lbl_kg)
        layout.addWidget(self.in_kg)

        # Tombol
        row_btn = QHBoxLayout()
        btn_pindah = QPushButton("Pindahkan")
        btn_batal = QPushButton("Batal")
        row_btn.addWidget(btn_pindah)
        row_btn.addWidget(btn_batal)
        layout.addLayout(row_btn)

        # Event
        self.cb_asal.currentIndexChanged.connect(self._update_tujuan_dan_kg)
        self.rb_tetap.toggled.connect(self._update_tujuan_dan_kg)
        btn_pindah.clicked.connect(self.pindahkan)
        btn_batal.clicked.connect(self.reject)

    # LOGIKA UKURAN
    def _ukuran_naik(self, ukuran):
        try:
            idx = self.URUTAN_UKURAN.index(ukuran)
            return self.URUTAN_UKURAN[idx + 1] if idx < len(self.URUTAN_UKURAN) - 1 else None
        except ValueError:
            return None

    def _muat_kolam_asal(self):
        self.cb_asal.clear()
        for k in self.data_dashboard:
            ukuran = str(k.get("ukuran_ikan", "")).strip()
            if ukuran:
                self.cb_asal.addItem(k["nama_kolam"], k["id_kolam"])

    def _ambil_row(self, id_kolam):
        for k in self.data_dashboard:
            if int(k.get("id_kolam")) == int(id_kolam):
                return k
        return None

    def _update_tujuan_dan_kg(self):
        id_asal = self.cb_asal.currentData()
        if id_asal is None:
            return

        row_asal = self._ambil_row(id_asal)
        ukuran_asal = row_asal.get("ukuran_ikan")

        # Tentukan ukuran tujuan
        if self.rb_naik.isChecked():
            ukuran_tujuan = self._ukuran_naik(ukuran_asal)
            if ukuran_tujuan is None:
                self.rb_tetap.setChecked(True)
                ukuran_tujuan = ukuran_asal
        else:
            ukuran_tujuan = ukuran_asal

        # Update tujuan
        self.cb_tujuan.clear()
        for k in self.data_dashboard:
            if int(k["id_kolam"]) == int(id_asal):
                continue

            ukuran_k = str(k.get("ukuran_ikan", "")).strip()
            total_k = int(k.get("total_ikan", 0))

            if ukuran_k == ukuran_tujuan or total_k == 0:
                self.cb_tujuan.addItem(k["nama_kolam"], k["id_kolam"])

        # Berat hanya jika tujuan Ukuran 3
        is_u3 = (ukuran_tujuan == "Ukuran 3")
        self.lbl_kg.setVisible(is_u3)
        self.in_kg.setVisible(is_u3)
        if not is_u3:
            self.in_kg.clear()

        # Disable naik ukuran jika asal Ukuran 3
        self.rb_naik.setEnabled(ukuran_asal != "Ukuran 3")

    # AKSI
    def pindahkan(self):
        id_asal = self.cb_asal.currentData()
        id_tujuan = self.cb_tujuan.currentData()

        if id_asal is None or id_tujuan is None:
            QMessageBox.warning(self, "Peringatan", "Kolam asal / tujuan belum valid.")
            return

        if not self.in_jumlah.text().isdigit():
            QMessageBox.warning(self, "Peringatan", "Jumlah ikan harus angka.")
            return

        jumlah_ikan = int(self.in_jumlah.text())
        if jumlah_ikan <= 0:
            QMessageBox.warning(self, "Peringatan", "Jumlah ikan harus > 0.")
            return

        row_asal = self._ambil_row(id_asal)
        ukuran_asal = row_asal.get("ukuran_ikan")

        ukuran_tujuan = (
            self._ukuran_naik(ukuran_asal)
            if self.rb_naik.isChecked()
            else ukuran_asal
        )

        berat = None
        if ukuran_tujuan == "Ukuran 3":
            try:
                berat = float(self.in_kg.text())
            except ValueError:
                QMessageBox.warning(self, "Peringatan", "Berat harus diisi & berupa angka.")
                return

        berhasil = self.db.sortir_ikan(
            id_kolam_asal=id_asal,
            id_kolam_tujuan=id_tujuan,
            jenis_ukuran=ukuran_tujuan,
            jumlah_ikan=jumlah_ikan,
            jumlah_berat=berat
        )

        if berhasil:
            nama_kolam_tujuan = self.cb_tujuan.currentText()

            if self.rb_naik.isChecked() and ukuran_asal != ukuran_tujuan:
                self.db.tambah_riwayat(
                    id_kolam=id_tujuan,
                    jenis_ukuran=ukuran_tujuan,
                    jumlah_ikan=jumlah_ikan,
                    jumlah_berat=berat,
                    keterangan=f"Naik ukuran dari {ukuran_asal} ke {ukuran_tujuan} (Kolam {nama_kolam_tujuan})"
                )

            QMessageBox.information(self, "Sukses", "Ikan berhasil dipindahkan.")
            self.accept()
        else:
            QMessageBox.critical(self, "Gagal", "Gagal memindahkan ikan.")
