"""Testes do extrator de NF-e."""

import unittest
from pathlib import Path

from nf_agent.extractor import NFData, extract_from_file, parse_amount

DEMO_XML = Path(__file__).resolve().parents[1] / "demo" / "inbox" / "NF_FORNECEDOR_2026.01.10_NF-1001.xml"


class TestExtractor(unittest.TestCase):
    def test_extract_xml_demo(self):
        nf = extract_from_file(DEMO_XML)
        self.assertEqual(nf.tipo_arquivo, "xml")
        self.assertEqual(nf.numero_nf, "1001")
        self.assertEqual(nf.cnpj_emitente, "12345678000190")
        self.assertIn("Fornecedor Alpha", nf.razao_social_emitente or "")

    def test_parse_amount_br(self):
        self.assertEqual(parse_amount("19.104,36"), 19104.36)

    def test_parse_amount_us(self):
        self.assertEqual(parse_amount("15000.00"), 15000.0)

    def test_empty_nfdata(self):
        nf = NFData()
        self.assertIsNone(parse_amount(nf.valor_total))


if __name__ == "__main__":
    unittest.main()
