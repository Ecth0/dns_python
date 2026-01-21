"""
Point d'entrée principal du DNS Mapper.
Utilise argparse pour respecter la culture UNIX.
"""
import argparse
import sys


def main():
    """Parse les arguments et lance l'analyse DNS."""
    parser = argparse.ArgumentParser(
        description='Cartographie DNS d\'un domaine',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'domain',
        help='Nom de domaine à analyser'
    )
    
    parser.add_argument(
        '-d', '--depth',
        type=int,
        default=3,
        help='Profondeur de récursion (défaut: 3)'
    )
    
    parser.add_argument(
        '-o', '--output',
        choices=['text', 'graph', 'both'],
        default='text',
        help='Format de sortie (défaut: text)'
    )
    
    parser.add_argument(
        '--exclude',
        nargs='+',
        default=[],
        help='Domaines à exclure (ex: akamai.com cloudfront.net)'
    )
    
    args = parser.parse_args()
    
    print(f"Analyse de {args.domain} en cours...")
    # TODO: Implémenter l'analyse
    

if __name__ == '__main__':
    main()