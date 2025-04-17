import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from scheduler_backend import Process, fcfs, sjf, preemptive_sjf, round_robin, priority_scheduling
