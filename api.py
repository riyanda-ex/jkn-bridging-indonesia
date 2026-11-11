# JKN Bridging API - V1.0 - Interface standar untuk SIMRS / Klinik
# Return selalu {success, data, error} - standar API internasional

from main import JKNBridgingIndonesia

class JKNAPI:
    def __init__(self):
        self.jkn = JKNBridgingIndonesia()

    def cek(self, nik, no_kartu, kode_jaminan, poli, tanggal=None, no_rujukan=None):
        hasil = self.jkn.cek_eligibilitas(nik, no_kartu, kode_jaminan, poli, tanggal, no_rujukan, simpan=False)
        if not hasil:
            return {"success": False, "error": "Validasi gagal, cek log ERROR.", "data": None}
        return {"success": True, "error": None, "data": hasil}

    def validasi_nik(self, nik):
        valid, pesan = self.jkn.validasi_nik_format(nik)
        return {"success": valid, "error": None if valid else pesan, "data": {"nik_anonim": self.jkn.anonymize_nik(nik), "pesan": pesan}}

if __name__ == "__main__":
    api = JKNAPI()
    print(api.cek("3201010101900001", "0001234567890", "JKN-PBI", "anak", "2026-11-11", "RUJUK-001"))
