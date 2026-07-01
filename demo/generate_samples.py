"""Gera XMLs fictícios de NFS-e para o modo demo (dados sintéticos)."""

from pathlib import Path

import config

SAMPLES = [
    ("2026.01.10", "1001", "Fornecedor Alpha Ltda", "12345678000190", "18500.00", "Comercial"),
    ("2026.01.18", "1002", "Agencia Beta Marketing SA", "23456789000181", "9200.50", "Marketing"),
    ("2026.01.25", "1003", "Studio Gamma Design ME", "34567890000172", "4300.00", "Marketing"),
    ("2026.02.05", "1004", "Fornecedor Alpha Ltda", "12345678000190", "22100.00", "Comercial"),
    ("2026.02.14", "1005", "Consultoria Delta Ltda", "45678901000163", "15800.75", "Experiencia Familia"),
    ("2026.02.22", "1006", "Tech Epsilon Servicos SA", "56789012000154", "7600.00", "Comercial"),
    ("2026.03.03", "1007", "Agencia Beta Marketing SA", "23456789000181", "11400.00", "Marketing"),
    ("2026.03.12", "1008", "Eventos Zeta Producoes Ltda", "67890123000145", "28900.00", "Experiencia Familia"),
    ("2026.03.20", "1009", "Fornecedor Alpha Ltda", "12345678000190", "16750.25", "Comercial"),
    ("2026.04.02", "1010", "Studio Gamma Design ME", "34567890000172", "5100.00", "Marketing"),
    ("2026.04.11", "1011", "Consultoria Delta Ltda", "45678901000163", "13200.00", "Experiencia Familia"),
    ("2026.04.19", "1012", "Tech Epsilon Servicos SA", "56789012000154", "8450.90", "Comercial"),
    ("2026.05.06", "1013", "Agencia Beta Marketing SA", "23456789000181", "19800.00", "Marketing"),
    ("2026.05.15", "1014", "Eventos Zeta Producoes Ltda", "67890123000145", "12400.00", "Experiencia Familia"),
    ("2026.05.28", "1015", "Fornecedor Alpha Ltda", "12345678000190", "20300.00", "Comercial"),
    # Duplicata proposital (mesmo CNPJ + número) para testar duplicate_checker
    ("2026.05.28", "1015", "Fornecedor Alpha Ltda", "12345678000190", "20300.00", "Comercial"),
]


def _xml(date_iso: str, numero: str, razao: str, cnpj: str, valor: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<CompNfse xmlns="http://www.abrasf.org.br/nfse.xsd">
  <Nfse>
    <InfNfse>
      <Numero>{numero}</Numero>
      <DataEmissao>{date_iso}T10:30:00</DataEmissao>
      <PrestadorServico>
        <IdentificacaoPrestador>
          <Cnpj>{cnpj}</Cnpj>
        </IdentificacaoPrestador>
        <RazaoSocial>{razao}</RazaoSocial>
      </PrestadorServico>
      <TomadorServico>
        <IdentificacaoTomador>
          <CpfCnpj><Cnpj>98765432000111</Cnpj></CpfCnpj>
        </IdentificacaoTomador>
      </TomadorServico>
      <ValoresNfse>
        <ValorLiquidoNfse>{valor}</ValorLiquidoNfse>
      </ValoresNfse>
    </InfNfse>
  </Nfse>
</CompNfse>
"""


def generate(out_dir: Path | None = None) -> list[Path]:
    out_dir = out_dir or config.DEMO_INBOX_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    seen_keys: set[str] = set()

    for date_folder, numero, razao, cnpj, valor, _area in SAMPLES:
        key = f"{cnpj}_{numero}"
        suffix = ""
        if key in seen_keys:
            suffix = "_dup"
        seen_keys.add(key)
        y, m, d = date_folder.split(".")
        date_iso = f"{y}-{m}-{d}"
        short = razao.split()[0].upper()
        filename = f"NF_{short}_{date_folder}_NF-{numero}{suffix}.xml"
        path = out_dir / filename
        path.write_text(_xml(date_iso, numero, razao, cnpj, valor), encoding="utf-8")
        created.append(path)

    return created


if __name__ == "__main__":
    files = generate()
    print(f"Gerados {len(files)} XML(s) em {config.DEMO_INBOX_DIR}")
