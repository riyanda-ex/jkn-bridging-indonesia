# Keamanan - JKN Bridging Indonesia

## Jangan Laporkan Data Asli di Issue Publik
Jangan pernah upload NIK asli, No. Kartu BPJS asli, No. SEP, No. Rujukan, foto KTP / Kartu BPJS, credential VClaim, file .key / .pem / sertifikat ke GitHub Issue.

## Melaporkan Celah Keamanan
Hubungi pemilik repo melalui GitHub secara privat.
Jelaskan: file yang bermasalah, langkah reproduksi, dan dampaknya.

## Prinsip
- NIK / No. Kartu asli tidak pernah disimpan, hanya hash anonim `NIK-XXXX` / `KARTU-XXXX` (SHA-256).
- Credential BPJS asli diblokir oleh `.gitignore` (`credential_bpjs/`, `*.key`, `*.pem`).
- Payload VClaim di repo ini adalah contoh struktur, bukan request asli.
- Bridging resmi WAJIB pakai credential resmi dari BPJS Kesehatan, antrean online, dan enkripsi sesuai standar BPJS.
- Sistem ini bukan keputusan resmi BPJS. Keputusan akhir di BPJS / verifikator.
