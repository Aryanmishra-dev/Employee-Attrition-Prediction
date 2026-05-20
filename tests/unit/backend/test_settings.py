from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from app.core.config import Settings


class SettingsTests(unittest.TestCase):
    def test_settings_reject_invalid_thresholds(self) -> None:
        env = {
            "MEDIUM_RISK_THRESHOLD": "0.8",
            "HIGH_RISK_THRESHOLD": "0.4",
        }
        with patch.dict(os.environ, env, clear=False):
            with self.assertRaisesRegex(ValueError, "Risk thresholds"):
                Settings.from_env()

    def test_settings_resolves_relative_runtime_data_dir(self) -> None:
        with patch.dict(os.environ, {"APP_RUNTIME_DATA_DIR": "runtime-data"}, clear=False):
            settings = Settings.from_env()

        self.assertEqual(settings.data_dir, settings.root_dir / "runtime-data")
