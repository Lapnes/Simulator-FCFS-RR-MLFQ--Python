====================================================================================================

# 🧠 Simulator Penjadwalan CPU (FCFS, RR, MLFQ)

==================================================================================
**_Create by.Ragil Amirzaky (alias Tenzly) | Dibantu oleh Gemini dan ChatGPT_**
==================================================================================
Github: https://github.com/Lapnes/Simulator-FCFS-RR-MLFQ--Python
====================================================================================================

**Simulator Python modular** untuk memvisualisasikan **Algoritma Penjadwalan CPU** klasik:

- ✅ First-Come, First-Served (FCFS)
- 🔁 Round Robin (RR)
- 🪜 Multi-Level Feedback Queue (MLFQ)

---

## 📚 Deskripsi Proyek

Proyek ini adalah implementasi simulator penjadwalan CPU berbasis Python yang modular. Tujuannya adalah memenuhi **Ujian Tengah Semester (UTS) mata kuliah Sistem Operasi Soal No. 5** dengan fokus pada skema penjadwalan kompleks.

Simulasi ini meniru perilaku sistem operasi nyata dengan:

- Menerima set proses kustom (waktu kedatangan, _CPU burst_, _I/O burst_, dan prioritas).
- Menjalankan proses melalui algoritma penjadwalan yang berbeda.
- Menganalisis performa sistem.

---

## ⚙️ Environment Eksekusi

Lingkungan yang dibutuhkan untuk menjalankan dan menghasilkan laporan dari simulator ini.

| Komponen           | Detail                                                                                                                 |
| :----------------- | :--------------------------------------------------------------------------------------------------------------------- |
| **Sistem Operasi** | Windows 10/11, macOS, atau Linux.                                                                                      |
| **Bahasa**         | **Python 3.x** (disarankan 3.10+).                                                                                     |
| **Dependensi**     | Pustaka wajib diinstal via `pip`: **`matplotlib`** (Gantt Chart), **`pandas`** (Metrik), dan **`fpdf`** (Laporan PDF). |

---

## 🧠 Environment Simulasi MLFQ (Sesuai `main.py`)

Simulasi ini dijalankan berdasarkan parameter ketat yang ditentukan di `main.py` untuk menguji perilaku _scheduler_ MLFQ terhadap _workload_ spesifik.

### 1. Parameter Scheduler

| Parameter Sistem      | Nilai                                 | Tujuan dalam Simulasi                                                                |
| :-------------------- | :------------------------------------ | :----------------------------------------------------------------------------------- |
| **Jumlah Queue**      | **3 Level**                           | L3 (Tertinggi), L2, dan L1 (Terendah).                                               |
| **Time Quantum (TQ)** | L3: **8ms**, L2: **4ms**, L1: **2ms** | TQ paling pendek di Level 1, TQ terpanjang di Level 3.                               |
| **Aging Threshold**   | **10ms**                              | Waktu tunggu sebelum proses di level bawah **dipromosikan** (mencegah _starvation_). |
| **Gantt Chart Limit** | **50ms**                              | Durasi maksimum yang divisualisasikan.                                               |

### 2. Set Proses (_Workload_)

| Process (PID) | Arrival Time (AT) | CPU Burst (BT) | I/O Burst (IO) | Prioritas Awal |
| :-----------: | :---------------: | :------------: | :------------: | :------------: |
|    **P1**     |        0ms        |      12ms      |      3ms       |       2        |
|    **P2**     |        1ms        |      8ms       |      2ms       |       1        |
|    **P3**     |        2ms        |      15ms      |      4ms       |       3        |
|    **P4**     |        3ms        |      6ms       |      1ms       |       1        |
|    **P5**     |        4ms        |      10ms      |      3ms       |       2        |

---

## ✨ Fitur Utama (Fokus UTS No. 5)

Implementasi MLFQ ini menyoroti konsep-konsep sistem operasi tingkat lanjut:

1.  **Mekanisme Aging:** Proses menunggu $\ge 10ms$ akan **dipromosikan** prioritasnya.
2.  **Degradasi Prioritas:** Proses yang menghabiskan TQ diturunkan levelnya (penalti untuk _CPU-bound_).
3.  **Simulasi I/O:** Proses meninggalkan CPU untuk I/O dan kembali ke _ready queue_.
4.  **Output Analitis Komprehensif:** Menyediakan Gantt Chart, Queue Log, Performance Metrics, dan Perbandingan Windows.

---

## 📊 Output Utama yang Dihasilkan

- **Gantt Chart** Visualisasi.
- **Dokumentasi Status Queue** (Log detail setiap _Promotion_, _Degradation_, dan _Blocking_).
- **Performance Metrics** (Rata-rata TAT, WT, dan RT).
- **Perbandingan Windows** (Analisis komparatif MLFQ vs. Windows Priority).

---

## 🚀 Cara Menjalankan

1.  **Persyaratan:** Pastikan library yang dibutuhkan telah terinstal.
    ```bash
    pip install matplotlib pandas fpdf
    ```
2.  **Eksekusi:** Jalankan file utama:
    ```bash
    python .\main.py
    ```
    _(Output log dan metrik akan dicetak di konsol, dan Gantt Chart akan muncul di jendela terpisah.)_
