# JKN Bridging Indonesia - V1.0 FINAL PERFECT NASIONAL
# Bridging: BPJS Kesehatan (JKN) + Jamkesda + Jampersal + JKK + Swasta + Umum
# Standar: BPJS VClaim 2.0 + FHIR R4 + ISO 8601 + Permenkes
# Keamanan: NIK / No. Kartu TIDAK PERNAH disimpan asli, hanya hash anonim.
# DISCLAIMER: Alat bantu simulasi bridging & validasi administrasi.
# BUKAN bridging resmi BPJS. Bridging resmi WAJIB pakai credential & sertifikat
# dari BPJS Kesehatan + antrean online RS. Keputusan akhir di BPJS / verifikator.
# Jangan pernah kirim NIK asli ke server tanpa enkripsi & izin.

import json
import os
import re
import hashlib
from datetime import datetime, date

class JKNBridgingIndonesia:
    def __init__(self, config_path="config.json"):
        self.config = self.load_config(config_path)
        self.jaminan_valid = self.config.get("jaminan_valid", {})
        self.faskes_valid = set(self.config.get("faskes_valid", ["1", "2", "3"]))
        self.kode_poli = self.config.get("kode_poli", {})

    def load_config(self, path):
        base = os.path.dirname(__file__)
        full = os.path.join(base, path)
        try:
            with open(full, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("WARNING: config.json tidak ditemukan, pakai aturan cadangan")
            return {
                "jaminan_valid": {"JKN-PBI": {"nama": "JKN KIS PBI", "butuh_sep": True, "butuh_rujukan": True}},
                "faskes_valid": ["1", "2", "3"],
                "kode_poli": {"anak": "ANA"}
            }

    def anonymize_nik(self, nik):
        # NIK asli 16 digit -> "NIK-XXXX" hash, tidak bisa dibalik
        if not nik or not str(nik).strip():
            return "NIK-0000"
        bersih = re.sub(r'[^0-9]', '', str(nik).strip())
        if len(bersih) != 16:
            return "NIK-INVALID"
        h = hashlib.sha256(bersih.encode('utf-8')).hexdigest()[:8].upper()
        return f"NIK-{h}"

    def anonymize_kartu(self, no_kartu):
        if not no_kartu or not str(no_kartu).strip():
            return "KARTU-0000"
        bersih = re.sub(r'[^0-9]', '', str(no_kartu).strip())
        if len(bersih) < 10:
            return "KARTU-INVALID"
        h = hashlib.sha256(bersih.encode('utf-8')).hexdigest()[:8].upper()
        return f"KARTU-{h}"

    def validasi_nik_format(self, nik):
        # Cek format NIK Indonesia 16 digit, bukan cek NIK asli ke Dukcapil
        if not nik:
            return False, "NIK kosong"
        bersih = re.sub(r'[^0-9]', '', str(nik).strip())
        if len(bersih) != 16:
            return False, "NIK harus 16 digit angka"
        # Cek tanggal lahir di NIK: digit 7-12 = DDMMYY (perempuan +40)
        try:
            tgl = int(bersih[6:8])
            bln = int(bersih[8:10])
            if not (1 <= bln <= 12):
                return False, "Bulan lahir di NIK tidak valid"
            if not (1 <= tgl <= 71):
                return False, "Tanggal lahir di NIK tidak valid"
        except ValueError:
            return False, "NIK mengandung karakter tidak valid"
        return True, "Format NIK valid (belum tentu terdaftar di Dukcapil)"

    def cek_eligibilitas(self, nik, no_kartu, kode_jaminan, kode_poli_input, tanggal_layanan=None, no_rujukan=None, simpan=True):
        # Validasi keras
        if not kode_jaminan or str(kode_jaminan).upper().strip() not in self.jaminan_valid:
            print(f"ERROR: Kode jaminan '{kode_jaminan}' tidak dikenal. Pilihan: {list(self.jaminan_valid.keys())}")
            return None
        kode_jaminan_bersih = str(kode_jaminan).upper().strip()
        info_jaminan = self.jaminan_valid[kode_jaminan_bersih]

        nik_valid, nik_pesan = self.validasi_nik_format(nik)
        if not nik_valid:
            print(f"ERROR: {nik_pesan}")
            return None

        poli_bersih = str(kode_poli_input).lower().strip() if kode_poli_input else ""
        kode_poli_vclaim = self.kode_poli.get(poli_bersih)
        if not kode_poli_vclaim:
            print(f"ERROR: Poli '{kode_poli_input}' tidak dikenal. Pilihan: {list(self.kode_poli.keys())}")
            return None

        # Tanggal layanan
        if tanggal_layanan:
            try:
                tgl_layanan = datetime.strptime(str(tanggal_layanan).strip(), "%Y-%m-%d").date()
            except ValueError:
                print("ERROR: Tanggal layanan harus YYYY-MM-DD")
                return None
            if tgl_layanan > date.today():
                print("ERROR: Tanggal layanan tidak boleh masa depan")
                return None
        else:
            tgl_layanan = date.today()

        masalah = []
        saran = []
        dokumen_wajib = []

        # Aturan per jaminan - ini inti bridging nasional
        if info_jaminan.get("butuh_sep"):
            dokumen_wajib.append("sep")
        if info_jaminan.get("butuh_rujukan"):
            dokumen_wajib.append("rujukan")
            if not no_rujukan or not str(no_rujukan).strip():
                masalah.append(f"Jaminan {kode_jaminan_bersih} WAJIB ada No. Rujukan FKTP")
                saran.append("Minta rujukan dari FKTP (Puskesmas / Klinik Pratama) sebelum ke FKRTL")
        if info_jaminan.get("butuh_kartu"):
            dokumen_wajib.append("kartu_jaminan")
            if not no_kartu or not str(no_kartu).strip():
                masalah.append(f"No. Kartu {kode_jaminan_bersih} kosong")
                saran.append("Minta foto kartu / cek Mobile JKN pasien")

        # Aturan khusus Jampersal
        if kode_jaminan_bersih == "JAMPERSAL":
            if poli_bersih not in ["kandungan", "anak"]:
                masalah.append("Jampersal hanya untuk poli Kandungan / Anak (persalinan)")
                saran.append("Cek ulang poli, Jampersal tidak berlaku untuk poli umum")
            dokumen_wajib.append("buku_kia")

        # Aturan khusus JKK (Kecelakaan Kerja)
        if kode_jaminan_bersih == "JKK":
            dokumen_wajib.append("laporan_kecelakaan_kerja")
            if not no_rujukan:
                masalah.append("JKK wajib ada laporan kecelakaan kerja dari perusahaan")
                saran.append("Minta HRD perusahaan buatkan laporan kecelakaan kerja")

        # Aturan khusus Jamkesda - cek domisili
        if kode_jaminan_bersih == "JAMKESDA":
            dokumen_wajib.append("ktp_domisili")
            saran.append("Pastikan KTP pasien sesuai domisili daerah penjamin Jamkesda")

        # Tentukan status eligibilitas
        if not masalah:
            status = "ELIGIBLE - BISA DILAYANI"
            skor = 100
            pesan_bpjs = "Lanjut buat SEP / VClaim di sistem BPJS resmi"
        elif any("WAJIB" in m for m in masalah):
            status = "BELUM ELIGIBLE - LENGKAPI DOKUMEN"
            skor = 50
            pesan_bpjs = "Jangan buat SEP dulu, lengkapi dokumen di atas"
        else:
            status = "PERLU VERIFIKASI MANUAL"
            skor = 70
            pesan_bpjs = "Hubungi verifikator BPJS / petugas jaminan"

        hasil = {
            "tanggal_cek": datetime.now().strftime("%d %B %Y %H:%M"),
            "tanggal_layanan": tgl_layanan.strftime("%Y-%m-%d"),
            "nik_anonim": self.anonymize_nik(nik),
            "no_kartu_anonim": self.anonymize_kartu(no_kartu),
            "kode_jaminan": kode_jaminan_bersih,
            "nama_jaminan": info_jaminan.get("nama", "-"),
            "kode_poli_input": poli_bersih,
            "kode_poli_vclaim": kode_poli_vclaim,
            "no_rujukan_ada": bool(no_rujukan and str(no_rujukan).strip()),
            "dokumen_wajib": sorted(set(dokumen_wajib)),
            "masalah": masalah,
            "saran": saran,
            "status": status,
            "skor_eligibilitas": skor,
            "pesan_bpjs": pesan_bpjs,
            # Payload siap kirim ke VClaim (TANPA NIK asli, hanya contoh struktur)
            "vclaim_payload_contoh": {
                "request": {
                    "t_sep": {
                        "noKartu": "[DIISI_SISTEM_RESIMI_DARI_MOBILE_JKN]",
                        "tglSep": tgl_layanan.strftime("%Y-%m-%d"),
                        "ppkPelayanan": "[KODE_FASKES_ANDA]",
                        "jnsPelayanan": "2",
                        "klsRawat": {"klsRawatHak": "3", "klsRawatNaik": "", "pembiayaan": "", "penanggungJawab": ""},
                        "noMR": "[NO_MR_ANONIM]",
                        "rujukan": {"asalRujukan": "1", "tglRujukan": tgl_layanan.strftime("%Y-%m-%d"), "noRujukan": "[NO_RUJUKAN_ANONIM]", "ppkRujukan": "[KODE_FKTP]"},
                        "poli": {"tujuan": kode_poli_vclaim, "eksekutif": "0"},
                        "catatan": f"Bridging {kode_jaminan_bersih} - {info_jaminan.get('nama','')}",
                        "diagAwal": "[KODE_ICD10]",
                        "poliEksekutif": "0",
                        "cob": {"cob": "0"},
                        "katarak": {"katarak": "0"},
                        "jaminan": {"lakaLantas": "0", "penjamin": {"penjamin": "1", "tglKejadian": "", "keterangan": "", "suplesi": {"suplesi": "0", "noSepSuplesi": "", "lokasiLaka": ""}}},
                        "skdp": {"noSurat": "", "kodeDPJP": ""},
                        "noTelp": "[NO_TELP_ANONIM]",
                        "user": "[USER_VCLAIM_ANDA]"
                    }
                }
            },
            "disclaimer": "Simulasi bridging & validasi administrasi. BUKAN bridging resmi BPJS. Keputusan akhir di BPJS Kesehatan. Jangan kirim NIK asli ke server tanpa enkripsi.",
        }

        self.tampilkan_hasil(hasil)
        if simpan:
            self.simpan_laporan(hasil)
        return hasil

    def simpan_laporan(self, hasil):
        folder = os.path.join(os.path.dirname(__file__), "laporan")
        os.makedirs(folder, exist_ok=True)
        nama_file = f"{hasil['nik_anonim']}_{hasil['kode_jaminan']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(folder, nama_file)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(hasil, f, indent=2, ensure_ascii=False)
        print(f"Laporan disimpan: {path}")

    def tampilkan_hasil(self, h):
        print("\n========== CEK ELIGIBILITAS JKN ==========")
        print(f"Tanggal Layanan: {h['tanggal_layanan']} | Jaminan: {h['kode_jaminan']} - {h['nama_jaminan']}")
        print(f"NIK Anonim: {h['nik_anonim']} | Kartu Anonim: {h['no_kartu_anonim']}")
        print(f"Poli: {h['kode_poli_input']} -> VClaim {h['kode_poli_vclaim']}")
        print(f"Status: {h['status']} | Skor: {h['skor_eligibilitas']}/100")
        print(f"Dokumen Wajib: {', '.join(h['dokumen_wajib'])}")
        if h['masalah']:
            print("Masalah:")
            for m in h['masalah']:
                print(f" - {m}")
        if h['saran']:
            print("Saran:")
            for s in h['saran']:
                print(f" - {s}")
        print(f"Pesan BPJS: {h['pesan_bpjs']}")
        print("==========================================")
        print("DISCLAIMER: Bukan bridging resmi BPJS.")

if __name__ == "__main__":
    print("=== JKN Bridging Indonesia ===")
    jkn = JKNBridgingIndonesia()
    # CONTOH SINTETIS - NIK 3201010101900001 ADALAH CONTOH, BUKAN NIK ASLI
    jkn.cek_eligibilitas("3201010101900001", "0001234567890", "JKN-PBI", "anak", "2026-11-11", "RUJUK-001")
    jkn.cek_eligibilitas("3201010101900001", "0001234567890", "JKN-MANDIRI", "umum", "2026-11-11", None)
    jkn.cek_eligibilitas("3201010101900001", "", "JAMPERSAL", "kandungan", "2026-11-11", "RUJUK-002")
    jkn.cek_eligibilitas("3201010101900001", "0001234567890", "JKK", "bedah", "2026-11-11", None)
    jkn.cek_eligibilitas("3201010101900001", "", "UMUM", "gigi", "2026-11-11", None)
