from mmu import MMU
import collections

class LruMMU(MMU):
    def __init__(self, frames):
        """
        Constructor: initialize the LRU MMU with a given number of frames.
        - frames: total physical frames available
        """
        self.frames = frames
        self.page_table = {}   # maps page_number -> frame index
        self.frame_usage = collections.OrderedDict()  # tracks recency of use
        self.disk_reads = 0
        self.disk_writes = 0
        self.page_faults = 0
        self.debug = False

    def set_debug(self):
        """Enable debug messages."""
        self.debug = True

    def reset_debug(self):
        """Disable debug messages."""
        self.debug = False

    def _access_page(self, page_number, is_write=False):
        """
        Internal helper for handling read/write accesses.
        - Checks if page is in memory.
        - If not, triggers a page fault and replacement.
        - Updates LRU ordering.
        """
        # CASE 1: Page hit
        if page_number in self.page_table:
            if self.debug:
                print(f"[HIT] Page {page_number} already in memory")
            # Move page to the end (most recently used)
            self.frame_usage.move_to_end(page_number)
            if is_write:
                # Mark as dirty
                self.frame_usage[page_number] = True
            return

        # CASE 2: Page fault
        self.page_faults += 1
        self.disk_reads += 1  # every fault causes a disk read

        if self.debug:
            print(f"[MISS] Page fault on {page_number}")

        # CASE 2a: Free frame available
        if len(self.page_table) < self.frames:
            self.page_table[page_number] = len(self.page_table)
            self.frame_usage[page_number] = is_write
            if self.debug:
                print(f"  Allocated page {page_number} into free frame")
            return

        # CASE 2b: Need replacement
        # Victim = least recently used (first entry in OrderedDict)
        victim_page, dirty = self.frame_usage.popitem(last=False)
        if dirty:
            self.disk_writes += 1
            if self.debug:
                print(f"  Evicting dirty page {victim_page} (disk write)")
        else:
            if self.debug:
                print(f"  Evicting clean page {victim_page} (discarded)")

        # Remove victim from page table
        del self.page_table[victim_page]

        # Insert new page
        self.page_table[page_number] = len(self.page_table)
        self.frame_usage[page_number] = is_write

        if self.debug:
            print(f"  Loaded new page {page_number}")

    def read_memory(self, page_number):
        """Simulate a read operation on a page."""
        self._access_page(page_number, is_write=False)
        if self.debug:
            print(f"  Read from page {page_number}")

    def write_memory(self, page_number):
        """Simulate a write operation on a page (marks page as dirty)."""
        self._access_page(page_number, is_write=True)
        if self.debug:
            print(f"  Write to page {page_number}")

    def get_total_disk_reads(self):
        """Return total disk reads (page faults)."""
        return self.disk_reads

    def get_total_disk_writes(self):
        """Return total disk writes (evicted dirty pages)."""
        return self.disk_writes

    def get_total_page_faults(self):
        """Return total page faults."""
        return self.page_faults
