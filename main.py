import numpy as np
import threading
import time
import curses

progress_lock = threading.Lock()
progress = {}
stop_flag = False


def worker_function(index):
    alt = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
    full = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    alt_num = 0
    full_num = 0
    for i in range(10000000):
        with progress_lock:
            progress[index] = i
        rand = np.random.randint(0, high=2, size=10)
        if np.array_equal(rand, alt):
            alt_num += 1
        if np.array_equal(rand, full):
            full_num += 1
    return alt_num, full_num


def monitor_function(stdscr):
    global stop_flag
    while not stop_flag:
        with progress_lock:
            for thread_index, iteration in progress.items():
                stdscr.addstr(
                    thread_index, 0, f"Thread {thread_index} iteration: {iteration}"
                )
        time.sleep(0.01)
        stdscr.refresh()


def main(stdscr):
    threads = list()
    results = list()
    for index in range(10):
        x = threading.Thread(
            target=lambda q, arg1: q.append(worker_function(arg1)),
            args=(results, index),
        )
        threads.append(x)
        x.start()

    monitor_thread = threading.Thread(target=monitor_function, args=(stdscr,))
    monitor_thread.start()

    for index, thread in enumerate(threads):
        thread.join()  # Wait for all worker threads to finish

    global stop_flag
    stop_flag = True

    monitor_thread.join()  # Wait for the monitor thread to finish

    for result in results:
        stdscr.addstr(11, 0, f"Number of alt: {result[0]}")
        stdscr.addstr(12, 0, f"Number of full: {result[1]}")
    stdscr.refresh()
    stdscr.getkey()


curses.wrapper(main)
