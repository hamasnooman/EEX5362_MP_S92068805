import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("simulation_results.csv")

plt.figure()
plt.bar(df["scenario"], df["avg_wait_min"])
plt.xticks(rotation=25, ha="right")
plt.ylabel("Average waiting time (min)")
plt.tight_layout()
plt.savefig("avg_wait.png", dpi=200)

plt.figure()
plt.bar(df["scenario"], df["avg_queue_len"])
plt.xticks(rotation=25, ha="right")
plt.ylabel("Average queue length")
plt.tight_layout()
plt.savefig("avg_queue.png", dpi=200)

plt.figure()
plt.bar(df["scenario"], df["utilization"])
plt.xticks(rotation=25, ha="right")
plt.ylabel("Utilization")
plt.tight_layout()
plt.savefig("utilization.png", dpi=200)

print("Saved: avg_wait.png, avg_queue.png, utilization.png")
