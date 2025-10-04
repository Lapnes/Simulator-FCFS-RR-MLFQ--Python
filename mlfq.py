# mlfq.py
from collections import deque

def mlfq_scheduler(processes, time_quantums, aging_threshold, max_time):
    # Asumsi: time_quantums = [tq_level1, tq_level2, tq_level3]
    # Prioritas level: Level 3 (indeks 2) tertinggi, Level 1 (indeks 0) terendah.
    # Kita menggunakan indeks 0, 1, 2 untuk Level 1, 2, 3 agar sesuai dengan list time_quantums.
    NUM_QUEUES = 3
    queues = [deque() for _ in range(NUM_QUEUES)]

    # Urutkan berdasarkan waktu kedatangan
    all_processes = sorted(processes, key=lambda p: p.arrival_time)

    time = 0
    process_idx = 0
    timeline = []
    log = []

    # Antrian untuk proses yang sedang I/O
    io_queue = []

    def log_state(current_time, action, process=None, from_q=None, to_q=None):
        """Mencatat perubahan status antrian"""
        q_status = {f"L{i+1}": [p.pid for p in queues[i]] for i in range(NUM_QUEUES)}
        log.append({
            'time': current_time,
            'action': action,
            'process': process.pid if process else None,
            'from_q': from_q,
            'to_q': to_q,
            'queues': q_status,
            'io_queue': [p.pid for p in io_queue]
        })

    while time < max_time and (any(queues) or process_idx < len(all_processes) or io_queue):
        # 1. Kedatangan Proses Baru
        while process_idx < len(all_processes) and all_processes[process_idx].arrival_time <= time:
            p = all_processes[process_idx]
            # Prioritas awal P1, P2, P3 di input diubah menjadi indeks 0, 1, 2.
            # Prioritas 1 -> Index 0 (Level 1), Prioritas 2 -> Index 1 (Level 2), Prioritas 3 -> Index 2 (Level 3)
            # Level prioritas di kode ini: indeks 0=terendah (Level 1), indeks 2=tertinggi (Level 3)

            queue_index = p.current_priority - 1
            queues[queue_index].append(p)
            log_state(time, "Arrival", p, to_q=f"L{queue_index+1}")
            process_idx += 1

        # 2. Pemrosesan I/O Selesai
        for p in list(io_queue):
            if p.remaining_io <= 0:
                io_queue.remove(p)
                p.in_io = False

                # Masukkan kembali ke antrian tertinggi (Level 3) sesuai aturan umum MLFQ setelah I/O
                # Namun, untuk menjaga prioritas awal, kita kembalikan ke level prioritas awal mereka.
                # Kita akan menggunakan aturan "prioritas awal" untuk kesederhanaan.
                # Prioritas 1 -> Index 0 (Level 1), Prioritas 2 -> Index 1 (Level 2), Prioritas 3 -> Index 2 (Level 3)
                queue_index = p.original_priority - 1 # Kembali ke prioritas awal setelah I/O
                queues[queue_index].append(p)
                p.last_run_time = time
                log_state(time, "IO Complete, Requeue", p, to_q=f"L{queue_index+1}")

        # 3. Aging (Hanya untuk proses yang menunggu)
        for q_idx in range(NUM_QUEUES - 1): # Lakukan aging dari Level 1 ke Level 3
            # Iterasi di setiap proses di level
            for p in list(queues[q_idx]):
                waiting_time = time - p.last_run_time
                if waiting_time >= aging_threshold and q_idx < NUM_QUEUES - 1:
                    # Promosikan ke level yang lebih tinggi
                    queues[q_idx].remove(p)
                    new_q_idx = q_idx + 1
                    queues[new_q_idx].appendleft(p) # Sisipkan di depan
                    p.current_priority = new_q_idx + 1
                    p.last_run_time = time # Reset waktu tunggu
                    log_state(time, "Aging Promotion", p, from_q=f"L{q_idx+1}", to_q=f"L{new_q_idx+1}")

        # 4. Cari Proses untuk Dijalankan
        selected_p = None
        selected_q_idx = -1
        for q_idx in reversed(range(NUM_QUEUES)): # Cek dari antrian tertinggi (Level 3)
            if queues[q_idx]:
                selected_p = queues[q_idx].popleft()
                selected_q_idx = q_idx
                break

        if selected_p:
            p = selected_p
            if p.start_time is None:
                p.start_time = time

            # Aturan penjadwalan: Round Robin pada setiap level
            tq_index = selected_q_idx # Indeks 0, 1, atau 2
            time_quantum = time_quantums[tq_index]

            exec_time = min(time_quantum, p.remaining_time)

            start_segment = time
            end_segment = time + exec_time

            timeline.append((p.pid, start_segment, end_segment))
            time = end_segment
            p.remaining_time -= exec_time
            p.service_time += exec_time

            # Update waktu tunggu untuk proses yang lain di antrian
            for q in queues:
                for other_p in q:
                    other_p.wait_time += exec_time

            # 5. Cek I/O dan Sisa Waktu
            if p.service_time % p.burst_time == 0 and p.remaining_time == 0:
                # Proses Selesai
                p.completion_time = time
                log_state(time, "Completed", p, from_q=f"L{selected_q_idx+1}")
            elif p.service_time % (p.burst_time // (p.io_count + 1)) == 0 and p.io_burst > 0 and p.remaining_time > 0:
                # Simulasikan I/O setiap kali proses menghabiskan sebagian burst time-nya
                p.in_io = True
                p.remaining_io = p.io_burst
                p.io_count += 1
                io_queue.append(p)
                log_state(time, "IO Blocked", p, from_q=f"L{selected_q_idx+1}")
            elif p.remaining_time > 0:
                # Waktu quantum habis, masih ada sisa waktu CPU
                p.last_run_time = time

                # Degradasi (Move down) ke level prioritas yang lebih rendah (jika belum di level terendah)
                if selected_q_idx > 0:
                    new_q_idx = selected_q_idx - 1
                    queues[new_q_idx].append(p)
                    p.current_priority = new_q_idx + 1
                    log_state(time, "Quantum Exceeded, Degradation", p, from_q=f"L{selected_q_idx+1}", to_q=f"L{new_q_idx+1}")
                else:
                    # Tetap di level terendah (Level 1), Round Robin
                    queues[selected_q_idx].append(p)
                    log_state(time, "Quantum Exceeded, Requeue L1", p, from_q=f"L{selected_q_idx+1}", to_q=f"L{selected_q_idx+1}")

            # Kurangi waktu I/O untuk proses yang terblokir
            for p_io in io_queue:
                p_io.remaining_io -= (time - start_segment)

        else:
            # CPU Idle, jika masih ada proses yang akan datang atau sedang I/O
            if process_idx < len(all_processes):
                # Langsung lompat ke waktu kedatangan berikutnya
                idle_time = all_processes[process_idx].arrival_time - time
                time = all_processes[process_idx].arrival_time
                for p_io in io_queue:
                    p_io.remaining_io -= idle_time
                log_state(time, "Idle Time End")
            elif io_queue:
                # Lompat ke waktu I/O tercepat selesai
                next_io_finish = min(p.remaining_io for p in io_queue)
                time += next_io_finish
                for p_io in io_queue:
                    p_io.remaining_io -= next_io_finish
                log_state(time, "IO Time Advance")
            else:
                # Semua selesai/Tidak ada yang tersisa
                break

    return timeline, log
