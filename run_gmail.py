"""NF Agent — modo Gmail (produção)."""

import argparse
import sys

from loguru import logger


def main() -> int:
    parser = argparse.ArgumentParser(description="NF Agent — processamento via Gmail API")
    parser.add_argument(
        "--query",
        default=None,
        help="Query Gmail customizada (padrão: GMAIL_SEARCH_QUERY do .env)",
    )
    args = parser.parse_args()

    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")

    try:
        from nf_agent.gmail_processor import process_gmail
    except ImportError as exc:
        logger.error(
            "Dependências Gmail não instaladas. Rode: pip install -r requirements-gmail.txt"
        )
        raise SystemExit(1) from exc

    stats = process_gmail(query=args.query)
    print("\n--- NF Agent (Gmail) ---")
    for key, value in stats.items():
        print(f"{key}: {value}")
    print("\nPróximo passo: python create_database.py && python run_queries.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
