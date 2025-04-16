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
