# l10n_id_hr_payroll

`l10n_id_hr_payroll` adalah fondasi awal addon **Odoo 19 Community** untuk payroll Indonesia.

## Cakupan awal

Addon ini menyiapkan pondasi Odoo-style untuk:
- ekstensi **employee** dan **contract**
- scaffold **payroll structure** dan **payroll rules**
- konfigurasi awal **BPJS**
- konfigurasi awal **PPh21 / PTKP / NPWP**
- konfigurasi awal **THR**

Referensi bisnis diambil dari konsep payroll Indonesia yang umum dipakai dan dari proyek ERPNext `IMOGI-ITB/Payroll-Indonesia`, tetapi implementasi di sini **bukan port literal**. Struktur data disesuaikan ke arsitektur addon Odoo.

## Yang ditambahkan

- field payroll Indonesia pada `hr.employee`
  - NIK
  - NPWP dan nama NPWP
  - status PTKP
  - metode pajak/payroll notes
  - partisipasi dan nomor BPJS
- field payroll Indonesia pada `hr.contract`
  - tunjangan tetap
  - deduction/override payroll lokal
  - preferensi THR
  - catatan payroll kontrak
- model baru untuk foundation payroll lokal:
  - `l10n_id.payroll.settings`
  - `l10n_id.payroll.structure`
  - `l10n_id.payroll.rule`
- views, menu, access rights, dan contoh data struktur payroll awal

## Status implementasi

Modul ini **installable sebagai fondasi data dan konfigurasi**, tetapi **belum merupakan implementasi legal/statutory penuh**. Beberapa area masih sengaja dibuat sebagai scaffold:

- formula PPh21 belum final dan belum menangani semua skenario regulasi
- kontribusi BPJS belum dihitung otomatis oleh engine payslip
- THR baru disiapkan sebagai struktur data dan rule placeholder
- belum ada integrasi penuh ke engine payroll Odoo Enterprise / OCA payroll
- belum ada e-filing, bukti potong, atau pelaporan resmi

## Asumsi desain

Karena targetnya **Odoo 19 Community**, addon ini fokus pada model, konfigurasi, dan struktur rule yang aman dipasang sebagai basis pengembangan berikutnya. Formula python di rule disimpan sebagai **developer guidance**, bukan dieksekusi oleh engine dalam modul ini.

## Setup singkat

1. Letakkan addon ini di path addons Odoo.
2. Update app list.
3. Install modul **Indonesia Payroll Foundation**.
4. Buka menu **Employees > Indonesian Payroll** untuk meninjau settings, structure, dan rules.
5. Lengkapi field payroll Indonesia pada employee dan contract sebelum melanjutkan pengembangan formula.

## Next steps yang disarankan

1. Tambahkan engine perhitungan payslip yang kompatibel dengan stack payroll yang dipilih.
2. Finalisasi formula PPh21 bulanan/tahunan sesuai regulasi yang berlaku.
3. Tambahkan perhitungan BPJS employer/employee yang dapat dikonfigurasi per company.
4. Tambahkan workflow THR prorata dan eligibility berdasarkan masa kerja.
5. Tambahkan test coverage Odoo untuk skenario master data dan kalkulasi.
