import unittest
from unittest.mock import MagicMock, patch, mock_open
import json
import Suricata_to_DB

# Run with:
# python -m unittest test_suricata_to_postgress.py

class TestSuricataToPostgress(unittest.TestCase):
    def test_insert_log_with_alert(self):
        fake_cursor = MagicMock()
        log_data = {
            "timestamp": "2020-01-01T12:00:00Z",
            "src_ip": "192.168.1.1",
            "src_port": 1234,
            "dest_ip": "192.168.1.2",
            "dest_port": 80,
            "proto": "TCP",
            "alert": {"signature": "Test Alert"}
        }
        
        Suricata_to_DB.insert_log(fake_cursor, log_data)
        self.assertEqual(fake_cursor.execute.call_count, 1)
        
        _, params = fake_cursor.execute.call_args[0]
        expected_params = (
            "2020-01-01T12:00:00Z",
            "192.168.1.1",
            1234,
            "192.168.1.2",
            80,
            "TCP",
            "Test Alert"
        )
        self.assertEqual(params, expected_params)

    def test_insert_log_without_alert(self):
        fake_cursor = MagicMock()
        log_data = {
            "timestamp": "2020-01-01T12:00:00Z",
            "src_ip": "192.168.1.1",
            "src_port": 1234,
            "dest_ip": "192.168.1.2",
            "dest_port": 80,
            "proto": "TCP"
        }
        Suricata_to_DB.insert_log(fake_cursor, log_data)
        self.assertEqual(fake_cursor.execute.call_count, 1)
        _, params = fake_cursor.execute.call_args[0]
        expected_params = (
            "2020-01-01T12:00:00Z",
            "192.168.1.1",
            1234,
            "192.168.1.2",
            80,
            "TCP",
            None
        )
        self.assertEqual(params, expected_params)

    @patch("Suricata_to_DB.connect_db")
    @patch("builtins.open", new_callable=mock_open, read_data=
           '{"event_type": "alert", "timestamp": "2020-01-01T12:00:00Z", "src_ip": "192.168.1.1", '
           '"src_port": 1234, "dest_ip": "192.168.1.2", "dest_port": 80, "proto": "TCP", '
           '"alert": {"signature": "Test Alert"}}\n'
           '{"event_type": "other"}\n'
          )
    def test_parse_logs(self, mock_file, mock_connect_db):
        fake_cursor = MagicMock()
        fake_conn = MagicMock()
        fake_conn.cursor.return_value = fake_cursor
        mock_connect_db.return_value = fake_conn

        Suricata_to_DB.parse_logs()

        self.assertEqual(fake_cursor.execute.call_count, 1)
        fake_conn.commit.assert_called_once()
        fake_cursor.close.assert_called_once()
        fake_conn.close.assert_called_once()

if __name__ == "__main__":
    unittest.main()
