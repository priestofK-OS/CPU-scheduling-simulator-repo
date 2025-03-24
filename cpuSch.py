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

def fcfs(processes):
    processes_copy = sorted(processes, key=lambda x: x.arrival_time)
    current_time = 0
    gantt_chart = []
    for process in processes_copy:
        if current_time < process.arrival_time:
            current_time = process.arrival_time
        process.completion_time = current_time + process.burst_time
        current_time = process.completion_time
        gantt_chart.append((process.pid, current_time - process.burst_time, current_time))
    avg_waiting_time, avg_turnaround_time = calculate_metrics(processes_copy)
    return gantt_chart, avg_waiting_time, avg_turnaround_time, processes_copy

def sjf(processes):
    processes_copy = sorted(processes, key=lambda x: x.arrival_time)
    current_time = 0
    ready_queue = []
    completed = []
    gantt_chart = []

    while processes_copy or ready_queue:
        arrived = [p for p in processes_copy if p.arrival_time <= current_time]
        ready_queue.extend(arrived)
        processes_copy = [p for p in processes_copy if p not in arrived]

        if not ready_queue:
            current_time += 1
            continue

        shortest = min(ready_queue, key=lambda x: x.burst_time)
        ready_queue.remove(shortest)
        shortest.completion_time = current_time + shortest.burst_time
        current_time = shortest.completion_time
        completed.append(shortest)
        gantt_chart.append((shortest.pid, current_time - shortest.burst_time, current_time))

    avg_waiting_time, avg_turnaround_time = calculate_metrics(completed)
    return gantt_chart, avg_waiting_time, avg_turnaround_time, completed
    def get_processes_from_user():
    processes = []
    while True:
        try:
            num_processes = int(input("Enter the number of processes: "))
            break
        except ValueError:
            print("Invalid input. Please enter an integer.")

    priority_involved = input("Are priorities involved? (yes/no): ").lower() == 'yes'

    for i in range(num_processes):
        pid = i + 1
        while True:
            try:
                arrival_time = int(input(f"Enter arrival time for process {pid}: "))
                break
            except ValueError:
                print("Invalid arrival time. Please enter an integer.")
        while True:
            try:
                burst_time = int(input(f"Enter burst time for process {pid}: "))
                break
            except ValueError:
                print("Invalid burst time. Please enter an integer.")

        if priority_involved:
            while True:
                priority_input = input(f"Enter priority for process {pid}: ")
                try:
                    priority = int(priority_input)
                    break
                except ValueError:
                    print("Invalid priority. Please enter an integer.")
        else:
            priority = None

        processes.append(Process(pid, arrival_time, burst_time, priority))
    return processes
