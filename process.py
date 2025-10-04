# process.py
class Process:
    def __init__(self, pid, arrival_time, burst_time, io_burst, priority):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.io_burst = io_burst
        self.original_priority = priority # Prioritas awal (1 terendah, 3 tertinggi)
        self.current_priority = priority

        self.remaining_time = burst_time
        self.remaining_io = 0 # Waktu I/O yang tersisa
        self.in_io = False    # Status I/O
        self.wait_time = 0    # Waktu tunggu kumulatif
        self.last_run_time = 0 # Waktu terakhir proses ini dijalankan atau dikeluarkan dari CPU
        self.start_time = None
        self.completion_time = None
        self.service_time = 0 # Waktu total CPU yang sudah dihabiskan
        self.io_count = 0     # Jumlah I/O yang telah dilakukan

    def reset(self):
        self.remaining_time = self.burst_time
        self.remaining_io = 0
        self.in_io = False
        self.wait_time = 0
        self.last_run_time = 0
        self.start_time = None
        self.completion_time = None
        self.service_time = 0
        self.io_count = 0
        self.current_priority = self.original_priority # Reset prioritas

    def __repr__(self):
        return f"Process(ID={self.pid}, AT={self.arrival_time}, BT={self.burst_time}, P={self.current_priority})"
