import multiprocessing
import time

BUFFER_SIZE = 2
NUM_PRODUCERS = 3
NUM_CONSUMERS = 3
ITEMS_PER_PRODUCER = 5


def log(message, print_lock):
    with print_lock:
        print(message, flush=True)

def producer(producer_id, buffer, print_lock):
    for number in range(ITEMS_PER_PRODUCER):
        item = (producer_id, number)

        buffer.put(item)
        log(f"Producer {producer_id} produced {item}", print_lock)

        time.sleep(0.1)

    log(f"Producer {producer_id} finished", print_lock)

def consumer(consumer_id, buffer, print_lock):
    while True:
        item = buffer.get()

        if item is None:
            log(f"Consumer {consumer_id} received stop signal", print_lock)
            buffer.task_done()
            break

        log(f"Consumer {consumer_id} consumed {item}", print_lock)
        time.sleep(0.2)
        buffer.task_done()

def main():
    start_time = time.perf_counter()
    buffer = multiprocessing.JoinableQueue(maxsize=BUFFER_SIZE)
    print_lock = multiprocessing.Lock()

    producers = []
    consumers = []

    for i in range(NUM_CONSUMERS):
        process = multiprocessing.Process(
            target=consumer,
            args=(i + 1, buffer, print_lock)
        )
        consumers.append(process)
        process.start()

    for i in range(NUM_PRODUCERS):
        process = multiprocessing.Process(
            target=producer,
            args=(i + 1, buffer, print_lock)
        )
        producers.append(process)
        process.start()

    for process in producers:
        process.join()

    for i in range(NUM_CONSUMERS):
        buffer.put(None)

    buffer.join()

    for process in consumers:
        process.join()

    buffer.close()
    buffer.join_thread()

    elapsed = time.perf_counter() - start_time
    print("All producers and consumers finished.")
    print(f"Elapsed time: {elapsed:.3f} seconds")


if __name__ == "__main__":
    main()


