"""Tests for persistence schema and reproducibility service."""

from __future__ import annotations

import importlib.util
import unittest

SQLALCHEMY_AVAILABLE = importlib.util.find_spec("sqlalchemy") is not None

if SQLALCHEMY_AVAILABLE:
    from synapses.persistence import Base, PersistenceService
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session


@unittest.skipUnless(SQLALCHEMY_AVAILABLE, "sqlalchemy dependency not installed")
class PersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.service = PersistenceService(self.session)

    def tearDown(self) -> None:
        self.session.close()

    def test_run_and_reproducibility_record(self) -> None:
        self.service.store_config_version("baseline", "v1", {"tax": 0.2})
        run = self.service.create_run(
            run_uid="run-1", experiment_name="baseline", seed=42, config_version="v1"
        )
        self.service.store_metric(run.id, 1, "crime", 0.3)
        self.service.store_intervention(run.id, 1, "taxation", {"delta": 0.01})
        self.service.store_snapshot(run.id, 1, b"{}")
        self.service.store_model_checkpoint(
            run.id, 1, "director_ppo", storage_uri="s3://bucket/model.bin", payload=None
        )
        self.service.finalize_run(run.id, "completed")
        self.session.commit()

        rr = self.service.build_reproducibility_record("run-1")
        self.assertEqual(rr.seed, 42)
        self.assertEqual(rr.config_version, "v1")
        self.assertTrue(rr.config_hash)


if __name__ == "__main__":
    unittest.main()
