import unittest

from priority_queue import Heap, HeapError


class TestHeapBasic(unittest.TestCase):
    def test_push_peek_pop_single(self):
        h = Heap()
        h.push(5, "a")
        self.assertEqual(h.peek(), (5, "a"))
        self.assertEqual(h.pop(), (5, "a"))
        self.assertEqual(len(h), 0)

    def test_empty_peek_raises(self):
        h = Heap()
        with self.assertRaises(HeapError):
            h.peek()

    def test_empty_pop_raises(self):
        h = Heap()
        with self.assertRaises(HeapError):
            h.pop()

    def test_ordering_with_distinct_priorities(self):
        h = Heap()
        for p, v in [(3, "c"), (1, "a"), (2, "b")]:
            h.push(p, v)
        result = []
        while len(h):
            result.append(h.pop())
        self.assertEqual(result, [(1, "a"), (2, "b"), (3, "c")])

    def test_len_tracks_size(self):
        h = Heap()
        self.assertEqual(len(h), 0)
        h.push(1, "a")
        self.assertEqual(len(h), 1)
        h.push(2, "b")
        self.assertEqual(len(h), 2)
        h.pop()
        self.assertEqual(len(h), 1)

    def test_contains(self):
        h = Heap()
        h.push(1, "a")
        self.assertIn("a", h)
        self.assertNotIn("b", h)


class TestDecreaseKey(unittest.TestCase):
    def test_decrease_key_promotes_element(self):
        h = Heap()
        h.push(5, "a")
        h.push(3, "b")
        h.push(4, "c")
        h.decrease_key("a", 1)
        self.assertEqual(h.peek(), (1, "a"))

    def test_decrease_key_no_op_when_not_smaller(self):
        h = Heap()
        h.push(5, "a")
        h.decrease_key("a", 5)
        self.assertEqual(h.peek(), (5, "a"))
        h.decrease_key("a", 7)
        self.assertEqual(h.peek(), (5, "a"))

    def test_decrease_key_missing_payload_raises(self):
        h = Heap()
        h.push(1, "a")
        with self.assertRaises(HeapError):
            h.decrease_key("z", 0)

    def test_decrease_key_after_pop_uses_correct_indices(self):
        # Pop clears the top; ensure the index map for the removed payload is
        # gone and that decrease-key still finds the survivors correctly.
        h = Heap()
        h.push(5, "a")
        h.push(3, "b")
        h.push(4, "c")
        self.assertEqual(h.pop(), (3, "b"))
        with self.assertRaises(HeapError):
            h.decrease_key("b", 1)
        h.decrease_key("c", 1)
        self.assertEqual(h.peek(), (1, "c"))

    def test_decrease_key_to_equal_of_another(self):
        # When two entries share a priority after decrease-key, the heap must
        # still be valid. We don't assert tie order, only that pop yields all
        # entries in non-decreasing priority order.
        h = Heap()
        h.push(2, "a")
        h.push(2, "b")
        h.decrease_key("b", 2)
        first = h.pop()[0]
        second = h.pop()[0]
        self.assertEqual((first, second), (2, 2))


class TestDuplicates(unittest.TestCase):
    def test_duplicate_payload_raises(self):
        h = Heap()
        h.push(1, "a")
        with self.assertRaises(HeapError):
            h.push(2, "a")


class TestHeapProperty(unittest.TestCase):
    def _validate(self, h):
        data = h._data
        n = len(data)
        for i in range(n):
            left = 2 * i + 1
            right = 2 * i + 2
            if left < n:
                self.assertLessEqual(data[i][0], data[left][0])
            if right < n:
                self.assertLessEqual(data[i][0], data[right][0])
        # Index map must be consistent with the array.
        for i, (_, payload) in enumerate(data):
            self.assertEqual(h._index[payload], i)

    def test_property_holds_after_mixed_operations(self):
        h = Heap()
        ops = [
            ("push", 5, "a"),
            ("push", 3, "b"),
            ("push", 7, "c"),
            ("pop",),
            ("push", 1, "d"),
            ("decrease", "c", 0),
            ("pop",),
            ("push", 4, "e"),
            ("decrease", "e", 2),
        ]
        for op in ops:
            kind = op[0]
            if kind == "push":
                h.push(op[1], op[2])
            elif kind == "pop":
                h.pop()
            elif kind == "decrease":
                h.decrease_key(op[1], op[2])
            self._validate(h)


class TestTuplePriorities(unittest.TestCase):
    def test_tuple_priorities_ordered_lexicographically(self):
        # Priorities are compared with ``<``, so tuples work for compound keys.
        h = Heap()
        h.push((2, 1), "a")
        h.push((1, 9), "b")
        self.assertEqual(h.peek()[1], "b")


if __name__ == "__main__":
    unittest.main()
