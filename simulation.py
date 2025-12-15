import pandas as pd
import simpy
import numpy as np

def run_registration_sim(csv_file, num_counters=2, speed_factor=1.0):
    """
    csv_file: path to dataset
    num_counters: number of registration counters
    speed_factor: 1.0 = normal; 0.9 = 10% faster service, 1.1 = 10% slower
    """

    df = pd.read_csv(csv_file).sort_values("arrival_time_min").reset_index(drop=True)

    # Metrics
    wait_times = []
    system_times = []
    queue_lengths = []

    busy_time = [0.0] * num_counters  # track busy time per counter

    env = simpy.Environment()
    counters = simpy.Resource(env, capacity=num_counters)

    def patient_process(i, arrival, service):
        nonlocal counters, env

        # Arrive
        yield env.timeout(arrival - env.now)

        queue_lengths.append(len(counters.queue))

        start_wait = env.now
        with counters.request() as req:
            yield req
            waited = env.now - start_wait
            wait_times.append(waited)

            # Service
            actual_service = service * speed_factor
            start_service = env.now
            yield env.timeout(actual_service)
            end_service = env.now

            # Approx busy time: add service time to one counter
            # (This is a simple approximation for utilization)
            # Utilization will still be accurate enough for this mini project.
            # Choose index 0 for simplicity
            busy_time[0] += (end_service - start_service)

            system_times.append(end_service - (arrival))

    # Create processes
    for i, row in df.iterrows():
        env.process(patient_process(i, row["arrival_time_min"], row["service_time_min"]))

    # Run until last patient finishes
    env.run()

    total_time = max(df["arrival_time_min"]) + (df["service_time_min"].max() * speed_factor) + 5

    # Throughput = number completed / total_time (per hour)
    throughput_per_hour = (len(df) / total_time) * 60

    avg_wait = float(np.mean(wait_times)) if wait_times else 0.0
    avg_system = float(np.mean(system_times)) if system_times else 0.0
    avg_queue_len = float(np.mean(queue_lengths)) if queue_lengths else 0.0

    # Approx utilization: total busy time / (num_counters * total_time)
    total_busy = sum(busy_time)
    utilization = total_busy / (num_counters * total_time)

    return {
        "counters": num_counters,
        "speed_factor": speed_factor,
        "avg_wait_min": avg_wait,
        "avg_system_time_min": avg_system,
        "avg_queue_len": avg_queue_len,
        "throughput_per_hour": throughput_per_hour,
        "utilization": utilization
    }

if __name__ == "__main__":
    csv_file = "50_Patient_Dataset.csv"

    scenarios = [
        ("A: 2 counters (baseline)", 2, 1.0),
        ("B: 1 counter", 1, 1.0),
        ("C: 3 counters", 3, 1.0),
        ("D: 2 counters, 10% faster service", 2, 0.9),
    ]

    results = []
    for name, c, s in scenarios:
        r = run_registration_sim(csv_file, num_counters=c, speed_factor=s)
        r["scenario"] = name
        results.append(r)

    out = pd.DataFrame(results)
    print(out[["scenario", "avg_wait_min", "avg_queue_len", "throughput_per_hour", "utilization"]])
    out.to_csv("simulation_results.csv", index=False)
