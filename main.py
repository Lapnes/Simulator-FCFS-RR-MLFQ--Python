# main.py
from process import Process
from mlfq import mlfq_scheduler
import matplotlib.pyplot as plt
import pandas as pd
# Anda perlu menginstal FPDF: pip install fpdf
try:
    from fpdf import FPDF
except ImportError:
    print("WARNING: FPDF library not found. PDF generation functionality is disabled. Install with: pip install fpdf")
    FPDF = None

# ----------------------------------------------------------------------
# System Parameters (Sesuai Kebutuhan)
# ----------------------------------------------------------------------
TIME_QUANTUMS = [2, 4, 8] # Level 1 (terendah) = 2ms, Level 2 = 4ms, Level 3 (tertinggi) = 8ms
AGING_THRESHOLD = 10     # Aging setelah 10 time units
MAX_TIME_UNITS = 50      # Gantt chart hingga 50 time units

# Sample processes (Sesuai Kebutuhan)
# Process(pid, arrival_time, burst_time, io_burst, priority)
# Priority: 1 (terendah) sampai 3 (tertinggi)
sample_processes = [
    Process(pid="P1", arrival_time=0, burst_time=12, io_burst=3, priority=2),
    Process(pid="P2", arrival_time=1, burst_time=8, io_burst=2, priority=1),
    Process(pid="P3", arrival_time=2, burst_time=15, io_burst=4, priority=3),
    Process(pid="P4", arrival_time=3, burst_time=6, io_burst=1, priority=1),
    Process(pid="P5", arrival_time=4, burst_time=10, io_burst=3, priority=2),
]

# ----------------------------------------------------------------------
# 1) Gantt Chart Drawer
# ----------------------------------------------------------------------
def draw_gantt_chart(timeline, title="Gantt Chart"):
    # Filter timeline hingga MAX_TIME_UNITS
    timeline_filtered = [(p, s, e) for p, s, e in timeline if s < MAX_TIME_UNITS]

    fig, gnt = plt.subplots(figsize=(15, 6))
    gnt.set_title(title)
    gnt.set_xlabel("Time (ms)")
    gnt.set_ylabel("Processes")

    # Atur batas waktu
    gnt.set_xlim(0, MAX_TIME_UNITS)

    process_ids = list({item[0] for item in timeline_filtered})
    process_ids.sort()

    y_ticks = [15 + 10 * i for i in range(len(process_ids))]
    gnt.set_yticks(y_ticks)
    gnt.set_yticklabels(process_ids)
    gnt.set_ylim(0, 10 * len(process_ids) + 10)
    gnt.grid(True)

    colors = plt.cm.get_cmap("tab20", len(process_ids))

    for i, pid in enumerate(process_ids):
        y_pos = 10 * i + 10
        for start, end in [(s, min(e, MAX_TIME_UNITS)) for p, s, e in timeline_filtered if p == pid]:
            # Hanya tampilkan bar jika durasinya > 0
            if end > start:
                gnt.broken_barh([(start, end - start)], (y_pos, 8), facecolors=colors(i))

    plt.show()

# ----------------------------------------------------------------------
# 2) Dokumentasi Queue State Changes (Pretty Print)
# ----------------------------------------------------------------------
def print_queue_log(log):
    print("\n" + "="*50)
    print("2) DOKUMENTASI PERUBAHAN STATUS QUEUE (MLFQ)")
    print("="*50)
    for entry in log:
        time = entry['time']
        action = entry['action']
        process = entry['process']
        from_q = entry['from_q']
        to_q = entry['to_q']
        q_status = entry['queues']
        io_queue = entry['io_queue']

        base_msg = f"[T={time:02d}] {action}"
        if process:
            base_msg += f" - P:{process}"
        if from_q and to_q:
            base_msg += f" ({from_q} -> {to_q})"
        elif from_q:
            base_msg += f" (From {from_q})"
        elif to_q:
            base_msg += f" (To {to_q})"

        print(base_msg)
        q_str = ", ".join([f"{q}:{pids}" for q, pids in q_status.items()])
        io_str = f"IO:{io_queue}"
        print(f"      -> Current Queues: {q_str} | {io_str}")
    print("="*50)

