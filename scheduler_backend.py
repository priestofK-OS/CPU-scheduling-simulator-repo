import copy

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=None):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.waiting_time = 0
        self.turnaround_time = 0
        self.completion_time = 0
        self.remaining_burst = burst_time

def calculate_metrics(processes):
    if not processes:
        return 0, 0, 0, 0
    total_waiting_time = 0
    total_turnaround_time = 0
    total_burst_time = sum(p.burst_time for p in processes)
    end_time = max(p.completion_time for p in processes)
    idle_time = end_time - total_burst_time

    for process in processes:
        process.turnaround_time = process.completion_time - process.arrival_time
        process.waiting_time = process.turnaround_time - process.burst_time
        total_waiting_time += process.waiting_time
        total_turnaround_time += process.turnaround_time
    
    avg_waiting_time = total_waiting_time / len(processes)
    avg_turnaround_time = total_turnaround_time / len(processes)
    cpu_utilization = (total_burst_time / end_time) * 100 if end_time > 0 else 0
    throughput = len(processes) / end_time if end_time > 0 else 0
    
    print(f"Metrics: Wait={avg_waiting_time:.2f}, Turn={avg_turnaround_time:.2f}, CPU={cpu_utilization:.2f}%, Throughput={throughput:.4f}")
    return avg_waiting_time, avg_turnaround_time, cpu_utilization, throughput

def fcfs(processes):
    processes_copy = sorted(processes, key=lambda x: x.arrival_time)
    current_time = 0
    gantt_chart = []
    print("FCFS Execution:")
    for process in processes_copy:
        if current_time < process.arrival_time:
            current_time = process.arrival_time
        start_time = current_time
        process.completion_time = current_time + process.burst_time
        current_time = process.completion_time
        gantt_chart.append((process.pid, start_time, current_time))
        print(f"P{process.pid}: Start={start_time}, End={current_time}")
    return gantt_chart, processes_copy, *calculate_metrics(processes_copy)

def sjf(processes):
    processes_copy = sorted(processes, key=lambda x: x.arrival_time)
    current_time = 0
    ready_queue = []
    completed = []
    gantt_chart = []
    max_iterations = 1000  # Safeguard against infinite loops
    iteration = 0
    print("SJF Execution:")
    while (processes_copy or ready_queue) and iteration < max_iterations:
        arrived = [p for p in processes_copy if p.arrival_time <= current_time]
        ready_queue.extend(arrived)
        processes_copy = [p for p in processes_copy if p not in arrived]
        if not ready_queue:
            if processes_copy:  # If there are still processes, jump to next arrival
                current_time = min(p.arrival_time for p in processes_copy)
            else:
                break  # No more processes to wait for
            print(f"Idle until time {current_time}")
            continue
        shortest = min(ready_queue, key=lambda x: x.burst_time)
        ready_queue.remove(shortest)
        start_time = current_time
        shortest.completion_time = current_time + shortest.burst_time
        current_time = shortest.completion_time
        completed.append(shortest)
        gantt_chart.append((shortest.pid, start_time, current_time))
        print(f"P{shortest.pid}: Start={start_time}, End={current_time}")
        iteration += 1
    if iteration >= max_iterations:
        print("SJF: Max iterations reached, possible infinite loop!")
    return gantt_chart, completed, *calculate_metrics(completed)

