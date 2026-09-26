# priority_queue

A binary min-heap for Python that supports decrease-key without rebuilding.

## Usage

```python
from priority_queue import Heap, HeapError

h = Heap()
h.push(5, "task-a")
h.push(3, "task-b")
h.push(7, "task-c")

print(h.peek())          # (3, 'task-b')
h.decrease_key("task-a", 1)
print(h.peek())          # (1, 'task-a')

while len(h):
    print(h.pop())       # (1, 'task-a'), (3, 'task-b'), (7, 'task-c')
```

## Why this exists

Classic Dijkstra/A* need a priority queue where a key already in the queue can
be lowered. Python's `heapq` has no index map, so the usual workaround is to
push a duplicate entry and ignore stale ones on `pop`. That works but wastes
memory on long-lived queues and makes `len()` misleading. This library tracks
each payload's position so decrease-key runs in O(log n) and `len()` stays
honest.

The trade-off: payloads must be hashable and unique within the heap. Pushing
the same payload twice raises `HeapError`. If you need multiple equal payloads,
wrap them in a unique identifier.

## Priorities

Priorities are ordered by Python's `<` operator. Numbers, strings, and tuples
all work. Ties are not broken by insertion order — don't depend on FIFO
behaviour among equal-priority entries.

## Edge cases

- `decrease_key` with a priority that isn't lower than the current one is a
  no-op, not an error. This keeps bulk updates idempotent.
- `peek` and `pop` on an empty heap raise `HeapError`.
- `decrease_key` on a payload not in the heap raises `HeapError`.

## Running the tests

```
PYTHONPATH=src python -m unittest discover -s tests
```
