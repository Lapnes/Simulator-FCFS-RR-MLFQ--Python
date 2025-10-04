def fcfs_scheduler(processes):
    processes.sort(key=lambda p: p.arrival_time)
    current_time = 0
    timeline = []

    for p in processes:
        if current_time < p.arrival_time:
            current_time = p.arrival_time
        start = current_time
        end = start + p.burst_time
        timeline.append((p.pid, start, end))
        current_time = end
        p.completion_time = end

    return timeline
