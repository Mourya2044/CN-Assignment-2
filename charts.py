import matplotlib.pyplot as plt
import numpy as np

# Data
protocols = ['Stop-and-Wait', 'Go-Back-N (10)', 'Selective Repeat']
error_conditions = ['No Error', 'Error 0.1', 'Error 0.5']

# Time taken in seconds
time_taken = [
    [0.9, 16.24, 147.0],
    [0.9, 10.0, 16.12],
    [0.9, 10.09, 20.2]
]

# Throughput in bps
throughput = [
    [8171.84, 504.58, 55.73],
    [8172.24, 1364.44, 508.28],
    [8170.89, 811.93, 405.55]
]

# Retransmission Rate in %
retransmission_rate = [
    [0.0, 11.54, 55.77],
    [0.0, 20.69, 47.73],
    [0.0, 11.54, 42.5]
]

x = np.arange(len(protocols))
width = 0.25
hatches = ['/', '\\', 'x']  # Patterns for bars

# Function to plot any metric with exact values and patterns
def plot_metric(data, ylabel, title):
    plt.figure(figsize=(10,6))
    for i, condition in enumerate(error_conditions):
        bars = plt.bar(x + i*width, [data[j][i] for j in range(3)], width, label=condition, hatch=hatches[i], edgecolor='black')
        # Add exact values on top
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, height, f'{height:.2f}', ha='center', va='bottom', fontsize=10)
    plt.ylabel(ylabel)
    plt.xticks(x + width, protocols)
    plt.title(title)
    plt.legend()
    plt.show()

# Plot each metric separately
plot_metric(time_taken, 'Time Taken (s)', 'Time Taken')
plot_metric(throughput, 'Throughput (bps)', 'Throughput')
plot_metric(retransmission_rate, 'Retransmission Rate (%)', 'Retransmission Rate')
