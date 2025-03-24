import matplotlib.pyplot as plt

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=None):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.waiting_time = 0
        self.turnaround_time = 0
        self.completion_time = 0
        self.remaining_burst = burst_time  # For preemptive algorithms

def calculate_metrics(processes):
    total_waiting_time = 0
    total_turnaround_time = 0
    for process in processes:
        process.turnaround_time = process.completion_time - process.arrival_time
        process.waiting_time = process.turnaround_time - process.burst_time
        total_waiting_time += process.waiting_time
        total_turnaround_time += process.turnaround_time
    avg_waiting_time = total_waiting_time / len(processes) if processes else 0
    avg_turnaround_time = total_turnaround_time / len(processes) if processes else 0
    return avg_waiting_time, avg_turnaround_time