def preemptive_sjf(processes):
    processes_copy = sorted(processes, key=lambda x: x.arrival_time)
    current_time = 0
    ready_queue = []
    completed = []
    gantt_chart = []
    running = None
    max_iterations = 1000  # Safeguard
    iteration = 0
    print("Preemptive SJF Execution:")
    while (processes_copy or ready_queue or running) and iteration < max_iterations:
        arrived = [p for p in processes_copy if p.arrival_time <= current_time]
        ready_queue.extend(arrived)
        processes_copy = [p for p in processes_copy if p not in arrived]
        
        if running and running.remaining_burst == 0:
            running.completion_time = current_time
            completed.append(running)
            print(f"P{running.pid} completed at {current_time}")
            running = None

        if ready_queue and not running:
            running = min(ready_queue, key=lambda x: x.remaining_burst)
            ready_queue.remove(running)
            print(f"P{running.pid} started at {current_time}")

        if running and ready_queue:
            shortest = min(ready_queue, key=lambda x: x.remaining_burst)
            if running.remaining_burst > shortest.remaining_burst:
                ready_queue.append(running)
                running = shortest
                ready_queue.remove(shortest)
                print(f"Preempted to P{running.pid} at {current_time}")

        if running:
            gantt_chart.append((running.pid, current_time, current_time + 1))
            running.remaining_burst -= 1
            print(f"P{running.pid} running: {current_time} -> {current_time + 1}")
            current_time += 1
        else:
            if processes_copy:
                current_time = min(p.arrival_time for p in processes_copy)
                print(f"Idle until {current_time}")
            else:
                break
        iteration += 1
    if iteration >= max_iterations:
        print("Preemptive SJF: Max iterations reached, possible infinite loop!")
    return gantt_chart, completed, *calculate_metrics(completed)

def round_robin(processes, quantum):
    processes_copy = copy.deepcopy(processes)
    current_time = 0
    gantt_chart = []
    queue = processes_copy[:]
    completed = []
    remaining_burst = {p.pid: p.burst_time for p in processes_copy}
    max_iterations = 1000  # Safeguard
    iteration = 0
    print(f"Round Robin Execution (Quantum={quantum}):")
    while queue and iteration < max_iterations:
        process = queue.pop(0)
        if remaining_burst[process.pid] > 0:
            start_time = current_time
            if remaining_burst[process.pid] > quantum:
                current_time += quantum
                remaining_burst[process.pid] -= quantum
                gantt_chart.append((process.pid, start_time, current_time))
                queue.append(process)
                print(f"P{process.pid}: {start_time} -> {current_time}")
            else:
                current_time += remaining_burst[process.pid]
                gantt_chart.append((process.pid, start_time, current_time))
                remaining_burst[process.pid] = 0
                process.completion_time = current_time
                completed.append(process)
                print(f"P{process.pid} completed: {start_time} -> {current_time}")
        iteration += 1
    if iteration >= max_iterations:
        print("Round Robin: Max iterations reached, possible infinite loop!")
    return gantt_chart, completed, *calculate_metrics(completed)

def priority_scheduling(processes):
    processes_copy = sorted(processes, key=lambda x: x.arrival_time)
    current_time = 0
    ready_queue = []
    completed = []
    gantt_chart = []
    max_iterations = 1000  # Safeguard
    iteration = 0
    print("Priority Scheduling Execution:")
    while (processes_copy or ready_queue) and iteration < max_iterations:
        arrived = [p for p in processes_copy if p.arrival_time <= current_time]
        ready_queue.extend(arrived)
        processes_copy = [p for p in processes_copy if p not in arrived]
        if not ready_queue:
            if processes_copy:
                current_time = min(p.arrival_time for p in processes_copy)
            else:
                break
            print(f"Idle until time {current_time}")
            continue
        highest_priority = min(ready_queue, key=lambda x: x.priority if x.priority is not None else float('inf'))
        ready_queue.remove(highest_priority)
        start_time = current_time
        highest_priority.completion_time = current_time + highest_priority.burst_time
        current_time = highest_priority.completion_time
        completed.append(highest_priority)
        gantt_chart.append((highest_priority.pid, start_time, current_time))
        print(f"P{highest_priority.pid}: Start={start_time}, End={current_time}")
        iteration += 1
    if iteration >= max_iterations:
        print("Priority Scheduling: Max iterations reached, possible infinite loop!")
    return gantt_chart, completed, *calculate_metrics(completed)

if __name__ == "__main__":
    # Test with sample processes
    processes = [
        Process(1, 0, 4, 2),
        Process(2, 1, 3, 1),
        Process(3, 2, 5, 3)
    ]
    quantum = 2

    print("\nTesting FCFS:")
    gantt, completed, wait, turn, cpu, throughput = fcfs(processes[:])
    print("\nTesting SJF:")
    sjf(processes[:])
    print("\nTesting Preemptive SJF:")
    preemptive_sjf(processes[:])
    print("\nTesting Round Robin:")
    round_robin(processes[:], quantum)
    print("\nTesting Priority Scheduling:")
    priority_scheduling(processes[:])