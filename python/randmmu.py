from mmu import MMU
import random

class RandMMU(MMU):
    def __init__(self, frames):
        """
        Constructor for Random MMU.
        """
        self.frames = frames
        self.page_table = {}   # page_number -> (frame index, dirty flag)
        self.disk_reads = 0
        self.disk_writes = 0
        self.page_faults = 0
        self.debug = False

    def set_debug(self):
        self.debug = True

    def reset_debug(self):
        self.debug = False

    def _access_page(self, page_number, is_write=False):
        # CASE 1: Page hit
        if page_number in self.page_table:
            if is_write:
                self.page_table[page_number] = (self.page_table[page_number][0], True)
            if self.debug:
                print(f"[HIT] Page {page_number} already in memory")
            return

        # CASE 2: Page fault
        self.page_faults += 1
        self.disk_reads += 1
        if self.debug:
            print(f"[MISS] Page fault on {page_number}")

        # Free frame available
        if len(self.page_table) < self.frames:
            self.page_table[page_number] = (len(self.page_table), is_write)
            if self.debug:
                print(f" - Allocated page {page_number} into free frame")
            return

        # No free frame → random victim
        victim_page = random.choice(list(self.page_table.keys()))
        frame_index, dirty = self.page_table[victim_page]

        if dirty:
            self.disk_writes += 1
            if self.debug:
                print(f" - Evicting dirty page {victim_page} (disk write)")
        else:
            if self.debug:
                print(f" - Evicting clean page {victim_page} (discarded)")

        del self.page_table[victim_page]
        self.page_table[page_number] = (frame_index, is_write)

        if self.debug:
            print(f" - Loaded new page {page_number} into frame {frame_index}")

    def read_memory(self, page_number):
        self._access_page(page_number, is_write=False)
        if self.debug:
            print(f" - Read from page {page_number}")

    def write_memory(self, page_number):
        self._access_page(page_number, is_write=True)
        if self.debug:
            print(f" - Write to page {page_number}")

    def get_total_disk_reads(self):
        return self.disk_reads

    def get_total_disk_writes(self):
        return self.disk_writes

    def get_total_page_faults(self):
        return self.page_faults
