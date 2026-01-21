"""
Point d'entrée principal du DNS Mapper.
Utilise argparse pour respecter la culture UNIX.
"""
import argparse
import sys
from dns_mapper.strategies import (
    TXTParserStrategy,
    TLDCrawlerStrategy,
    SRVScannerStrategy,
    ReverseDNSStrategy,
    IPNeighborsStrategy,
    SubdomainEnumStrategy,
)
from dns_mapper.core.recursive_engine import RecursiveEngine
from dns_mapper.output import TextFormatter, GraphFormatter


def main():
    """Parse les arguments et lance l'analyse DNS."""
    parser = argparse.ArgumentParser(
        description="Cartographie DNS d'un domaine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "domain",
        help="Nom de domaine à analyser",
    )

    parser.add_argument(
        "-d",
        "--depth",
        type=int,
        default=2,
        help="Profondeur de récursion (défaut: 2)",
    )

    parser.add_argument(
        "-o",
        "--output",
        choices=["text", "graph", "both"],
        default="text",
        help="Format de sortie (défaut: text)",
    )

    parser.add_argument(
        "--exclude",
        nargs="+",
        default=["cloudfront.net", "akamai.net", "fastly.net"],
        help="Domaines à exclure (ex: akamai.com cloudfront.net)",
    )

    parser.add_argument(
        "--scan-range",
        type=int,
        default=3,
        help="Nombre d'IPs voisines à scanner (défaut: 3)",
    )

    args = parser.parse_args()

    print(f"🔍 Analyse de {args.domain}")
    print(f"📊 Profondeur: {args.depth}")
    print(f"🚫 Exclusions: {', '.join(args.exclude)}")
    print("-" * 60)

    # Crée les stratégies
    exclude_set = set(args.exclude)
    strategies = [
        TXTParserStrategy(exclude_set),
        TLDCrawlerStrategy(exclude_set),
        SRVScannerStrategy(exclude_set),
        ReverseDNSStrategy(exclude_set),
        IPNeighborsStrategy(exclude_set, scan_range=args.scan_range),
        SubdomainEnumStrategy(exclude_set),
    ]

    # Crée et lance le moteur
    engine = RecursiveEngine(
        strategies=strategies,
        max_depth=args.depth,
        exclude_domains=exclude_set,
    )

    try:
        results = engine.analyze(args.domain)

        # Affichage selon le format choisi
        if args.output in ["text", "both"]:
            text_formatter = TextFormatter()
            print("\n" + text_formatter.format(results))

            # Sauvegarde en fichier
            output_file = f"{args.domain.replace('.', '_')}_report.md"
            text_formatter.save(results, output_file)

        if args.output in ["graph", "both"]:
            graph_formatter = GraphFormatter()
            dot_file = f"{args.domain.replace('.', '_')}_graph.dot"
            graph_formatter.save(results, dot_file)
            print(
                f"\n💡 Générez l'image avec : dot -Tpng {dot_file} -o graph.png"
            )

    except KeyboardInterrupt:
        print("\n\nAnalyse interrompue")
        sys.exit(1)
    except Exception as e:
        print(f"\nErreur: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