# ----------------------------------------------------------------------
# 3) Kalkulasi Performance Metrics
# ----------------------------------------------------------------------
def calculate_metrics(processes):
    print("\n" + "="*50)
    print("3) KALKULASI PERFORMANCE METRICS")
    print("="*50)

    completed_processes = [p for p in processes if p.completion_time is not None]

    if not completed_processes:
        print("Tidak ada proses yang selesai dalam simulasi.")
        return

    metrics_data = []

    for p in completed_processes:
        # Turnaround Time (TAT) = Completion Time - Arrival Time
        tat = p.completion_time - p.arrival_time
        # Waiting Time (WT) = Turnaround Time - Burst Time (total waktu CPU) - Total waktu I/O yang dilalui saat I/O selesai
        # Dengan asumsi I/O Burst sudah dihitung secara internal oleh scheduler
        # WT yang sudah dihitung di proses.py (p.wait_time) adalah waktu tunggu di queue.
        # Mari kita hitung ulang dari formula dasar untuk WT:
        wt = tat - p.burst_time
        # Response Time (RT) = Start Time - Arrival Time
        rt = p.start_time - p.arrival_time

        metrics_data.append({
            'Process': p.pid,
            'Arrival Time': p.arrival_time,
            'Burst Time': p.burst_time,
            'Completion Time': p.completion_time,
            'Start Time': p.start_time,
            'Turnaround Time (TAT)': tat,
            'Waiting Time (WT)': wt,
            'Response Time (RT)': rt
        })

    df = pd.DataFrame(metrics_data)

    # Hitung Rata-rata
    avg_tat = df['Turnaround Time (TAT)'].mean()
    avg_wt = df['Waiting Time (WT)'].mean()
    avg_rt = df['Response Time (RT)'].mean()

    print(df.to_string(index=False))
    print(f"\nAverage Turnaround Time: {avg_tat:.2f} ms")
    print(f"Average Waiting Time: {avg_wt:.2f} ms")
    print(f"Average Response Time: {avg_rt:.2f} ms")
    print("="*50)

