from collections import deque

def rr_scheduler(processes, time_quantum):
    queue = deque()
    processes = sorted(processes, key=lambda p: p.arrival_time)
    time = 0
    timeline = []
    i = 0

    while queue or i < len(processes):
        while i < len(processes) and processes[i].arrival_time <= time:
            queue.append(processes[i])
            i += 1

        if not queue:
            time = processes[i].arrival_time
            continue

        p = queue.popleft()
        if p.start_time is None:
            p.start_time = time

        execution_time = min(time_quantum, p.remaining_time)
        timeline.append((p.pid, time, time + execution_time))
        time += execution_time
        p.remaining_time -= execution_time

        while i < len(processes) and processes[i].arrival_time <= time:
            queue.append(processes[i])
            i += 1

        if p.remaining_time > 0:
            queue.append(p)
        else:
            p.completion_time = time

    return timeline
