"""Ponto de entrada do pipeline demo."""

import argparse
import sys

from loguru import logger

from demo.generate_samples import generate
from nf_agent.processor import process_inbox


def main() -> int:
    parser = argparse.ArgumentParser(description="Finance Ops Automation — modo demo")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Limpa output anterior antes de processar",
    )
    parser.add_argument(
        "--skip-generate",
        action="store_true",
        help="Não regenera XMLs fictícios em demo/inbox",
    )
    args = parser.parse_args()

    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")

    if not args.skip_generate:
        files = generate()
        logger.info(f"Demo: {len(files)} XML(s) sintéticos gerados")

    stats = process_inbox(reset_output=args.reset)
    print("\n--- Resumo ---")
    for key, value in stats.items():
        print(f"{key}: {value}")
    print("\nPróximo passo: python create_database.py && python run_queries.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
