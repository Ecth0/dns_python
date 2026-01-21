"""
Moteur de récursion optimisé.
Version rapide avec moins de prints.
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
            exclude_domains: Domaines à exclure
        """
        self.strategies = strategies
        self.max_depth = max_depth
        self.exclude_domains = exclude_domains or set()
        
        # Suivi des éléments visités
        self.visited = set()
        
        # Graphe des relations
        self.graph = defaultdict(list)
        
        # Tous les résultats
        self.all_results = {
            'domains': set(),
            'ips': set(),
            'relationships': []
        }
        
        # Compteur pour affichage minimal
        self.discovery_count = 0
    
    def analyze(self, initial_domain: str) -> Dict[str, Any]:
        """Lance l'analyse récursive."""
        print(f"Analyse de {initial_domain}...")
        
        # Réinitialise
        self.visited.clear()
        self.graph.clear()
        self.all_results = {
            'domains': set(),
            'ips': set(),
            'relationships': []
        }
        self.discovery_count = 0
        
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
        """Analyse récursive d'une cible."""
        # Vérifie la profondeur
        if depth > self.max_depth:
            return
        
        # Évite les cycles
        if target in self.visited:
            return
        
        self.visited.add(target)
        
        # Affichage minimal (seulement depth 0 et 1)
        if depth <= 1:
            indent = "  " * depth
            print(f"{indent}[depth {depth}] {target}")
        
        # Contexte partagé
        context = {
            'depth': depth,
            'parent': parent,
            'visited': self.visited,
        }
        
        # Exécute les stratégies
        discovered = []
        for strategy in self.strategies:
            try:
                results = strategy.discover(target, context)
                
                for result in results:
                    # Normalise le résultat
                    if isinstance(result, tuple):
                        result_type = result[0]
                        result_value = result[1]
                        result_source = result[2]
                        result_metadata = dict(result[3]) if len(result) > 3 else {}
                    else:
                        result_type = result.get('type')
                        result_value = result.get('value')
                        result_source = result.get('source')
                        result_metadata = dict(result.get('metadata', {})) if isinstance(result.get('metadata'), tuple) else result.get('metadata', {})
                    
                    # Ajoute aux résultats
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
                    
                    # Compteur
                    self.discovery_count += 1
                    
                    # Affiche un point tous les 20 résultats
                    if self.discovery_count % 20 == 0:
                        print(".", end="", flush=True)
                    
            except Exception as e:
                # Affiche les erreurs seulement en depth 0
                if depth == 0:
                    print(f"  [WARNING] Erreur avec {strategy.name}: {e}")
        
        # Récursion sur les découvertes
        for discovered_item in discovered:
            if discovered_item not in self.visited:
                self._recursive_analyze(discovered_item, depth + 1, parent=target)