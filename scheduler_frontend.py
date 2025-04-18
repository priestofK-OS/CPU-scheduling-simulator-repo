import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from scheduler_backend import Process, fcfs, sjf, preemptive_sjf, round_robin, priority_scheduling

class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CPU Scheduling Simulator")
        self.root.geometry("1200x800")
        self.processes = []
        self.results = {}

        # Apply a modern theme
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Helvetica", 10), padding=5)
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("TCheckbutton", font=("Helvetica", 10))

        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10", style="Main.TFrame")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        style.configure("Main.TFrame", background="#f0f0f0")

        # Title banner
        title_label = ttk.Label(self.main_frame, text="CPU Scheduling Simulator", font=("Helvetica", 16, "bold"), 
                                background="#4a90e2", foreground="white", padding=10)
        title_label.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Frames
        self.input_frame = ttk.LabelFrame(self.main_frame, text="Process Input", padding="10")
        self.input_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.control_frame = ttk.LabelFrame(self.main_frame, text="Scheduling Options", padding="10")
        self.control_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)
        self.output_frame = ttk.LabelFrame(self.main_frame, text="Simulation Results", padding="10")
        self.output_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

        self.main_frame.rowconfigure(2, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

        # Input Frame
        self.tree = ttk.Treeview(self.input_frame, columns=("PID", "Arrival", "Burst", "Priority"), show="headings", height=5)
        self.tree.heading("PID", text="PID")
        self.tree.heading("Arrival", text="Arrival Time")
        self.tree.heading("Burst", text="Burst Time")
        self.tree.heading("Priority", text="Priority")
        self.tree.column("PID", width=50)
        self.tree.column("Arrival", width=100)
        self.tree.column("Burst", width=100)
        self.tree.column("Priority", width=100)
        scrollbar = ttk.Scrollbar(self.input_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.input_frame.rowconfigure(0, weight=1)
        self.input_frame.columnconfigure(0, weight=1)

        ttk.Button(self.input_frame, text="Add Process", command=self.add_process).grid(row=1, column=0, pady=5, sticky="w")
        ttk.Button(self.input_frame, text="Clear Processes", command=self.clear_processes).grid(row=1, column=0, pady=5, sticky="e")

        # Control Frame
        self.algo_vars = {}
        for i, algo in enumerate(["FCFS", "SJF", "Preemptive SJF", "Round Robin", "Priority"]):
            var = tk.BooleanVar()
            ttk.Checkbutton(self.control_frame, text=algo, variable=var).grid(row=i, column=0, sticky="w", pady=2)
            self.algo_vars[algo] = var
        ttk.Label(self.control_frame, text="Quantum (for RR):").grid(row=5, column=0, sticky="w", pady=5)
        self.quantum_entry = ttk.Entry(self.control_frame, width=10)
        self.quantum_entry.grid(row=5, column=1, sticky="w")
        self.quantum_entry.insert(0, "2")
        ttk.Button(self.control_frame, text="Run Simulation", command=self.run_simulation, style="Accent.TButton").grid(row=6, column=0, columnspan=2, pady=10)
        style.configure("Accent.TButton", background="#4a90e2", foreground="white")

        # Output Frame
        self.notebook = ttk.Notebook(self.output_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        self.output_frame.rowconfigure(0, weight=1)
        self.output_frame.columnconfigure(0, weight=1)

    def add_process(self):
        pid = len(self.processes) + 1
        arrival = simpledialog.askinteger("Input", f"Arrival Time for P{pid} (non-negative):", minvalue=0, parent=self.root)
        if arrival is None:
            messagebox.showwarning("Cancelled", "Process addition cancelled at Arrival Time.")
            return
        burst = simpledialog.askinteger("Input", f"Burst Time for P{pid} (positive):", minvalue=1, parent=self.root)
        if burst is None:
            messagebox.showwarning("Cancelled", "Process addition cancelled at Burst Time.")
            return
        priority_input = simpledialog.askstring("Input", f"Priority for P{pid} (lower is higher, press Cancel to skip):", parent=self.root)
        if priority_input is None or priority_input.strip() == "":
            priority = None
        else:
            try:
                priority = int(priority_input)
                if priority < 0:
                    messagebox.showerror("Error", "Priority cannot be negative.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid priority value. Must be a non-negative integer.")
                return
        process = Process(pid, arrival, burst, priority)
        self.processes.append(process)
        self.tree.insert("", "end", values=(pid, arrival, burst, priority if priority is not None else "-"))
        messagebox.showinfo("Success", f"Process P{pid} added successfully!")

    def clear_processes(self):
        self.processes.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)

    def run_simulation(self):
        if not self.processes:
            messagebox.showerror("Error", "No processes added!")
            return
        selected_algos = [algo for algo, var in self.algo_vars.items() if var.get()]
        if not selected_algos:
            messagebox.showerror("Error", "No algorithms selected!")
            return
        try:
            quantum = int(self.quantum_entry.get())
            if quantum <= 0:
                raise ValueError("Quantum must be positive.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid quantum: {e}")
            return

        self.results.clear()
        for tab in self.notebook.winfo_children():
            tab.destroy()

        # Run only selected algorithms for individual tabs
        for algo in selected_algos:
            if algo == "FCFS":
                gantt, completed, *metrics = fcfs(self.processes[:])
            elif algo == "SJF":
                gantt, completed, *metrics = sjf(self.processes[:])
            elif algo == "Preemptive SJF":
                gantt, completed, *metrics = preemptive_sjf(self.processes[:])
            elif algo == "Round Robin":
                gantt, completed, *metrics = round_robin(self.processes[:], quantum)
            else:  # Priority
                gantt, completed, *metrics = priority_scheduling(self.processes[:])
            
            self.results[algo] = metrics
            self.create_result_tab(algo, gantt, completed, metrics)

        # Run all algorithms for comparison
        all_algorithms = ["FCFS", "SJF", "Preemptive SJF", "Round Robin", "Priority"]
        for algo in all_algorithms:
            if algo not in self.results:
                if algo == "FCFS":
                    _, _, *metrics = fcfs(self.processes[:])
                elif algo == "SJF":
                    _, _, *metrics = sjf(self.processes[:])
                elif algo == "Preemptive SJF":
                    _, _, *metrics = preemptive_sjf(self.processes[:])
                elif algo == "Round Robin":
                    _, _, *metrics = round_robin(self.processes[:], quantum)
                else:  # Priority
                    _, _, *metrics = priority_scheduling(self.processes[:])
                self.results[algo] = metrics

        self.create_comparison_tab()

    def create_result_tab(self, algo, gantt, completed, metrics):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=algo)

        # Gantt Chart
        fig, ax = plt.subplots(figsize=(5, 2))
        for pid, start, end in gantt:
            ax.barh(pid, end - start, left=start, height=0.8, color="#4a90e2")
            ax.text((start + end) / 2, pid, str(pid), ha='center', va='center', color="white")
        ax.set_xlabel("Time")
        ax.set_ylabel("PID")
        ax.set_title(f"{algo} Gantt Chart", fontsize=10)
        ax.grid(axis="x", linestyle="--", alpha=0.7)
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=0, padx=5, pady=5)

        # Process Table
        table_frame = ttk.Frame(tab)
        table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1, padx=5, pady=5)
        tree = ttk.Treeview(table_frame, columns=("PID", "Arrival", "Burst", "Completion", "Waiting", "Turnaround"), 
                            show="headings", height=5)
        tree.heading("PID", text="PID")
        tree.heading("Arrival", text="Arrival")
        tree.heading("Burst", text="Burst")
        tree.heading("Completion", text="Completion")
        tree.heading("Waiting", text="Waiting")
        tree.heading("Turnaround", text="Turnaround")
        tree.column("PID", width=50)
        tree.column("Arrival", width=80)
        tree.column("Burst", width=80)
        tree.column("Completion", width=100)
        tree.column("Waiting", width=80)
        tree.column("Turnaround", width=100)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        for p in completed:
            tree.insert("", "end", values=(p.pid, p.arrival_time, p.burst_time, p.completion_time, p.waiting_time, p.turnaround_time))

        # Metrics
        metrics_frame = ttk.Frame(tab)
        metrics_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        ttk.Label(metrics_frame, text=f"Avg Waiting: {metrics[0]:.2f}", font=("Helvetica", 10)).pack(pady=2)
        ttk.Label(metrics_frame, text=f"Avg Turnaround: {metrics[1]:.2f}", font=("Helvetica", 10)).pack(pady=2)
        ttk.Label(metrics_frame, text=f"CPU Util: {metrics[2]:.2f}%", font=("Helvetica", 10)).pack(pady=2)
        ttk.Label(metrics_frame, text=f"Throughput: {metrics[3]:.4f}", font=("Helvetica", 10)).pack(pady=2)
        ttk.Button(metrics_frame, text="Export Chart", command=lambda: fig.savefig(f"{algo}_gantt.png")).pack(pady=5)

    def create_comparison_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Comparison")

        # Comparison Frame
        comparison_frame = ttk.Frame(tab)
        comparison_frame.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

        # Header
        ttk.Label(comparison_frame, text="Algorithm Comparison", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=6, pady=5)
        ttk.Label(comparison_frame, text="Algorithm", font=("Helvetica", 10, "bold")).grid(row=1, column=0, sticky="w", padx=5)
        ttk.Label(comparison_frame, text="Avg Waiting", font=("Helvetica", 10, "bold")).grid(row=1, column=1, sticky="w", padx=5)
        ttk.Label(comparison_frame, text="Avg Turnaround", font=("Helvetica", 10, "bold")).grid(row=1, column=2, sticky="w", padx=5)
        ttk.Label(comparison_frame, text="CPU Util (%)", font=("Helvetica", 10, "bold")).grid(row=1, column=3, sticky="w", padx=5)
        ttk.Label(comparison_frame, text="Throughput", font=("Helvetica", 10, "bold")).grid(row=1, column=4, sticky="w", padx=5)
        ttk.Label(comparison_frame, text="Optimal", font=("Helvetica", 10, "bold")).grid(row=1, column=5, sticky="w", padx=5)

        # Determine the optimal algorithm
        optimal_algo = min(self.results, key=lambda algo: self.results[algo][0] + self.results[algo][1])
        
        # Data for all algorithms
        all_algorithms = ["FCFS", "SJF", "Preemptive SJF", "Round Robin", "Priority"]
        for i, algo in enumerate(all_algorithms):
            wait, turn, cpu, throughput = self.results[algo]
            is_optimal = algo == optimal_algo
            optimality_text = "Yes" if is_optimal else "No"
            ttk.Label(comparison_frame, text=algo).grid(row=i+2, column=0, sticky="w", padx=5, pady=2)
            ttk.Label(comparison_frame, text=f"{wait:.2f}").grid(row=i+2, column=1, sticky="w", padx=5, pady=2)
            ttk.Label(comparison_frame, text=f"{turn:.2f}").grid(row=i+2, column=2, sticky="w", padx=5, pady=2)
            ttk.Label(comparison_frame, text=f"{cpu:.2f}").grid(row=i+2, column=3, sticky="w", padx=5, pady=2)
            ttk.Label(comparison_frame, text=f"{throughput:.4f}").grid(row=i+2, column=4, sticky="w", padx=5, pady=2)
            ttk.Label(comparison_frame, text=optimality_text, foreground="green" if is_optimal else "red").grid(row=i+2, column=5, sticky="w", padx=5, pady=2)

    def save_results(self):
        with open("scheduling_results.txt", "w") as f:
            for algo, metrics in self.results.items():
                f.write(f"{algo}:\n")
                f.write(f"  Avg Waiting Time: {metrics[0]}\n")
                f.write(f"  Avg Turnaround Time: {metrics[1]}\n")
                f.write(f"  CPU Utilization: {metrics[2]:.2f}%\n")
                f.write(f"  Throughput: {metrics[3]:.4f}\n\n")
        messagebox.showinfo("Success", "Results saved to 'scheduling_results.txt'")

if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()