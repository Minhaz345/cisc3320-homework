
import csv
import copy

class Process:
    def __init__(self, pid, arrival, burst, priority):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.priority = priority
        self.remaining = burst
        self.start = None
        self.finish = None


def read_workload(filename):
    processes = []

    with open(filename) as file:
        reader = csv.DictReader(file)

        for row in reader:
            p = Process(
                row["pid"],
                int(row["arrival"]),
                int(row["burst"]),
                int(row["priority"])
            )

            if p.arrival < 0 or p.burst <= 0:
                raise ValueError("Arrival must be greather than or equal to  0 and burst must be greaater than  0.")

            processes.append(p)

    if len(processes) == 0:
        raise ValueError(" workload is empty.")

    return processes


def arrival_order(p):
    return p.arrival


def fcfs_schedule(processes, quantum=None):
    time = 0
    timeline = []
    ordered = sorted(processes, key=arrival_order)

    for p in ordered :
        if time < p.arrival:
            time = p.arrival

        p.start = time
        time = time + p.burst
        p.finish = time
        p.remaining = 0

        timeline.append((p.pid, p.start, p.finish))

    return timeline
def sjf_schedule(processes, quantum=None):
    time = 0
    timeline = []
    unfinished = processes.copy()

    while unfinished:
        ready = []

        for p in unfinished:
            if p.arrival <= time:
                ready.append(p)

        if not ready:
            time = min(p.arrival for p in unfinished)
            continue

        ready.sort(key=arrival_order)
        shortest = ready[0]

        for p in ready:
            if p.burst < shortest.burst:
                shortest = p

        shortest.start = time
        time = time + shortest.burst
        shortest.finish = time
        shortest.remaining = 0

        timeline.append((shortest.pid, shortest.start, shortest.finish))
        unfinished.remove(shortest)

    return timeline

def round_robin_schedule(processes, quantum=None):
    if quantum is None:
        quantum = 4

    if quantum <= 0:
        raise ValueError("Quantum have to be greater than 0.")

    time = 0
    timeline = []
    ready = []
    upcoming = sorted(processes, key=arrival_order)

    while upcoming or ready:
        if not ready and upcoming:
            time = max(time, upcoming[0].arrival)

        while upcoming and upcoming[0].arrival <= time:
            ready.append(upcoming.pop(0))

        p = ready.pop(0)

        if p.start is None:
            p.start = time

        turn_start = time
        run_time = min(quantum, p.remaining)

        time = time + run_time
        p.remaining -= run_time

        timeline.append((p.pid, turn_start, time))

        while upcoming and upcoming[0].arrival <= time:
            ready.append(upcoming.pop(0))

        if p.remaining > 0:
            ready.append(p)
        else:
            p.finish = time

    return timeline


def priority_schedule(processes, quantum=None):
    time = 0
    timeline = []
    unfinished = processes.copy()

    while unfinished:
        ready = []

        for p in unfinished:
            if p.arrival <= time:
                ready.append(p)

        if not ready:
            time = min(p.arrival for p in unfinished)
            continue

        # Equal priorities favor earlier arrivals.
        ready.sort(key=arrival_order)
        chosen = ready[0]
        best_priority = chosen.priority - (time - chosen.arrival) // 5

        for p in ready:
            waiting = time - p.arrival
            effective_priority = p.priority - waiting // 5

            if effective_priority < best_priority:
                chosen = p
                best_priority = effective_priority

        chosen.start = time
        time += chosen.burst
        chosen.finish = time
        chosen.remaining = 0

        timeline.append((chosen.pid, chosen.start, chosen.finish))
        unfinished.remove(chosen)

    return timeline



def mlfq_schedule(processes, quantum=None):
    if quantum is None:
        quantum = 4

    if quantum <= 0:
        raise ValueError("Quantum must be greater than 0.")

    limits = [quantum, quantum * 2, quantum * 4]
    queues = [[], [], []]
    upcoming = sorted(processes, key=arrival_order)
    timeline = []
    time = 0
    used = {}

    for p in processes:
        used[p] = 0

    while upcoming or any(queues):
        if not any(queues) and upcoming:
            time = max(time, upcoming[0].arrival)

        # New processes enter the highest queue.
        while upcoming and upcoming[0].arrival <= time:
            queues[0].append(upcoming.pop(0))

        # Boost all ready processes every 50 time units.
        if time > 0 and time % 50 == 0:
            queues[0].extend(queues[1])
            queues[0].extend(queues[2])
            queues[1] = []
            queues[2] = []

            for p in queues[0]:
                used[p] = 0

        level = 0
        while not queues[level]:
            level += 1

        p = queues[level][0]

        if p.start is None:
            p.start = time

        # Run one simulated time unit.
        if timeline and timeline[-1][0] == p.pid and timeline[-1][2] == time:
            pid, start, end = timeline[-1]
            timeline[-1] = (pid, start, time + 1)
        else:
            timeline.append((p.pid, time, time + 1))

        time += 1
        p.remaining -= 1
        used[p] += 1

        if p.remaining == 0:
            p.finish = time
            queues[level].pop(0)

        elif used[p] == limits[level]:
            queues[level].pop(0)
            next_level = min(level + 1, 2)
            queues[next_level].append(p)
            used[p] = 0

    return timeline


def show_results(processes):
    total_wait = total_turnaround = total_response = 0
    print("PID arrival burst start finish waiting turnaround response")

    for p in processes:
        turnaround = p.finish - p.arrival
        waiting = turnaround - p.burst
        response = p.start - p.arrival

        total_wait = total_wait + waiting
        total_turnaround = total_turnaround + turnaround
        total_response = total_response + response

        print(
            p.pid, p.arrival, p.burst, p.start,
            p.finish, waiting, turnaround, response
        )

    count = len(processes)

    print()
    print("Average waiting", round(total_wait / count, 2))
    print("Average turnaround ", round(total_turnaround / count, 2))
    print("Average response ", round(total_response / count, 2))
    return total_wait / count, total_turnaround / count, total_response / count



def main():
    processes = read_workload("my_workload.csv")

    algorithms = [
        ("FCFS", fcfs_schedule),
        ("SJF", sjf_schedule),
        ("Round Robin", round_robin_schedule),
        ("Priority", priority_schedule),
        ("MLFQ", mlfq_schedule)    ]

    comparison = []

    for name, schedule in algorithms:
        fresh_processes = copy.deepcopy(processes)

        print("\nAlgorithm:", name)
        schedule(fresh_processes)
        averages = show_results(fresh_processes)

        comparison.append((name, averages))

    print("\nCOMPARISON REPORT")
    print(f"{'Algorithm':<15} {'Waiting':>10} {'Turnaround':>12} {'Response':>10}")

    for name, averages in comparison:
        waiting, turnaround, response = averages

        print(
            f"{name:<15} {waiting:>10.2f} "
            f"{turnaround:>12.2f} {response:>10.2f}"
        )

if __name__ == "__main__":
    main()
