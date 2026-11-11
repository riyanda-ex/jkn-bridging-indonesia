# 🇮🇩 JKN Bridging Indonesia - Bridging BPJS + Semua Jaminan Nasional

[Python](https://img.shields.io/badge/Python-3.11-blue)
[Tests](https://github.com/riyanda-ex/jkn-bridging-indonesia/actions/workflows/test.yml/badge.svg)
[License](https://img.shields.io/badge/License-Apache%202.0-blue)
[Standard](https://img.shields.io/badge/Standard-BPJS%20VClaim%202.0%20%2B%20FHIR%20R4-orange)
[Status](https://img.shields.io/badge/Status-Selesai-green)
[Nasional](https://img.shields.io/badge/Indonesia-JKN%20%2B%20Jamkesda%20%2B%20Jampersal-red)

Bridging & validasi eligibilitas untuk semua jaminan kesehatan nasional Indonesia: BPJS Kesehatan JKN (PBI, Mandiri, PPU, BP, BBL), Jamkesda, Jampersal, JKK, Swasta, Umum.

Dibuat untuk Klinik Al Madina Husada, Nganjuk.

> **Disclaimer:** Alat bantu simulasi bridging & validasi administrasi. BUKAN bridging resmi BPJS. Bridging resmi WAJIB pakai credential & sertifikat dari BPJS Kesehatan. Keputusan akhir di BPJS / verifikator. Jangan kirim NIK asli tanpa enkripsi.

## 🇮🇩 Jaminan Yang Di-cover (10 Jaminan)
- **JKN-PBI** - KIS PBI, dibayar pemerintah
- **JKN-MANDIRI** - PBPU, bayar sendiri
- **JKN-PPU** - Pekerja Penerima Upah
- **JKN-BP** - Bukan Pekerja / Pensiunan
- **JKN-BBL** - Bayi Baru Lahir
- **JAMKESDA** - Jaminan Daerah APBD
- **JAMPERSAL** - Jaminan Persalinan (hanya Kandungan / Anak)
- **JKK** - BPJS Ketenagakerjaan, Kecelakaan Kerja
- **SWASTA** - Asuransi Swasta
- **UMUM** - Bayar Sendiri

## ✨ Fitur
- Validasi format NIK Indonesia 16 digit (DDMMYY + bulan + tanggal)
- Anonimisasi NIK & No. Kartu jadi hash SHA-256 (`NIK-XXXX`)
- Cek eligibilitas per jaminan: butuh SEP? butuh rujukan? butuh kartu?
- Aturan khusus: Jampersal, JKK, Jamkesda
- Mapping poli ke kode VClaim BPJS (ANA, UMU, GIG, OBG, BED, dll)
- Payload VClaim contoh siap pakai (tanpa NIK asli)
- API sederhana `api.py` untuk SIMRS / Klinik
- 20 Test Otomatis

## 🚀 Cara Pakai
```bash
python main.py
# atau
python test.py
# atau via API
python api.py
