"""Testes da organização documental."""

import shutil
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from nf_agent.extractor import NFData
from nf_agent.organizer import organize_file


class TestOrganizer(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.notas_dir = Path(self.tmp.name) / "notas"
        self.notas_dir.mkdir()
        self.src_dir = Path(self.tmp.name) / "src"
        self.src_dir.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_organize_creates_supplier_date_path(self):
        demo = (
            Path(__file__).resolve().parents[1]
            / "demo"
            / "inbox"
            / "NF_FORNECEDOR_2026.01.10_NF-1001.xml"
        )
        src = self.src_dir / demo.name
        shutil.copy(demo, src)
        nf = NFData(
            numero_nf="1001",
            razao_social_emitente="Fornecedor Alpha Ltda",
            data_emissao="2026-01-10",
        )

        with patch("nf_agent.organizer.config.NOTAS_DIR", self.notas_dir):
            result = organize_file(
                src, fallback_date=datetime(2026, 1, 10), nf_data=nf, copy=True
            )

        self.assertTrue(result["success"])
        dest = Path(result["destination_path"])
        self.assertTrue(dest.exists())
        self.assertIn("Fornecedor Alpha", str(dest))
        self.assertIn("2026.01.10", str(dest))


if __name__ == "__main__":
    unittest.main()
