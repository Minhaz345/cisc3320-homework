import threading
import queue
import time

BUFFER_SIZE = 2
NUM_PRODUCERS = 3
NUM_CONSUMERS = 3
ITEMS_PER_PRODUCER = 5

buffer = queue.Queue(maxsize=BUFFER_SIZE)
print_lock = threading.Lock()


def log(message):
    with print_lock:
        print(message)

def producer(producer_id):
    for number in range(ITEMS_PER_PRODUCER):
        item = (producer_id, number)

        buffer.put(item)
        log(f"Producer {producer_id} produced {item}")

        time.sleep(0.1)

    log(f"Producer {producer_id} finished")

def consumer(consumer_id):
    while True:
        item = buffer.get()

        if item is None:
            log(f"Consumer {consumer_id} received stop signal")
            buffer.task_done()
            break

        log(f"Consumer {consumer_id} consumed {item}")
        time.sleep(0.2)
        buffer.task_done()

def main():
    start_time = time.perf_counter()
    producers = []
    consumers = []

    for i in range(NUM_CONSUMERS):
        thread = threading.Thread(target=consumer, args=(i + 1,))
        consumers.append(thread)
        thread.start()

    for i in range(NUM_PRODUCERS):
        thread = threading.Thread(target=producer, args=(i + 1,))
        producers.append(thread)
        thread.start()

    for thread in producers:
        thread.join()

    for i in range(NUM_CONSUMERS):
        buffer.put(None)

    buffer.join()

    for thread in consumers:
        thread.join()

    elapsed = time.perf_counter() - start_time
    print("All producers and consumers finished.")
    print("Items left in buffer:", buffer.qsize())
    print(f"Elapsed time: {elapsed:.3f} seconds")


if __name__ == "__main__":
    main()

