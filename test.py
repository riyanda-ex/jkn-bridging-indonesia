# Test otomatis - JKN Bridging Indonesia V1.0
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from main import JKNBridgingIndonesia
from api import JKNAPI

def test(nama, kondisi):
    print(f"{'✅' if kondisi else '❌'} {nama}")
    return kondisi

NIK_CONTOH = "3201010101900001"

if __name__ == "__main__":
    print("=== TEST JKN Bridging Indonesia ===\n")
    j = JKNBridgingIndonesia()
    hasil = []

    r1 = j.cek_eligibilitas(NIK_CONTOH, "0001234567890", "JKN-PBI", "anak", "2026-11-11", "RUJUK-001", simpan=False)
    hasil.append(test("1. JKN-PBI + rujukan -> ELIGIBLE", r1 is not None and "ELIGIBLE" in r1["status"] and r1["skor_eligibilitas"] == 100))
    r2 = j.cek_eligibilitas(NIK_CONTOH, "0001234567890", "JKN-MANDIRI", "umum", "2026-11-11", None, simpan=False)
    hasil.append(test("2. JKN tanpa rujukan -> BELUM ELIGIBLE", r2 is not None and "BELUM ELIGIBLE" in r2["status"]))
    r3 = j.cek_eligibilitas(NIK_CONTOH, "", "JAMPERSAL", "kandungan", "2026-11-11", "RUJUK-002", simpan=False)
    hasil.append(test("3. Jampersal kandungan -> ELIGIBLE", r3 is not None and "ELIGIBLE" in r3["status"] and "buku_kia" in r3["dokumen_wajib"]))
    r4 = j.cek_eligibilitas(NIK_CONTOH, "", "JAMPERSAL", "gigi", "2026-11-11", "RUJUK-002", simpan=False)
    hasil.append(test("4. Jampersal poli gigi ditolak aturan", r4 is not None and len(r4["masalah"]) >= 1))
    r5 = j.cek_eligibilitas(NIK_CONTOH, "0001234567890", "JKK", "bedah", "2026-11-11", None, simpan=False)
    hasil.append(test("5. JKK wajib laporan kecelakaan", r5 is not None and "laporan_kecelakaan_kerja" in r5["dokumen_wajib"]))
    r6 = j.cek_eligibilitas(NIK_CONTOH, "", "UMUM", "gigi", "2026-11-11", None, simpan=False)
    hasil.append(test("6. UMUM tanpa kartu tetap ELIGIBLE", r6 is not None and "ELIGIBLE" in r6["status"]))
    r7 = j.cek_eligibilitas("123", "0001234567890", "JKN-PBI", "anak", "2026-11-11", "RUJUK-001", simpan=False)
    hasil.append(test("7. NIK 3 digit ditolak", r7 is None))
    r8 = j.cek_eligibilitas(NIK_CONTOH, "0001234567890", "JAMINAN-NGAWUR", "anak", "2026-11-11", "RUJUK-001", simpan=False)
    hasil.append(test("8. Jaminan tidak dikenal ditolak", r8 is None))
    r9 = j.cek_eligibilitas(NIK_CONTOH, "0001234567890", "JKN-PBI", "poli-ngawur", "2026-11-11", "RUJUK-001", simpan=False)
    hasil.append(test("9. Poli tidak dikenal ditolak", r9 is None))
    r10 = j.cek_eligibilitas(NIK_CONTOH, "0001234567890", "JKN-PBI", "anak", "2030-01-01", "RUJUK-001", simpan=False)
    hasil.append(test("10. Tanggal masa depan ditolak", r10 is None))
    hasil.append(test("11. NIK dianonimkan, NIK asli tidak tersimpan", r1["nik_anonim"].startswith("NIK-") and NIK_CONTOH not in str(r1)))
    hasil.append(test("12. Kartu dianonimkan", r1["no_kartu_anonim"].startswith("KARTU-")))
    hasil.append(test("13. Mapping poli VClaim benar ANA", r1["kode_poli_vclaim"] == "ANA"))
    hasil.append(test("14. Payload VClaim ada, tanpa NIK asli", "vclaim_payload_contoh" in r1 and NIK_CONTOH not in str(r1["vclaim_payload_contoh"])))
    hasil.append(test("15. Disclaimer ada", "bukan bridging resmi" in r1["disclaimer"].lower()))
    api = JKNAPI()
    api_ok = api.cek(NIK_CONTOH, "0001234567890", "JKN-PBI", "anak", "2026-11-11", "RUJUK-001")
    hasil.append(test("16. API cek berhasil", api_ok["success"] is True))
    api_gagal = api.cek("123", "0001234567890", "JKN-PBI", "anak", "2026-11-11", "RUJUK-001")
    hasil.append(test("17. API gagal return success False", api_gagal["success"] is False))
    hasil.append(test("18. Validasi NIK format jalan", j.validasi_nik_format(NIK_CONTOH)[0] is True))
    hasil.append(test("19. Config 10 jaminan terload", len(j.jaminan_valid) == 10))
    r20 = j.cek_eligibilitas(NIK_CONTOH, "0001234567890", "JAMKESDA", "dalam", "2026-11-11", "RUJUK-003", simpan=False)
    hasil.append(test("20. Jamkesda butuh KTP domisili", r20 is not None and "ktp_domisili" in r20["dokumen_wajib"]))

    lulus = sum(hasil)
    print(f"\nHASIL: {lulus}/{len(hasil)} lulus")
    if lulus == len(hasil):
        print("🎉 SEMUA TEST LULUS!")
    else:
        print("⚠️ Ada test gagal, cek di atas.")
        sys.exit(1)
