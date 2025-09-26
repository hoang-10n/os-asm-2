from mmu import MMU

class ClockMMU(MMU):
    def __init__(self, frames):
        """
        Constructor for Clock (ESC) MMU.
        Each frame has:
        - page_number
        - reference bit (for second chance)
        - dirty bit
        """
        self.frames = frames
        self.frame_table = [None] * frames
        self.ref_bits = [0] * frames
        self.dirty_bits = [0] * frames
        self.page_to_frame = {}  # maps page_number -> frame index
        self.clock_hand = 0
        self.disk_reads = 0
        self.disk_writes = 0
        self.page_faults = 0
        self.debug = False

    def set_debug(self):
        self.debug = True

    def reset_debug(self):
        self.debug = False

    def _find_victim(self):
        """
        Clock replacement algorithm:
        - Scan with clock hand
        - If ref bit == 0, remove this frame
        - If ref bit == 1, clear it and move hand forward
        """
        while True:
            if self.ref_bits[self.clock_hand] == 0:
                # Found victim
                victim_index = self.clock_hand
                victim_page = self.frame_table[victim_index]
                dirty = self.dirty_bits[victim_index]
                return victim_index, victim_page, dirty
            else:
                # Give second chance
                self.ref_bits[self.clock_hand] = 0
                self.clock_hand = (self.clock_hand + 1) % self.frames

    def _access_page(self, page_number, is_write=False):
        # CASE 1: Page hit
        if page_number in self.page_to_frame:
            idx = self.page_to_frame[page_number]
            self.ref_bits[idx] = 1  # mark recently used
            if is_write:
                self.dirty_bits[idx] = 1
            if self.debug:
                print(f"[HIT] Page {page_number} in frame {idx}")
            return

        # CASE 2: Page fault
        self.page_faults += 1
        self.disk_reads += 1
        if self.debug:
            print(f"[MISS] Page fault on {page_number}")

        # Free frame available
        if None in self.frame_table:
            idx = self.frame_table.index(None)
            self.frame_table[idx] = page_number
            self.page_to_frame[page_number] = idx
            self.ref_bits[idx] = 1
            self.dirty_bits[idx] = 1 if is_write else 0
            if self.debug:
                print(f" - Allocated page {page_number} to free frame {idx}")
            return

        # Replacement required
        idx, victim_page, dirty = self._find_victim()

        if dirty:
            self.disk_writes += 1
            if self.debug:
                print(f" - Removing dirty page {victim_page} (disk write)")
        else:
            if self.debug:
                print(f" - Removing clean page {victim_page} (discarded)")

        # Replace with new page
        del self.page_to_frame[victim_page]
        self.frame_table[idx] = page_number
        self.page_to_frame[page_number] = idx
        self.ref_bits[idx] = 1
        self.dirty_bits[idx] = 1 if is_write else 0

        if self.debug:
            print(f" - Loaded new page {page_number} into frame {idx}")

        # Advance clock hand
        self.clock_hand = (idx + 1) % self.frames

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
