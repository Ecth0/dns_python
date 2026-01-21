"""Formatter pour sortie texte/Markdown."""
from typing import Dict, Any
from collections import defaultdict
from .base_formatter import BaseFormatter


class TextFormatter(BaseFormatter):
    """Formate les résultats en texte lisible / Markdown."""
    
    def format(self, results: Dict[str, Any]) -> str:
        """Génère un rapport texte complet."""
        output = []
        
        # En-tête
        output.append("=" * 80)
        output.append(f"📊 RAPPORT D'ANALYSE DNS - {results['initial_domain']}")
        output.append("=" * 80)
        output.append("")
        
        # Statistiques
        stats = results['stats']
        output.append("## 📈 Statistiques")
        output.append("")
        output.append(f"- **Domaines découverts** : {stats['total_domains']}")
        output.append(f"- **Adresses IP découvertes** : {stats['total_ips']}")
        output.append(f"- **Relations découvertes** : {stats['total_relationships']}")
        output.append("")
        
        # Domaines par type de découverte
        output.append("## 🌐 Domaines découverts")
        output.append("")
        
        # Groupe par source
        by_source = defaultdict(list)
        for rel in results['relationships']:
            if rel['type'] == 'domain':
                by_source[rel['source']].append(rel['to'])
        
        for source, domains in sorted(by_source.items()):
            output.append(f"### Via {source}")
            for domain in sorted(set(domains))[:10]:  # Limite à 10
                output.append(f"  - {domain}")
            if len(set(domains)) > 10:
                output.append(f"  - ... et {len(set(domains)) - 10} autres")
            output.append("")
        
        # IPs découvertes
        output.append("## 🔢 Adresses IP")
        output.append("")
        
        # Sépare IPv4 et IPv6
        ipv4 = [ip for ip in results['ips'] if ':' not in ip]
        ipv6 = [ip for ip in results['ips'] if ':' in ip]
        
        if ipv4:
            output.append("### IPv4")
            for ip in sorted(ipv4)[:20]:
                output.append(f"  - {ip}")
            if len(ipv4) > 20:
                output.append(f"  - ... et {len(ipv4) - 20} autres")
            output.append("")
        
        if ipv6:
            output.append("### IPv6")
            for ip in sorted(ipv6)[:20]:
                output.append(f"  - {ip}")
            if len(ipv6) > 20:
                output.append(f"  - ... et {len(ipv6) - 20} autres")
            output.append("")
        
        # Arbre de relations (simplifié)
        output.append("## 🌳 Arbre des relations (extrait)")
        output.append("")
        output.append(self._build_tree(results['graph'], results['initial_domain'], max_depth=2))
        
        output.append("")
        output.append("=" * 80)
        
        return "\n".join(output)
    
    def _build_tree(self, graph: Dict, node: str, indent: str = "", max_depth: int = 3, current_depth: int = 0, visited: set = None) -> str:
        """Construit un arbre textuel des relations."""
        if visited is None:
            visited = set()
        
        if current_depth >= max_depth or node in visited:
            return ""
        
        visited.add(node)
        output = [f"{indent}├─ {node}"]
        
        if node in graph:
            children = graph[node][:5]  # Limite à 5 enfants
            for i, child in enumerate(children):
                child_node = child['value']
                is_last = i == len(children) - 1
                new_indent = indent + ("   " if is_last else "│  ")
                subtree = self._build_tree(graph, child_node, new_indent, max_depth, current_depth + 1, visited)
                if subtree:
                    output.append(subtree)
            
            if len(graph[node]) > 5:
                output.append(f"{indent}│  └─ ... et {len(graph[node]) - 5} autres")
        
        return "\n".join(output)
    
    def save(self, results: Dict[str, Any], filepath: str) -> None:
        """Sauvegarde le rapport en fichier Markdown."""
        content = self.format(results)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Rapport sauvegardé : {filepath}")