# ----------------------------------------------------------------------
# FUNGSI GENERASI PDF
# ----------------------------------------------------------------------
def generate_pdf_report(timeline, log, processes, output_path="output/hasil.pdf"):
    if FPDF is None:
        print("\nPDF generation skipped. FPDF not installed.")
        return

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)

    # Judul
    pdf.cell(0, 10, "Laporan Simulasi MLFQ Scheduler", 0, 1, "C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, f"Parameter: TQ={TIME_QUANTUMS}, Aging={AGING_THRESHOLD}ms, Max Time={MAX_TIME_UNITS}ms", 0, 1)

    # ----------------------------------------
    # 1) Gantt Chart
    # ----------------------------------------
    gantt_chart_filename = "gantt_chart.png"

    # Generate Gantt Chart PNG (perlu disimpan dulu)
    fig, gnt = plt.subplots(figsize=(15, 6))
    # ... (Isi dari draw_gantt_chart, tanpa plt.show()) ...
    # Salin isi draw_gantt_chart ke sini untuk menyimpan gambar

    timeline_filtered = [(p, s, e) for p, s, e in timeline if s < MAX_TIME_UNITS]
    gnt.set_title(f"1) Gantt Chart (Max Time = {MAX_TIME_UNITS}ms)")
    gnt.set_xlabel("Time (ms)")
    gnt.set_ylabel("Processes")
    gnt.set_xlim(0, MAX_TIME_UNITS)
    process_ids = list({item[0] for item in timeline_filtered})
    process_ids.sort()
    y_ticks = [15 + 10 * i for i in range(len(process_ids))]
    gnt.set_yticks(y_ticks)
    gnt.set_yticklabels(process_ids)
    gnt.set_ylim(0, 10 * len(process_ids) + 10)
    gnt.grid(True)
    colors = plt.cm.get_cmap("tab20", len(process_ids))
    for i, pid in enumerate(process_ids):
        y_pos = 10 * i + 10
        for start, end in [(s, min(e, MAX_TIME_UNITS)) for p, s, e in timeline_filtered if p == pid]:
            if end > start:
                gnt.broken_barh([(start, end - start)], (y_pos, 8), facecolors=colors(i))

    plt.savefig(gantt_chart_filename, dpi=100)
    plt.close(fig)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1) Gantt Chart", 0, 1)
    pdf.image(gantt_chart_filename, w=pdf.w - 20)
    pdf.ln(5)

    # ----------------------------------------
    # 2) Queue State Changes
    # ----------------------------------------
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2) Dokumentasi Perubahan Status Queue", 0, 1)
    pdf.set_font("Courier", "", 8)

    for entry in log:
        time = entry['time']
        action = entry['action']
        process = entry['process']
        from_q = entry['from_q']
        to_q = entry['to_q']
        q_status = entry['queues']
        io_queue = entry['io_queue']

        base_msg = f"[T={time:02d}] {action}"
        if process: base_msg += f" - P:{process}"
        if from_q and to_q: base_msg += f" ({from_q} -> {to_q})"
        elif from_q: base_msg += f" (From {from_q})"
        elif to_q: base_msg += f" (To {to_q})"

        pdf.cell(0, 4, base_msg, 0, 1)
        q_str = ", ".join([f"{q}:{','.join(pids)}" for q, pids in q_status.items()])
        io_str = f"IO:{','.join(io_queue)}"
        pdf.cell(0, 4, f"      -> Queues: {q_str} | {io_str}", 0, 1)

    # ----------------------------------------
    # 3) Performance Metrics
    # ----------------------------------------
    completed_processes = [p for p in processes if p.completion_time is not None]
    metrics_data = []
    if completed_processes:
        for p in completed_processes:
            tat = p.completion_time - p.arrival_time
            wt = tat - p.burst_time
            rt = p.start_time - p.arrival_time
            metrics_data.append({
                'Process': p.pid, 'AT': p.arrival_time, 'BT': p.burst_time, 'CT': p.completion_time,
                'ST': p.start_time, 'TAT': tat, 'WT': wt, 'RT': rt
            })
        df = pd.DataFrame(metrics_data)

        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "3) Kalkulasi Performance Metrics", 0, 1)

        # Tabel
        col_width = pdf.w / 8.5
        pdf.set_font("Arial", "B", 8)
        headers = ['Process', 'AT', 'BT', 'CT', 'ST', 'TAT', 'WT', 'RT']
        for header in headers:
            pdf.cell(col_width, 7, header, 1, 0, "C")
        pdf.ln()

        pdf.set_font("Arial", "", 8)
        for row in df.itertuples():
            for i, val in enumerate(row[1:]): # row[0] is index
                pdf.cell(col_width, 6, str(val), 1, 0, "C")
            pdf.ln()

        # Rata-rata
        pdf.ln(2)
        avg_tat = df['TAT'].mean()
        avg_wt = df['WT'].mean()
        avg_rt = df['RT'].mean()
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 5, f"Average Turnaround Time: {avg_tat:.2f} ms", 0, 1)
        pdf.cell(0, 5, f"Average Waiting Time: {avg_wt:.2f} ms", 0, 1)
        pdf.cell(0, 5, f"Average Response Time: {avg_rt:.2f} ms", 0, 1)

    # ----------------------------------------
    # 4) Comparison with Windows
    # ----------------------------------------
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "4) Perbandingan dengan Windows Task Manager Priority", 0, 1)
    pdf.set_font("Arial", "", 10)

    comparison_text = (
        "MLFQ yang disimulasikan memiliki kesamaan dengan penjadwalan Windows, yaitu penggunaan **Level Prioritas** dan bersifat **Preemptif**. "
        "Namun, ada perbedaan kunci:\n\n"
        "-> **Aging (Penuaan)**:\n"
        "   - MLFQ (Simulasi): Menerapkan Aging eksplisit (promosi) untuk mencegah starvation.\n"
        "   - Windows: Tidak ada Aging eksplisit, hanya *priority boost* sementara untuk I/O atau responsivitas.\n\n"
        "-> **Degradation (Penurunan)**:\n"
        "   - MLFQ (Simulasi): Proses yang *CPU-bound* (menggunakan TQ penuh) diturunkan prioritasnya secara sistematis.\n"
        "   - Windows: Prioritas cenderung statis atau diatur berdasarkan kebutuhan responsivitas (I/O) dan bukan karena penggunaan CPU yang berlebihan.\n"
    )

    pdf.multi_cell(0, 5, comparison_text)

    # Output file
    pdf.output(output_path, 'F')
    print(f"\nPDF Report generated successfully at: {output_path}")



