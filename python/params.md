# `memsim.py` (the driver program)

### Parameters

* **`sys.argv[1] → input_file`**
  Path to the memory trace file. Each line has `<hex_address> <R/W>`.

* **`sys.argv[2] → frames`**
  Number of physical frames available in memory. This is the capacity of your simulated RAM.

* **`sys.argv[3] → replacement_mode`**
  Replacement strategy to use:

  * `"rand"` → random replacement (`RandMMU`).
  * `"lru"` → least recently used (`LruMMU`).
  * `"esc"` → enhanced second chance / clock (`ClockMMU`).

* **`sys.argv[4] → debug_mode`**
  Controls verbosity:

  * `"debug"` → print detailed hits/misses/evictions.
  * `"quiet"` → only print final stats.

* **`PAGE_OFFSET = 12`**
  Because each page = $2^{12} = 4096$ bytes. Shifting logical addresses right by 12 bits extracts the **page number**.

### Variables

* **`logical_address`**: The raw virtual address from trace file.
* **`page_number`**: Virtual page index = `logical_address >> 12`.
* **`no_events`**: Counter of total read/write operations processed.

### Outputs (from MMU)

* **`total disk reads`**: How many times a page fault required fetching a page from disk.
* **`total disk writes`**: How many evictions wrote dirty pages back to disk.
* **`total page faults`**: How many times the requested page was not in memory.
* **`page fault rate`**: `faults / frames` (⚠️ sometimes it’s faults / events — check your assignment spec).

---

# `mmu.py` (abstract base class)

Defines the **interface** all MMUs must implement:

* **`read_memory(page_number)`**: Handle a read operation for a given virtual page.
* **`write_memory(page_number)`**: Handle a write operation.
* **`set_debug()`**: Enable debug printing.
* **`reset_debug()`**: Disable debug printing.
* **`get_total_disk_reads()`**: Return counter of disk reads.
* **`get_total_disk_writes()`**: Return counter of disk writes.
* **`get_total_page_faults()`**: Return counter of page faults.

---

# `lrummu.py` (LRU replacement)

### Parameters / Variables

* **`frames`**: Max number of physical frames.
* **`frame_table (OrderedDict)`**: Keys = page numbers, Values = `(frame_index, dirty_flag)`. Ordered so oldest (LRU) is at front.
* **`next_frame`**: Next free frame index to use before memory is full.
* **`debug`**: Whether to print debug logs.

### Counters

* **`page_faults`**: Incremented when page is not found.
* **`disk_reads`**: Incremented when a page must be loaded from disk.
* **`disk_writes`**: Incremented when evicting a dirty page.

---

# `randmmu.py` (Random replacement)

### Parameters / Variables

* **`frames`**: Max number of physical frames.
* **`page_table (dict)`**: Maps page numbers → `(frame_index, dirty_flag)`.
* **`next_frame`**: Next free frame index.
* **`debug`**: Debug printing flag.

### Counters

* **`page_faults`**: Misses that required fetching from disk.
* **`disk_reads`**: Always incremented when bringing a new page.
* **`disk_writes`**: Incremented if a dirty page is chosen randomly for eviction.

---

# `clockmmu.py` (Enhanced Second Chance / Clock)

### Parameters / Variables

* **`frames`**: Max number of physical frames.
* **`frame_table (list)`**: Array of length = frames, storing page numbers (or `None` if empty).
* **`ref_bits (list)`**: Parallel array of reference bits (`0` or `1`). Indicates if page was recently used.
* **`dirty_bits (list)`**: Parallel array of dirty flags (`0` clean, `1` modified).
* **`page_to_frame (dict)`**: Fast lookup from page number → frame index.
* **`clock_hand (int)`**: Points to the current frame in the circular scan.

### Counters

* **`page_faults`**: Number of misses.
* **`disk_reads`**: Number of loads from disk.
* **`disk_writes`**: Number of dirty evictions.

---

# Summary of shared parameters

| Parameter / Variable | Where      | Meaning                                |
| -------------------- | ---------- | -------------------------------------- |
| `frames`             | all MMUs   | Max number of pages in memory at once  |
| `page_number`        | everywhere | The virtual page index (address >> 12) |
| `debug`              | all MMUs   | Controls detailed vs quiet logging     |
| `page_faults`        | all MMUs   | Count of misses (page not in memory)   |
| `disk_reads`         | all MMUs   | Pages fetched from disk (on fault)     |
| `disk_writes`        | all MMUs   | Dirty pages written back when evicted  |

---