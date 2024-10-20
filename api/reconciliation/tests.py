import os
import tempfile
import pandas as pd
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

class ReconcileAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/reconcile/"

        # Create sample source and target CSV files
        self.source_file = self._create_temp_csv([
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "age": 25}
        ])
        self.target_file = self._create_temp_csv([
            {"id": 1, "name": "Alice", "age": 31},
            {"id": 3, "name": "Charlie", "age": 40}
        ])

    def tearDown(self):
        # Cleanup temp files after each test
        os.remove(self.source_file.name)
        os.remove(self.target_file.name)

    def _create_temp_csv(self, data):
        """Helper function to create temporary CSV files."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.csv')
        pd.DataFrame(data).to_csv(temp_file.name, index=False)
        return temp_file

    def test_reconciliation_json_format(self):
        """Test reconciliation with JSON response."""
        with open(self.source_file.name, 'rb') as src, open(self.target_file.name, 'rb') as tgt:
            response = self.client.post(
                f"{self.url}?format=json",
                {"source_file": src, "target_file": tgt},
                format='multipart'
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('missing_in_target', response.json())
        self.assertIn('discrepancies', response.json())

    def test_reconciliation_csv_format(self):
        """Test reconciliation with CSV response."""
        with open(self.source_file.name, 'rb') as src, open(self.target_file.name, 'rb') as tgt:
            response = self.client.post(
                f"{self.url}?format=csv",
                {"source_file": src, "target_file": tgt},
                format='multipart'
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_reconciliation_html_format(self):
        """Test reconciliation with HTML response."""
        with open(self.source_file.name, 'rb') as src, open(self.target_file.name, 'rb') as tgt:
            response = self.client.post(
                f"{self.url}?format=html",
                {"source_file": src, "target_file": tgt},
                format='multipart'
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/html')

    def test_missing_files(self):
        """Test error response when files are missing."""
        response = self.client.post(self.url, {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())

    def test_invalid_format(self):
        """Test error response for invalid format type."""
        with open(self.source_file.name, 'rb') as src, open(self.target_file.name, 'rb') as tgt:
            response = self.client.post(
                f"{self.url}?format=invalid",
                {"source_file": src, "target_file": tgt},
                format='multipart'
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())
