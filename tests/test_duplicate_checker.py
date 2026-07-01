"""Testes do controle de duplicidade."""

import tempfile
import unittest
from pathlib import Path

from nf_agent.duplicate_checker import DuplicateChecker
from nf_agent.extractor import NFData


class TestDuplicateChecker(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.registry = Path(self.tmp.name) / "registry.json"
        self.checker = DuplicateChecker(registry_path=self.registry)

    def tearDown(self):
        self.tmp.cleanup()

    def test_register_and_detect_cnpj_numero(self):
        nf = NFData(cnpj_emitente="12345678000190", numero_nf="1001")
        self.assertFalse(self.checker.check(nf).is_duplicate)
        self.checker.register(nf, "/tmp/nf.xml")
        result = self.checker.check(nf)
        self.assertTrue(result.is_duplicate)
        self.assertIn("cnpj_num", result.reason)

    def test_chave_acesso_44_digitos(self):
        nf = NFData(chave_acesso="1" * 44, numero_nf="999")
        self.checker.register(nf, "/tmp/chave.xml")
        dup = NFData(chave_acesso="1" * 44)
        self.assertTrue(self.checker.check(dup).is_duplicate)

    def test_compute_hash_stable(self):
        sample = Path(__file__).resolve().parents[1] / "demo" / "inbox" / "NF_FORNECEDOR_2026.01.10_NF-1001.xml"
        h1 = DuplicateChecker.compute_hash(sample)
        h2 = DuplicateChecker.compute_hash(sample)
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 32)


if __name__ == "__main__":
    unittest.main()
