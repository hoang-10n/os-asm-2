import time
from clockmmu import ClockMMU
from lrummu import LruMMU
from randmmu import RandMMU

def run_simulation(input_file, frames, replacement_mode):
    PAGE_OFFSET = 12  # page is 2^12 = 4KB

    if replacement_mode == "rand":
        mmu = RandMMU(frames)
    elif replacement_mode == "lru":
        mmu = LruMMU(frames)
    elif replacement_mode == "clock":
        mmu = ClockMMU(frames)
    else:
        print("Invalid replacement mode. Valid options are [rand, lru, clock]")
        return

    mmu.reset_debug()

    no_events = 0
    start_time = time.time()  # Start the timer

    with open(input_file, 'r') as trace_file:
        for trace_line in trace_file:
            trace_cmd = trace_line.strip().split(" ")
            logical_address = int(trace_cmd[0], 16)
            page_number = logical_address >>  PAGE_OFFSET

            # Process read or write
            if trace_cmd[1] == "R":
                mmu.read_memory(page_number)
            elif trace_cmd[1] == "W":
                mmu.write_memory(page_number)
            else:
                print(f"Badly formatted file. Error on line {no_events + 1}")
                return

            no_events += 1

    # Calculate hit rate
    hit_rate = 1 - (mmu.get_total_page_faults() / no_events) if no_events > 0 else 0

    # Calculate execution time
    end_time = time.time()  # End the timer
    execution_time = end_time - start_time  # Time in seconds

    return (frames, no_events, mmu.get_total_disk_reads(), mmu.get_total_disk_writes(), mmu.get_total_page_faults(), hit_rate, execution_time)