# ----------------------------------------------------------------------
# Main Execution
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# Main Execution (Diubah untuk PDF dan Konsol)
# ----------------------------------------------------------------------
# ... (Proses Eksekusi di Konsol) ...
# Clone proses agar bisa direset untuk berbagai skenario (walaupun di sini hanya MLFQ)
processes_for_mlfq = [Process(p.pid, p.arrival_time, p.burst_time, p.io_burst, p.original_priority) for p in sample_processes]

print(f"Running MLFQ with 3 Queues (TQs: {TIME_QUANTUMS}, Aging: {AGING_THRESHOLD}):")
timeline_mlfq, log_mlfq = mlfq_scheduler(
    processes_for_mlfq,
    time_quantums=TIME_QUANTUMS,
    aging_threshold=AGING_THRESHOLD,
    max_time=MAX_TIME_UNITS
)

# 1) Gantt Chart (Akan muncul di window terpisah)
draw_gantt_chart(timeline_mlfq, f"1) FCFS Scheduler (Max Time = {MAX_TIME_UNITS}ms)")

# 2) Queue Log
print_queue_log(log_mlfq)

# 3) Performance Metrics
calculate_metrics(processes_for_mlfq)

# GENERASI PDF
# generate_pdf_report(timeline_mlfq, log_mlfq, processes_for_mlfq, output_path="output/hasil.pdf")

# *Catatan: Untuk menjalankan fungsi generate_pdf_report, Anda harus memastikan file .py yang lain
# (process.py, mlfq.py) sudah dimodifikasi sesuai jawaban sebelumnya dan semua library (matplotlib, pandas, fpdf) sudah terinstal.*
# ----------------------------------------------------------------------
# 4) Comparison dengan Windows Task Manager priority behavior
# ----------------------------------------------------------------------
def compare_with_windows_priority():
    print("\n" + "="*50)
    print("4) PERBANDINGAN DENGAN PERILAKU PRIORITAS WINDOWS TASK MANAGER")
    print("="*50)
    print("MLFQ (Multilevel Feedback Queue) yang disimulasikan di atas memiliki beberapa kesamaan dan perbedaan dengan penjadwalan prioritas di Windows Task Manager.")
    print("\n## Kesamaan Prinsip:")
    print("- **Prioritas Level**: Windows menggunakan prioritas diskret (misalnya, Real-time, High, Normal, Low), mirip dengan level di MLFQ (L3, L2, L1). Prioritas yang lebih tinggi mendapatkan CPU lebih dulu.")
    print("- **Preemption**: Baik MLFQ maupun Windows (dengan prioritas Real-time/High) adalah preemptif; proses dengan prioritas lebih tinggi akan segera mengambil alih CPU dari proses berprioritas lebih rendah.")

    print("\n## Perbedaan Kunci:")
    print("- **Aging (Penuaan)**:")
    print("  - **MLFQ (Simulasi)**: Menerapkan mekanisme *Aging* eksplisit (proses yang menunggu terlalu lama dipromosikan ke *queue* level lebih tinggi) untuk mencegah *starvation* (kelaparan).")
    print("  - **Windows**: Windows tidak memiliki mekanisme *Aging* eksplisit seperti ini. Proses hanya akan ditingkatkan prioritasnya *secara sementara* oleh *scheduler* jika proses itu terdeteksi berada dalam kondisi *wait* yang lama atau untuk meningkatkan responsivitas interaktif (*priority boost*). Namun, perubahan ini tidak sejelas aturan *aging* MLFQ.")
    print("- **Degradation (Penurunan)**:")
    print("  - **MLFQ (Simulasi)**: Proses yang menggunakan *time quantum* penuh akan diturunkan ke level prioritas yang lebih rendah (kecuali di level terendah), mengidentifikasi proses sebagai *CPU-bound*.")
    print("  - **Windows**: Perubahan prioritas pada Windows umumnya tidak bersifat permanen dan tidak ada 'penalti' berupa penurunan prioritas sistematis setelah menggunakan *time slice* penuh. Prioritas cenderung tetap statis atau diatur secara manual/otomatis berdasarkan kebutuhan responsivitas (I/O) dan bukan hanya karena penggunaan CPU.")
    print("- **Penanganan I/O**: Di Windows, proses yang beralih dari I/O menjadi *ready* sering menerima *priority boost* agar cepat mendapatkan CPU lagi dan terus memproses I/O berikutnya, mirip dengan proses di MLFQ yang kembali ke *queue* atas setelah I/O, untuk mendukung proses *I/O-bound*.")
    print("="*50)

compare_with_windows_priority()
