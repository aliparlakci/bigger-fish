import unittest
import trace_collector

class TestTraceCollector(unittest.TestCase):
    def test_get_process_parent_id_of(self):
        pgid = trace_collector.get_process_parent_id_of("chrome")
        assert True

if __name__ == '__main__':
    unittest.main()