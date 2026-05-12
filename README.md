# Odoo 19 - PPh 21 Indonesia (TER & Progressive)

Custom Odoo 19 module untuk perhitungan PPh Pasal 21 sesuai dengan regulasi terbaru Indonesia.

## Fitur

### Master Data
- **PTKP (Penghasilan Tidak Kena Pajak)**: TK/0, TK/1, TK/2, TK/3, K/0, K/1, K/2, K/3
- **TER Category (Tarif Efektif Rata-rata)**: Kategori A, B, C
- **TER Rates**: Tabel tarif lengkap per kategori berdasarkan lapisan bruto bulanan
- **Progressive Tax Rates**: Tarif progresif Pasal 17 UU HPP (5 lapisan)

### Perhitungan PPh 21
- **TER (Januari - November)**: PPh 21 = Bruto Bulanan × TER Rate
- **Progressive (Desember / Resign)**: Perhitungan pajak final tahunan dikurangi TER yang sudah dibayar
- **Outsource**: Selalu menggunakan tarif progresif (annualized)

### Konfigurasi Karyawan
- Status PTKP per karyawan
- Tipe kontrak kerja (Tetap, Kontrak, Outsource, Tidak Tetap)
- NPWP & penalti 20% jika tidak memiliki NPWP
- Tanggal mulai & resign untuk prorata perhitungan

## Regulasi yang Digunakan

| Regulasi | Keterangan |
|----------|------------|
| PP 58 Tahun 2023 | Dasar hukum TER |
| PMK 168 Tahun 2023 | Teknis perhitungan PPh 21 TER |
| UU HPP | Tarif Progresif Pasal 17 |

## Tarif Progresif (Pasal 17 UU HPP)

| Lapisan PKP | Tarif |
|-------------|-------|
| Rp 0 - Rp 60.000.000 | 5% |
| Rp 60.000.000 - Rp 250.000.000 | 15% |
| Rp 250.000.000 - Rp 500.000.000 | 25% |
| Rp 500.000.000 - Rp 5.000.000.000 | 30% |
| > Rp 5.000.000.000 | 35% |

## Mapping TER Kategori → PTKP

| Kategori | Status PTKP |
|----------|-------------|
| A | TK/0, TK/1, K/0 |
| B | TK/2, TK/3, K/1, K/2 |
| C | K/3 |

## Alur Perhitungan

### Karyawan Tetap/Kontrak (Jan-Nov)
```
PPh 21 Bulan ini = Penghasilan Bruto Bulanan × TER Rate (%)
```

### Karyawan Tetap/Kontrak (Desember / Resign)
```
1. Hitung Total Bruto Tahunan (Jan - Des)
2. Kurangi Biaya Jabatan (5%, max Rp 500rb/bulan atau Rp 6jt/tahun)
3. Kurangi Iuran Pensiun (jika ada)
4. Kurangi PTKP → didapat PKP
5. Hitung PPh 21 Terutang Setahun (tarif progresif)
6. PPh 21 Desember = PPh 21 Terutang Setahun - Total TER sudah dipotong (Jan-Nov)
```

### Karyawan Outsource
```
1. Annualisasi Bruto Bulanan (× 12)
2. Kurangi Biaya Jabatan, PTKP → PKP
3. Hitung PPh 21 Tahunan (progresif)
4. PPh 21 Bulanan = PPh 21 Tahunan / 12
```

## Instalasi

1. Copy folder `l10n_id_pph21` ke direktori addons Odoo 19
2. Update Apps List di Odoo
3. Install module "Indonesia PPh 21 - TER & Progressive"
4. Data master (PTKP, TER rates, Progressive rates) akan otomatis ter-load

## Penggunaan

1. **Setup Karyawan**: Buka Employee → Tab "PPh 21 Tax" → Set PTKP, tipe kontrak, NPWP
2. **Buat Payslip**: Saat compute payslip, method `compute_pph21()` akan otomatis menentukan metode yang tepat
3. **Review**: Di payslip tab "PPh 21 Info" bisa dilihat detail perhitungan

## Penggunaan di Salary Rule

Untuk mengintegrasikan perhitungan PPh 21 ke dalam salary structure, tambahkan salary rule dengan Python code:

```python
# Salary Rule: PPh 21
# Code: PPH21
# Category: Deduction
result = -payslip.compute_pph21()
```

## Dependencies

- `hr_payroll`
- `hr`

## License

LGPL-3
