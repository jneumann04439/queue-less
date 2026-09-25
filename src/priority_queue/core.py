"""A binary min-heap that supports decrease-key in O(log n).

Design
------
The heap stores entries as ``(priority, payload)`` pairs. Each payload's
current index in the underlying list is tracked in a separate dict so that
decrease-key can locate it in O(1) without rebuilding.

A few decisions worth stating:
- Priorities are compared with Python's ``<`` operator. That means tuples and
  other comparable objects are fine, but we make no attempt to order by payload
  when priorities tie; the original insertion order is preserved only to the
  extent that the heap's own shape dictates. Don't rely on FIFO tie-breaking.
- Payloads must be hashable, because they serve as keys in the index dict.
- Each payload may appear at most once in the heap. Pushing the same payload
  twice raises ``HeapError``. Without this invariant, decrease-key could not
  uniquely identify which slot to update.
"""


class HeapError(Exception):
    """Raised when the heap's invariants would be broken by an operation."""


class Heap:
    """A binary min-heap supporting decrease-key.

    >>> h = Heap()
    >>> h.push(5, "a")
    >>> h.push(3, "b")
    >>> h.peek()
    (3, 'b')
    >>> h.decrease_key("a", 2)
    >>> h.peek()
    (2, 'a')
    """

    def __init__(self):
        # Underlying storage: list of [priority, payload] lists. We use lists
        # rather than tuples because decrease-key mutates the priority in
        # place; allocating a new tuple on every sift would be wasteful.
        self._data = []
        # Maps payload -> index in self._data. Kept in lockstep with the
        # array so we never have to scan for a payload.
        self._index = {}

    def __len__(self):
        return len(self._data)

    def __contains__(self, payload):
        return payload in self._index

    def push(self, priority, payload):
        """Insert ``payload`` with the given ``priority``.

        Raises ``HeapError`` if ``payload`` is already in the heap; this keeps
        the index map unique.
        """
        if payload in self._index:
            raise HeapError(f"payload {payload!r} already in heap")
        entry = [priority, payload]
        self._data.append(entry)
        idx = len(self._data) - 1
        self._index[payload] = idx
        self._sift_up(idx)

    def peek(self):
        """Return the ``(priority, payload)`` of the minimum element.

        Raises ``HeapError`` if the heap is empty.
        """
        if not self._data:
            raise HeapError("peek from empty heap")
        return (self._data[0][0], self._data[0][1])

    def pop(self):
        """Remove and return the ``(priority, payload)`` of the minimum element.

        Raises ``HeapError`` if the heap is empty.
        """
        if not self._data:
            raise HeapError("pop from empty heap")
        top = self._data[0]
        last = self._data.pop()
        del self._index[top[1]]
        if self._data:
            # Move the last element into the root and sift it down. The index
            # map is updated inside _sift_down.
            self._data[0] = last
            self._index[last[1]] = 0
            self._sift_down(0)
        return (top[0], top[1])

    def decrease_key(self, payload, new_priority):
        """Lower the priority of ``payload`` to ``new_priority``.

        If ``new_priority`` is not less than the current priority, this is a
        no-op rather than an error: idempotent updates are convenient and the
        heap invariant is already satisfied.

        Raises ``HeapError`` if ``payload`` is not in the heap.
        """
        if payload not in self._index:
            raise HeapError(f"payload {payload!r} not in heap")
        idx = self._index[payload]
        current = self._data[idx][0]
        if new_priority >= current:
            return
        self._data[idx][0] = new_priority
        self._sift_up(idx)

    def _sift_up(self, idx):
        """Move the entry at ``idx`` up until the heap property is restored."""
        item = self._data[idx]
        while idx > 0:
            parent = (idx - 1) >> 1
            parent_item = self._data[parent]
            # Min-heap: parent must be <= child. Stop early if invariant
            # already holds.
            if parent_item[0] <= item[0]:
                break
            self._data[idx] = parent_item
            self._index[parent_item[1]] = idx
            idx = parent
        self._data[idx] = item
        self._index[item[1]] = idx

    def _sift_down(self, idx):
        """Move the entry at ``idx`` down until the heap property is restored."""
        n = len(self._data)
        item = self._data[idx]
        while True:
            left = 2 * idx + 1
            right = 2 * idx + 2
            smallest = idx
            smallest_pri = item[0]
            # Find the smallest among parent and children. We compare by
            # priority only; ties are broken by heap position (left before
            # right), which keeps the order deterministic.
            if left < n:
                left_pri = self._data[left][0]
                if left_pri < smallest_pri:
                    smallest = left
                    smallest_pri = left_pri
            if right < n:
                right_pri = self._data[right][0]
                if right_pri < smallest_pri:
                    smallest = right
                    smallest_pri = right_pri
            if smallest == idx:
                break
            child_item = self._data[smallest]
            self._data[idx] = child_item
            self._index[child_item[1]] = idx
            idx = smallest
        self._data[idx] = item
        self._index[item[1]] = idx
