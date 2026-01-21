"""
Moteur de récursion pour orchestrer les stratégies.
Gère la profondeur, les cycles, et l'exécution des stratégies.
VERSION CORRIGÉE - Gère les résultats tuple et dict.
"""
from typing import Set, Dict, Any, List
from collections import defaultdict


class RecursiveEngine:
    """Orchestre l'exécution récursive des stratégies."""
    
    def __init__(self, strategies: List, max_depth: int = 3, exclude_domains: Set[str] = None):
        """
        Initialise le moteur.
        
        Args:
            strategies: Liste des stratégies à utiliser
            max_depth: Profondeur maximale de récursion
            exclude_domains: Domaines à exclure (akamai, cloudfront, etc.)
        """
        self.strategies = strategies
        self.max_depth = max_depth
        self.exclude_domains = exclude_domains or set()
        
        # Suivi des éléments déjà visités pour éviter les cycles
        self.visited = set()
        
        # Graphe des relations (pour l'affichage)
        self.graph = defaultdict(list)
        
        # Tous les résultats collectés
        self.all_results = {
            'domains': set(),
            'ips': set(),
            'relationships': []
        }
    
    def analyze(self, initial_domain: str) -> Dict[str, Any]:
        """
        Lance l'analyse récursive d'un domaine.
        
        Args:
            initial_domain: Domaine de départ
        
        Returns:
            Dictionnaire avec tous les résultats
        """
        print(f"🔍 Analyse de {initial_domain}...")
        
        # Réinitialise l'état
        self.visited.clear()
        self.graph.clear()
        self.all_results = {
            'domains': set(),
            'ips': set(),
            'relationships': []
        }
        
        # Lance la récursion
        self._recursive_analyze(initial_domain, depth=0, parent=None)
        
        return {
            'initial_domain': initial_domain,
            'domains': sorted(self.all_results['domains']),
            'ips': sorted(self.all_results['ips']),
            'relationships': self.all_results['relationships'],
            'graph': dict(self.graph),
            'stats': {
                'total_domains': len(self.all_results['domains']),
                'total_ips': len(self.all_results['ips']),
                'total_relationships': len(self.all_results['relationships']),
            }
        }
    
    def _recursive_analyze(self, target: str, depth: int, parent: str = None):
        """
        Analyse récursive d'une cible.
        
        Args:
            target: Domaine ou IP à analyser
            depth: Profondeur actuelle
            parent: Cible parente (pour le graphe)
        """
        # Vérifie la profondeur maximale
        if depth > self.max_depth:
            return
        
        # Évite les cycles
        if target in self.visited:
            return
        
        self.visited.add(target)
        
        # Affiche la progression
        indent = "  " * depth
        print(f"{indent}├─ {target} (depth: {depth})")
        
        # Contexte partagé entre les stratégies
        context = {
            'depth': depth,
            'parent': parent,
            'visited': self.visited,
        }
        
        # Exécute chaque stratégie
        discovered = []
        for strategy in self.strategies:
            try:
                results = strategy.discover(target, context)
                
                for result in results:
                    # Normalise le résultat (peut être tuple ou dict)
                    if isinstance(result, tuple):
                        # Format: (type, value, source, metadata_tuple)
                        result_type = result[0]
                        result_value = result[1]
                        result_source = result[2]
                        result_metadata = dict(result[3]) if len(result) > 3 else {}
                    else:
                        # Format dict
                        result_type = result.get('type')
                        result_value = result.get('value')
                        result_source = result.get('source')
                        result_metadata = dict(result.get('metadata', {})) if isinstance(result.get('metadata'), tuple) else result.get('metadata', {})
                    
                    # Ajoute aux résultats globaux
                    if result_type == 'domain':
                        self.all_results['domains'].add(result_value)
                    elif result_type == 'ip':
                        self.all_results['ips'].add(result_value)
                    
                    # Ajoute la relation
                    relationship = {
                        'from': target,
                        'to': result_value,
                        'type': result_type,
                        'source': result_source,
                        'depth': depth,
                    }
                    self.all_results['relationships'].append(relationship)
                    
                    # Ajoute au graphe
                    self.graph[target].append({
                        'value': result_value,
                        'type': result_type,
                        'source': result_source,
                    })
                    
                    # Prépare pour la récursion
                    discovered.append(result_value)
                    
            except Exception as e:
                print(f"{indent} Erreur avec {strategy.name}: {e}")
                # Décommenter pour debug :
                # import traceback
                # traceback.print_exc()
        
        # Récursion sur les éléments découverts
        for discovered_item in discovered:
            if discovered_item not in self.visited:
                self._recursive_analyze(discovered_item, depth + 1, parent=target)