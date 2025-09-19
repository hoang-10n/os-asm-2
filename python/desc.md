# `lrummu.py` — **Least Recently Used (LRU)**

**Idea:**

* Always evict the page that was accessed the longest time ago.
* Tracks recency of use → good approximation of real-world program behavior (locality of reference).

**How the code works:**

* Uses `OrderedDict`:

  * Keys = page numbers.
  * Values = `(frame_index, dirty_flag)`.
  * When a page is accessed, it’s moved to the **end** of the dictionary (most recent).
  * The **first element** in the dictionary is always the *least recently used* page.
* **On a hit**:

  * Moves the page to the end.
  * Updates dirty flag if it was a write.
* **On a miss**:

  * If free frames exist → allocate one.
  * Else → evict the first page in the dictionary.
  * If the evicted page is dirty → increment disk writes.
  * Insert new page at the end.
* Stats tracked: page faults, disk reads, disk writes.
* Debug prints show whether access was a **hit**, **miss**, or **eviction**.

---

# `randmmu.py` — **Random Replacement**

**Idea:**

* When memory is full, evict a **random page**.
* Very simple, but has unpredictable performance.

**How the code works:**

* Maintains a `page_table` (dict mapping `page_number -> (frame_index, dirty_flag)`).
* **On a hit**:

  * Updates dirty flag if it was a write.
* **On a miss**:

  * If free frame exists → allocate it.
  * Else → pick a victim randomly from `page_table.keys()`.
  * If victim is dirty → increment disk writes.
  * Replace victim’s entry with the new page.
* Randomness provided by Python’s `random.choice()`.
* Stats tracked: page faults, disk reads, disk writes.
* Debug prints show random victim selection and whether it was dirty or clean.

---

# `clockmmu.py` — **Clock / Enhanced Second Chance**

**Idea:**

* Approximates LRU with less overhead.
* Each frame has a **reference bit**:

  * Set to `1` when page is accessed.
  * When searching for a victim:

    * If reference bit = `0` → evict this page.
    * If reference bit = `1` → clear it and move the clock hand forward.
* This gives pages a “second chance” before eviction.

**How the code works:**

* Structures:

  * `frame_table` → stores page numbers in frames.
  * `ref_bits` → tracks recent usage (0 or 1).
  * `dirty_bits` → tracks whether page was written.
  * `page_to_frame` → fast lookup of page’s frame index.
  * `clock_hand` → pointer moving in a circular fashion.
* **On a hit**:

  * Sets reference bit to `1`.
  * Updates dirty bit if it was a write.
* **On a miss**:

  * If free frame exists → allocate it.
  * Else → run `_find_victim()`:

    * Spins the clock hand until it finds a frame with `ref_bit == 0`.
    * If ref\_bit == 1, clear it and advance.
    * Once victim is found:

      * If dirty → increment disk writes.
      * Replace victim with new page.
      * Set reference bit = 1, dirty bit depending on access.
      * Advance clock hand.
* Stats tracked: page faults, disk reads, disk writes.
* Debug prints trace the clock hand, evictions, and replacements.

---

# Comparison at a glance

| File          | Algorithm | Eviction policy                     | Overhead              | Notes                                |
| ------------- | --------- | ----------------------------------- | --------------------- | ------------------------------------ |
| `lrummu.py`   | LRU       | Oldest accessed                     | High (needs ordering) | Very accurate, costly to maintain.   |
| `randmmu.py`  | Random    | Pick any page randomly              | Low                   | Fast but often poor performance.     |
| `clockmmu.py` | Clock/ESC | Approximate LRU with reference bits | Medium                | Efficient, widely used in real OSes. |

---