from database.koneksi import buat_koneksi
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class QueryDatabase:
    def __init__(self, id_user=None):
        self.koneksi = buat_koneksi()
        self.id_user = id_user

    # LOGIN & USER
    def daftar_user(self, username, password_hash):
        try:
            self.koneksi.table("users").insert({
                "username": username,
                "password_hash": password_hash
            }).execute()
            return True
        except:
            return False

    def login_user(self, username, password):
        try:
            hasil = (
                self.koneksi.table("users")
                .select("*")
                .eq("username", username)
                .single()
                .execute()
            )

            if not hasil.data:
                return None

            input_hash = hash_password(password)

            if input_hash != hasil.data["password_hash"]:
                return None

            return hasil.data

        except Exception as error:
            print("❌ Gagal login:", error)
            return None

    def signup_user(self, username, password):
        try:
            password_hash = hash_password(password)
            hasil = self.koneksi.table("users").insert({
                "username": username,
                "password_hash": password_hash
            }).execute()
            return True if hasil.data else False
        except Exception as error:
            print("❌ Gagal signup:", error)
            return False

    # DASHBOARD KOLAM
    def ambil_dashboard_kolam(self):
        try:
            hasil = (
                self.koneksi.table("view_dashboard_kolam")
                .select("*")
                .order("nama_kolam")
                .execute()
            )
            return hasil.data if hasil.data else []
        except Exception as e:
            print("❌ Gagal ambil dashboard kolam:", e)
            return []

    # TAMBAH & HAPUS KOLAM
    def tambah_kolam(self, nama_kolam):
        try:
            from utils.session import Session

            data = {
                "nama_kolam": nama_kolam,
                "status_kolam": "Tidak Aktif",
                "id_user": Session.id_user
            }

            hasil = self.koneksi.table("kolam").insert(data).execute()
            return hasil.data[0] if hasil.data else None
        except Exception as e:
            print("❌ Gagal tambah kolam:", e)
            return None

    def hapus_kolam(self, id_kolam):
        from PySide6.QtWidgets import QMessageBox

        konfirmasi = QMessageBox.question(
            None,
            "Konfirmasi Hapus",
            "Yakin ingin menghapus kolam ini?",
            QMessageBox.Yes | QMessageBox.No
        )

        if konfirmasi != QMessageBox.Yes:
            return False, "Penghapusan dibatalkan."

        try:
            hasil = (
                self.koneksi.table("view_dashboard_kolam")
                .select("total_ikan")
                .eq("id_kolam", id_kolam)
                .execute()
            )

            if not hasil.data:
                return False, "Kolam tidak ditemukan."

            if hasil.data[0]["total_ikan"] > 0:
                return False, "Kolam masih memiliki ikan."

            self.koneksi.table("kolam").delete().eq("id_kolam", id_kolam).execute()
            return True, "Kolam berhasil dihapus."
        except Exception as e:
            return False, str(e)


    # DETAIL KOLAM
    def ambil_detail_kolam(self, id_kolam):
        try:
            hasil = (
                self.koneksi.table("detail_kolam")
                .select("*")
                .eq("id_kolam", id_kolam)
                .order("tanggal_pembaruan", desc=True)
                .execute()
            )
            return hasil.data if hasil.data else []
        except Exception as e:
            print("❌ Gagal ambil detail kolam:", e)
            return []

    def tambah_detail_kolam(self, id_kolam, jenis_ukuran, jumlah_ikan, jumlah_berat=None):
        try:
            existing = (
                self.koneksi.table("detail_kolam")
                .select("id_detail, jumlah_ikan, jumlah_berat")
                .eq("id_kolam", id_kolam)
                .maybe_single()
                .execute()
            )

            if existing and existing.data:
                stok_ikan = int(existing.data["jumlah_ikan"])
                stok_berat = float(existing.data["jumlah_berat"] or 0)

                data_update = {
                    "jumlah_ikan": stok_ikan + jumlah_ikan
                }

                if jenis_ukuran == "Ukuran 3":
                    data_update["jumlah_berat"] = stok_berat + float(jumlah_berat or 0)

                self.koneksi.table("detail_kolam") \
                    .update(data_update) \
                    .eq("id_detail", existing.data["id_detail"]) \
                    .execute()

            else:
                self.koneksi.table("detail_kolam").insert({
                    "id_kolam": id_kolam,
                    "jenis_ukuran": jenis_ukuran,
                    "jumlah_ikan": jumlah_ikan,
                    "jumlah_berat": jumlah_berat
                }).execute()

            # =============================
            # STATUS & RIWAYAT
            # =============================
            self.perbarui_status_kolam(id_kolam)

            self.tambah_riwayat(
                id_kolam=id_kolam,
                jenis_ukuran=jenis_ukuran,
                jumlah_ikan=jumlah_ikan,
                jumlah_berat=jumlah_berat,
                keterangan="Penambahan Data Ikan"
            )

            return True

        except Exception as e:
            print("❌ Gagal tambah detail kolam:", e)
            return False


    def hapus_detail_kolam(self, id_detail):
        try:
            kolam = (
                self.koneksi.table("detail_kolam")
                .select("id_kolam")
                .eq("id_detail", id_detail)
                .single()
                .execute()
            )

            id_kolam = kolam.data["id_kolam"] if kolam.data else None

            self.tambah_riwayat(
                id_kolam=id_kolam,
                jenis_ukuran="-",
                jumlah_ikan=0,
                jumlah_berat=0,
                keterangan="Data dihapus dari kolam"
            )

            self.koneksi.table("detail_kolam").delete().eq("id_detail", id_detail).execute()

            if id_kolam:
                self.perbarui_status_kolam(id_kolam)

            return True
        except Exception as e:
            print("❌ Gagal hapus detail kolam:", e)
            return False

    def hapus_detail(self, id_detail):
        return self.hapus_detail_kolam(id_detail)

    # SORTIR IKAN
    def sortir_ikan(self, id_kolam_asal, id_kolam_tujuan, jenis_ukuran, jumlah_ikan, jumlah_berat=None):
        try:
            asal = (
                self.koneksi.table("detail_kolam")
                .select("id_detail, jumlah_ikan, jumlah_berat")
                .eq("id_kolam", id_kolam_asal)
                .single()
                .execute()
            )

            if not asal.data:
                return False

            stok_ikan = int(asal.data["jumlah_ikan"])
            stok_berat = float(asal.data["jumlah_berat"] or 0)

            if stok_ikan < jumlah_ikan:
                return False

            if jenis_ukuran == "Ukuran 3":
                if jumlah_berat is None or stok_berat < float(jumlah_berat):
                    return False
                sisa_berat = stok_berat - float(jumlah_berat)
            else:
                sisa_berat = None

            self.koneksi.table("detail_kolam").update({
                "jumlah_ikan": stok_ikan - jumlah_ikan,
                "jumlah_berat": sisa_berat
            }).eq("id_detail", asal.data["id_detail"]).execute()

            tujuan = (
                self.koneksi.table("detail_kolam")
                .select("id_detail, jumlah_ikan, jumlah_berat")
                .eq("id_kolam", id_kolam_tujuan)
                .maybe_single()
                .execute()
            )

            if tujuan and tujuan.data:
                self.koneksi.table("detail_kolam").update({
                    "jumlah_ikan": tujuan.data["jumlah_ikan"] + jumlah_ikan,
                    "jumlah_berat": (
                        (tujuan.data["jumlah_berat"] or 0) + float(jumlah_berat)
                        if jenis_ukuran == "Ukuran 3" else tujuan.data["jumlah_berat"]
                    )
                }).eq("id_detail", tujuan.data["id_detail"]).execute()
            else:
                self.koneksi.table("detail_kolam").insert({
                    "id_kolam": id_kolam_tujuan,
                    "jenis_ukuran": jenis_ukuran,
                    "jumlah_ikan": jumlah_ikan,
                    "jumlah_berat": jumlah_berat
                }).execute()

            self.perbarui_status_kolam(id_kolam_asal)
            self.perbarui_status_kolam(id_kolam_tujuan)

            kolam_tujuan = (
                self.koneksi.table("kolam")
                .select("nama_kolam")
                .eq("id_kolam", id_kolam_tujuan)
                .single()
                .execute()
            )

            nama_kolam_tujuan = (
                kolam_tujuan.data["nama_kolam"]
                if kolam_tujuan and kolam_tujuan.data
                else id_kolam_tujuan
            )

            self.tambah_riwayat(
                id_kolam=id_kolam_asal,
                jenis_ukuran=jenis_ukuran,
                jumlah_ikan=jumlah_ikan,
                jumlah_berat=jumlah_berat,
                keterangan=f"Dipindahkan ke kolam {nama_kolam_tujuan}"
            )

            self.tambah_riwayat(
                id_kolam=id_kolam_tujuan,
                jenis_ukuran=jenis_ukuran,
                jumlah_ikan=jumlah_ikan,
                jumlah_berat=jumlah_berat,
                keterangan=f"Sumber dari kolam {id_kolam_asal}"
            )

            return True

        except Exception as e:
            print("❌ Gagal sortir ikan:", e)
            return False

    # STATUS OTOMATIS
    def perbarui_status_kolam(self, id_kolam):
        try:
            hasil = (
                self.koneksi.table("view_dashboard_kolam")
                .select("total_ikan")
                .eq("id_kolam", id_kolam)
                .execute()
            )
            if hasil.data:
                status = "Aktif" if hasil.data[0]["total_ikan"] > 0 else "Tidak Aktif"
                self.koneksi.table("kolam").update(
                    {"status_kolam": status}
                ).eq("id_kolam", id_kolam).execute()
        except Exception as e:
            print("⚠️ Gagal update status kolam:", e)

    # JUAL IKAN
    def jual_ikan(self, id_kolam, jumlah_ikan, jumlah_berat=None):
        try:
            detail = (
                self.koneksi.table("detail_kolam")
                .select("id_detail, jenis_ukuran, jumlah_ikan, jumlah_berat")
                .eq("id_kolam", id_kolam)
                .single()
                .execute()
            )

            if not detail.data:
                return False

            stok_ikan = detail.data["jumlah_ikan"]
            stok_berat = detail.data["jumlah_berat"] or 0
            jenis_ukuran = detail.data["jenis_ukuran"]

            if stok_ikan < jumlah_ikan:
                return False

            data_update = {
                "jumlah_ikan": stok_ikan - jumlah_ikan
            }

            if jumlah_berat is not None:
                if stok_berat < jumlah_berat:
                    return False
                data_update["jumlah_berat"] = stok_berat - jumlah_berat

            self.koneksi.table("detail_kolam") \
                .update(data_update) \
                .eq("id_detail", detail.data["id_detail"]) \
                .execute()

            self.perbarui_status_kolam(id_kolam)

            self.tambah_riwayat(
                id_kolam=id_kolam,
                jenis_ukuran=jenis_ukuran,
                jumlah_ikan=jumlah_ikan,
                jumlah_berat=jumlah_berat,
                keterangan="Terjual"
            )

            return True

        except Exception as error:
            print("❌ Gagal jual ikan:", error)
            return False

    # HAPUS IKAN
    def hapus_ikan(self, id_kolam, jumlah_ikan, jumlah_berat=None, mode="Hapus Berkala"):
        try:
            detail = (
                self.koneksi.table("detail_kolam")
                .select("id_detail, jenis_ukuran, jumlah_ikan, jumlah_berat")
                .eq("id_kolam", id_kolam)
                .single()
                .execute()
            )

            if not detail.data:
                return False

            stok_ikan = int(detail.data["jumlah_ikan"] or 0)
            stok_berat = float(detail.data["jumlah_berat"] or 0)
            jenis_ukuran = detail.data["jenis_ukuran"]


            # MODE: HAPUS SEMUA
            if mode == "Hapus Semua":
                jumlah_ikan = stok_ikan
                jumlah_berat = stok_berat if jenis_ukuran == "Ukuran 3" else None

            # VALIDASI
            if stok_ikan < jumlah_ikan:
                return False

            if jenis_ukuran == "Ukuran 3":
                if jumlah_berat is None or stok_berat < float(jumlah_berat):
                    return False

            sisa_ikan = stok_ikan - jumlah_ikan
            sisa_berat = (
                stok_berat - float(jumlah_berat)
                if jenis_ukuran == "Ukuran 3"
                else None
            )

            # UPDATE / DELETE
            if sisa_ikan <= 0:
                self.koneksi.table("detail_kolam") \
                    .delete() \
                    .eq("id_detail", detail.data["id_detail"]) \
                    .execute()
            else:
                self.koneksi.table("detail_kolam") \
                    .update({
                        "jumlah_ikan": sisa_ikan,
                        "jumlah_berat": sisa_berat
                    }) \
                    .eq("id_detail", detail.data["id_detail"]) \
                    .execute()

            # STATUS & RIWAYAT
            self.perbarui_status_kolam(id_kolam)

            self.tambah_riwayat(
                id_kolam=id_kolam,
                jenis_ukuran=jenis_ukuran,
                jumlah_ikan=jumlah_ikan,
                jumlah_berat=jumlah_berat,
                keterangan=(
                    "Dihapus Semua Ikan"
                    if mode == "Hapus Semua"
                    else "Dihapus Berkala"
                )
            )

            return True

        except Exception as error:
            print("❌ Gagal hapus ikan:", error)
            return False

    # RIWAYAT AKSI KOLAM
    def tambah_riwayat(self, id_kolam, jenis_ukuran, jumlah_ikan, jumlah_berat, keterangan):
        try:
            data = {
                "id_kolam": id_kolam,
                "jenis_ukuran": jenis_ukuran,
                "jumlah_ikan": jumlah_ikan,
                "jumlah_berat": jumlah_berat,
                "keterangan": keterangan
            }

            self.koneksi.table("riwayat_kolam").insert(data).execute()
            return True

        except Exception as error:
            print("❌ Gagal tambah riwayat:", error)
            return False

    def ambil_riwayat_per_kolam(self, id_kolam, tanggal=None):
        try:
            query = (
                self.koneksi.table("riwayat_kolam")
                .select("*")
                .eq("id_kolam", id_kolam)
            )

            if tanggal:
                query = query.gte(
                    "tanggal_aksi", f"{tanggal} 00:00:00"
                ).lte(
                    "tanggal_aksi", f"{tanggal} 23:59:59"
                )

            hasil = query.order("tanggal_aksi", desc=True).execute()
            return hasil.data if hasil.data else []
        except Exception as e:
            print("❌ Gagal ambil riwayat kolam:", e)
            return []