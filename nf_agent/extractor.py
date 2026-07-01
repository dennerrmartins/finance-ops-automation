"""Extração de dados de NF-e a partir de XML (e PDF opcional)."""

import re
import zipfile
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from loguru import logger


@dataclass
class NFData:
    numero_nf: Optional[str] = None
    serie: Optional[str] = None
    data_emissao: Optional[str] = None
    valor_total: Optional[str] = None
    cnpj_emitente: Optional[str] = None
    razao_social_emitente: Optional[str] = None
    cnpj_tomador: Optional[str] = None
    chave_acesso: Optional[str] = None
    tipo_arquivo: str = "desconhecido"
    extraction_method: str = "none"


def extract_from_file(file_path: Path) -> NFData:
    ext = file_path.suffix.lower()
    if ext == ".xml":
        return _from_xml(file_path)
    if ext == ".pdf":
        return _from_pdf(file_path)
    if ext == ".zip":
        return _from_zip(file_path)
    logger.warning(f"Tipo não suportado: {ext}")
    return NFData(tipo_arquivo=ext.lstrip(".") or "desconhecido")


def _from_xml(file_path: Path) -> NFData:
    nf = NFData(tipo_arquivo="xml", extraction_method="lxml")
    try:
        from lxml import etree

        root = etree.parse(str(file_path)).getroot()
        nf.numero_nf = (
            _xt(root, ".//{*}nNF")
            or _xt(root, ".//{*}Numero")
            or _xt(root, ".//{*}nDPS")
        )
        nf.serie = _xt(root, ".//{*}serie") or _xt(root, ".//{*}serieDPS")
        nf.data_emissao = (
            _xt(root, ".//{*}dhEmi")
            or _xt(root, ".//{*}DataEmissao")
            or _xt(root, ".//{*}dhProc")
        )
        nf.cnpj_emitente = (
            _xt(root, ".//{*}emit/{*}CNPJ")
            or _xt(root, ".//{*}PrestadorServico/{*}IdentificacaoPrestador/{*}Cnpj")
            or _xt(root, ".//{*}Prestador/{*}Cnpj")
            or _xt(root, ".//{*}CpfCnpj/{*}Cnpj")
        )
        nf.razao_social_emitente = (
            _xt(root, ".//{*}emit/{*}xNome")
            or _xt(root, ".//{*}PrestadorServico/{*}RazaoSocial")
            or _xt(root, ".//{*}Prestador/{*}RazaoSocial")
            or _xt(root, ".//{*}RazaoSocial")
        )
        nf.cnpj_tomador = (
            _xt(root, ".//{*}dest/{*}CNPJ")
            or _xt(root, ".//{*}TomadorServico/{*}IdentificacaoTomador/{*}CpfCnpj/{*}Cnpj")
            or _xt(root, ".//{*}Tomador/{*}Cnpj")
        )
        nf.valor_total = (
            _xt(root, ".//{*}ICMSTot/{*}vNF")
            or _xt(root, ".//{*}ValoresNfse/{*}ValorLiquidoNfse")
            or _xt(root, ".//{*}ValorServicos")
        )
        chave = _xa(root, ".//{*}infNFe", "Id")
        if chave and chave.startswith("NFe"):
            chave = chave[3:]
        nf.chave_acesso = chave
    except ImportError:
        nf.extraction_method = "unavailable"
        logger.error("lxml não instalado.")
    except Exception as exc:
        nf.extraction_method = "error"
        logger.error(f"Erro XML {file_path.name}: {exc}")
    return nf


def _from_pdf(file_path: Path) -> NFData:
    nf = NFData(tipo_arquivo="pdf", extraction_method="pdfplumber")
    try:
        import pdfplumber

        with pdfplumber.open(str(file_path)) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        patterns = {
            "numero_nf": [r"N[úu]mero\s*[:\-]?\s*(\d{4,9})"],
            "cnpj_emitente": [r"(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})"],
            "valor_total": [r"Valor\s+Total\s*[:\-]?\s*R?\$?\s*([\d.,]+)"],
            "data_emissao": [r"Emiss[aã]o\s*[:\-]?\s*(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})"],
        }
        for field, pats in patterns.items():
            for pat in pats:
                match = re.search(pat, text, re.IGNORECASE)
                if match:
                    setattr(nf, field, match.group(1).strip())
                    break
    except ImportError:
        nf.extraction_method = "unavailable"
    except Exception as exc:
        nf.extraction_method = "error"
        logger.error(f"Erro PDF {file_path.name}: {exc}")
    return nf


def _from_zip(file_path: Path) -> NFData:
    try:
        with zipfile.ZipFile(str(file_path), "r") as zf:
            xml_files = [f for f in zf.namelist() if f.lower().endswith(".xml")]
            if not xml_files:
                return NFData(tipo_arquivo="zip")
            with tempfile.TemporaryDirectory() as tmpdir:
                zf.extract(xml_files[0], tmpdir)
                nf = extract_from_file(Path(tmpdir) / xml_files[0])
                nf.tipo_arquivo = "zip"
                return nf
    except Exception as exc:
        logger.error(f"Erro ZIP {file_path.name}: {exc}")
    return NFData(tipo_arquivo="zip")


def _xt(root, xpath: str) -> Optional[str]:
    elements = root.findall(xpath)
    if elements and elements[0].text:
        return elements[0].text.strip() or None
    return None


def _xa(root, xpath: str, attr: str) -> Optional[str]:
    elements = root.findall(xpath)
    if elements:
        return (elements[0].get(attr) or "").strip() or None
    return None


def parse_amount(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    cleaned = re.sub(r"[^\d,.-]", "", value)
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None
