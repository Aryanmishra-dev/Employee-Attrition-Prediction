from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.services.storage import AppStorage


class StorageTests(unittest.TestCase):
    def test_batch_result_ids_cannot_escape_storage_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = AppStorage(Path(temp_dir))

            with self.assertRaisesRegex(ValueError, "Invalid batch"):
                storage.get_batch_results_path("../employee_notes")

    def test_employee_notes_are_written_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = AppStorage(Path(temp_dir))

            notes = storage.add_employee_note("42", "Follow up scheduled", author="HR")

            self.assertEqual(notes, [storage.load_employee_notes("42")[0]])
            self.assertEqual(notes[0]["author"], "HR")
            self.assertEqual(notes[0]["note"], "Follow up scheduled")
