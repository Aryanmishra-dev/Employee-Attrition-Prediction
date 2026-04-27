from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.security import configure_security
from app.core.settings import Settings


def build_settings(tmp_path: Path, auth_token: str | None = None) -> Settings:
    return Settings(
        root_dir=tmp_path,
        app_dir=tmp_path / "app",
        model_path=tmp_path / "app" / "ml_model" / "model.pkl",
        public_dir=tmp_path / "public",
        dataset_path=tmp_path / "dataset.csv",
        data_dir=tmp_path / "data",
        medium_risk_threshold=0.35,
        high_risk_threshold=0.65,
        max_upload_bytes=20,
        max_batch_rows=10,
        max_note_chars=100,
        store_raw_prediction_inputs=True,
        allowed_hosts=["*"],
        allowed_origins=[],
        auth_token=auth_token,
        auth_username=None,
        auth_password=None,
        docs_enabled=True,
    )


def build_client(settings: Settings) -> TestClient:
    app = FastAPI()
    configure_security(app, settings)

    @app.get("/")
    async def index() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/write")
    async def write() -> dict[str, str]:
        return {"status": "written"}

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return TestClient(app)


class SecurityTests(unittest.TestCase):
    def test_auth_token_protects_private_routes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            client = build_client(build_settings(Path(temp_dir), auth_token="secret"))

            self.assertEqual(client.get("/").status_code, 401)
            self.assertEqual(
                client.get("/", headers={"Authorization": "Bearer secret"}).status_code,
                200,
            )
            self.assertEqual(client.get("/health").status_code, 200)

    def test_oversized_requests_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            client = build_client(build_settings(Path(temp_dir)))

            response = client.post(
                "/write",
                content="x" * 21,
                headers={"Origin": "http://testserver"},
            )

        self.assertEqual(response.status_code, 413)

    def test_cross_origin_writes_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            client = build_client(build_settings(Path(temp_dir)))

            response = client.post(
                "/write",
                content="ok",
                headers={"Origin": "https://evil.example"},
            )

        self.assertEqual(response.status_code, 403)
