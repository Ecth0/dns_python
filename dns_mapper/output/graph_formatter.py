"""Formatter pour graphes Graphviz (DOT)."""
from typing import Dict, Any
from .base_formatter import BaseFormatter


class GraphFormatter(BaseFormatter):
    """Génère des graphes au format DOT (Graphviz)."""
    
    def format(self, results: Dict[str, Any]) -> str:
        """Génère un fichier DOT pour Graphviz."""
        output = []
        
        # En-tête DOT
        output.append('digraph DNS_Map {')
        output.append('  // Configuration')
        output.append('  rankdir=LR;')
        output.append('  node [shape=box, style=rounded];')
        output.append('  edge [color=gray];')
        output.append('')
        
        # Nœud racine
        initial = results['initial_domain']
        output.append(f'  "{initial}" [fillcolor=lightblue, style="rounded,filled"];')
        output.append('')
        
        # Groupes par type
        domains = set()
        ips = set()
        
        for rel in results['relationships']:
            if rel['type'] == 'domain':
                domains.add(rel['to'])
            elif rel['type'] == 'ip':
                ips.add(rel['to'])
        
        # Déclare les nœuds domaines
        output.append('  // Domaines')
        for domain in sorted(domains):
            safe_domain = domain.replace('.', '_').replace('-', '_')
            output.append(f'  "{domain}" [fillcolor=lightgreen, style="rounded,filled"];')
        output.append('')
        
        # Déclare les nœuds IPs
        output.append('  // Adresses IP')
        for ip in sorted(ips):
            output.append(f'  "{ip}" [fillcolor=lightyellow, style="rounded,filled", shape=ellipse];')
        output.append('')
        
        # Relations
        output.append('  // Relations')
        seen_edges = set()
        for rel in results['relationships'][:200]:  # Limite pour lisibilité
            edge = (rel['from'], rel['to'])
            if edge not in seen_edges:
                label = rel['source'].split(' ')[0]  # Premier mot
                output.append(f'  "{rel["from"]}" -> "{rel["to"]}" [label="{label}"];')
                seen_edges.add(edge)
        
        output.append('}')
        
        return '\n'.join(output)
    
    def save(self, results: Dict[str, Any], filepath: str) -> None:
        """Sauvegarde le graphe DOT."""
        content = self.format(results)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Graphe DOT sauvegardé : {filepath}")
        print(f"💡 Générez l'image avec : dot -Tpng {filepath} -o output.png")
