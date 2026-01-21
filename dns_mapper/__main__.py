"""
Point d'entrée principal du DNS Mapper.
Version optimisée : rapide, colorée, sans emojis.
"""
import argparse
import sys
import time
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


# Codes couleur ANSI
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_colored(text, color=''):
    """Affiche du texte en couleur."""
    print(f"{color}{text}{Colors.ENDC}")


def print_banner():
    """Affiche une bannière."""
    banner = """
    ================================================================
                    DNS MAPPER - Cartographie DNS
                         Analyse d'infrastructure
    ================================================================
    """
    print_colored(banner, Colors.CYAN + Colors.BOLD)


def main():
    """Parse les arguments et lance l'analyse DNS."""
    parser = argparse.ArgumentParser(
        description='Cartographie DNS d\'un domaine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python -m dns_mapper google.com                    # Analyse rapide
  python -m dns_mapper google.com -d 2               # Profondeur 2
  python -m dns_mapper google.com -o both            # Texte + graphe
  python -m dns_mapper google.com --fast             # Mode ultra-rapide
        """
    )
    
    parser.add_argument('domain', help='Nom de domaine à analyser')
    parser.add_argument('-d', '--depth', type=int, default=1,
                       help='Profondeur de récursion (défaut: 1)')
    parser.add_argument('-o', '--output', choices=['text', 'graph', 'both'],
                       default='text', help='Format de sortie')
    parser.add_argument('--exclude', nargs='+',
                       default=['cloudfront.net', 'akamai.net', 'fastly.net', 
                               'amazonaws.com', 'azureedge.net'],
                       help='Domaines CDN à exclure')
    parser.add_argument('--scan-range', type=int, default=1,
                       help='IPs voisines à scanner (défaut: 1)')
    parser.add_argument('--fast', action='store_true',
                       help='Mode rapide (skip subdomain enum)')
    parser.add_argument('--no-color', action='store_true',
                       help='Désactive les couleurs')
    parser.add_argument('--quiet', action='store_true',
                       help='Mode silencieux (minimal output)')
    
    args = parser.parse_args()
    
    # Désactive les couleurs si demandé
    if args.no_color:
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, '')
    
    # Mode silencieux
    quiet = args.quiet
    
    # Bannière
    if not quiet:
        print_banner()
    
    # Mode rapide : ajustements automatiques
    if args.fast:
        args.scan_range = 1
        args.depth = min(args.depth, 1)
        if not quiet:
            print_colored("[MODE RAPIDE] Optimisations activées", Colors.YELLOW)
    
    # Informations de démarrage
    if not quiet:
        print()
        print_colored(f"[CIBLE]       {args.domain}", Colors.GREEN + Colors.BOLD)
        print_colored(f"[PROFONDEUR]  {args.depth}", Colors.BLUE)
        print_colored(f"[SCAN IP]     +/- {args.scan_range}", Colors.BLUE)
        print_colored(f"[EXCLUSIONS]  {len(args.exclude)} domaines", Colors.YELLOW)
        print_colored("-" * 60, Colors.CYAN)
    
    # Crée les stratégies
    exclude_set = set(args.exclude)
    strategies = [
        TXTParserStrategy(exclude_set),
        TLDCrawlerStrategy(exclude_set),
        SRVScannerStrategy(exclude_set),
        ReverseDNSStrategy(exclude_set),
        IPNeighborsStrategy(exclude_set, scan_range=args.scan_range),
    ]
    
    # Subdomain enum seulement si pas en mode rapide
    if not args.fast:
        strategies.append(SubdomainEnumStrategy(exclude_set))
    elif not quiet:
        print_colored("[INFO] Subdomain enumeration désactivée (--fast)", Colors.YELLOW)
    
    # Crée le moteur
    engine = RecursiveEngine(
        strategies=strategies,
        max_depth=args.depth,
        exclude_domains=exclude_set
    )
    
    # Désactive les prints du moteur en mode quiet
    if quiet:
        import os
        import sys
        sys.stdout = open(os.devnull, 'w')
    
    # Mesure le temps
    start_time = time.time()
    
    try:
        if not quiet:
            print()
            print_colored("[DEBUT] Analyse en cours...", Colors.GREEN)
            print()
        
        results = engine.analyze(args.domain)
        
        # Réactive stdout
        if quiet:
            sys.stdout = sys.__stdout__
        
        elapsed = time.time() - start_time
        
        # Résultats
        print_colored("\n" + "=" * 60, Colors.CYAN)
        print_colored("RESULTATS DE L'ANALYSE", Colors.HEADER + Colors.BOLD)
        print_colored("=" * 60, Colors.CYAN)
        
        stats = results['stats']
        print()
        print_colored(f"[TERMINE]     {elapsed:.1f} secondes", Colors.GREEN)
        print_colored(f"[DOMAINES]    {stats['total_domains']} découverts", Colors.BLUE)
        print_colored(f"[IP]          {stats['total_ips']} découvertes", Colors.BLUE)
        print_colored(f"[RELATIONS]   {stats['total_relationships']}", Colors.BLUE)
        
        # Aperçu rapide (seulement si pas quiet)
        if not quiet and results['domains']:
            print()
            print_colored("[APERCU DOMAINES] (5 premiers):", Colors.CYAN)
            for domain in sorted(results['domains'])[:5]:
                print(f"  - {domain}")
            if len(results['domains']) > 5:
                print(f"  ... et {len(results['domains']) - 5} autres")
        
        if not quiet and results['ips']:
            print()
            print_colored("[APERCU IP] (5 premières):", Colors.CYAN)
            for ip in sorted(results['ips'])[:5]:
                print(f"  - {ip}")
            if len(results['ips']) > 5:
                print(f"  ... et {len(results['ips']) - 5} autres")
        
        # Génération des rapports
        print()
        print_colored("-" * 60, Colors.CYAN)
        print_colored("[RAPPORTS] Génération...", Colors.GREEN)
        print()
        
        if args.output in ['text', 'both']:
            text_formatter = TextFormatter()
            output_file = f"{args.domain.replace('.', '_')}_report.md"
            text_formatter.save(results, output_file)
            print_colored(f"[OK] Rapport Markdown : {output_file}", Colors.GREEN)
        
        if args.output in ['graph', 'both']:
            graph_formatter = GraphFormatter()
            dot_file = f"{args.domain.replace('.', '_')}_graph.dot"
            graph_formatter.save(results, dot_file)
            print_colored(f"[OK] Graphe DOT : {dot_file}", Colors.GREEN)
            print_colored(f"[INFO] Générer image : dot -Tpng {dot_file} -o graph.png", Colors.YELLOW)
        
        print()
        print_colored("=" * 60, Colors.CYAN)
        print_colored("[SUCCESS] Analyse terminée", Colors.GREEN + Colors.BOLD)
        print_colored("=" * 60 + "\n", Colors.CYAN)
        
    except KeyboardInterrupt:
        if quiet:
            sys.stdout = sys.__stdout__
        print_colored("\n\n[INTERROMPU] Arrêt par l'utilisateur", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        if quiet:
            sys.stdout = sys.__stdout__
        print_colored(f"\n[ERREUR] {e}", Colors.RED)
        if '--debug' in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()