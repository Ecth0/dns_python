"""
Stratégie IP Neighbors.
Scanne les IPs voisines pour trouver d'autres domaines.
"""
import ipaddress
from typing import Set, Dict, Any
from .base import Strategy
from ..dns_functions import reverse_dns, is_valid_ip


class IPNeighborsStrategy(Strategy):
    """Scanne les IPs adjacentes pour découvrir des domaines voisins."""
    
    def __init__(self, exclude_domains: Set[str] = None, scan_range: int = 5):
        """
        Initialise la stratégie.
        
        Args:
            exclude_domains: Domaines à exclure
            scan_range: Nombre d'IPs à scanner de chaque côté (défaut: 5)
        """
        super().__init__(exclude_domains)
        self.scan_range = scan_range
    
    @property
    def name(self) -> str:
        return "IP Neighbors"
    
    def discover(self, target: str, context: Dict[str, Any]) -> Set[Dict[str, Any]]:
        """
        Scanne les IPs adjacentes.
        
        Exemple:
            dig A m6.fr +short → 92.61.160.137
            dig -x 92.61.160.136 +short → rev-160-136.rtl.fr.
            dig -x 92.61.160.138 +short → rev-160-138.rtl.fr.
        """
        results = set()
        
        # Vérifie si c'est une IP valide
        if not is_valid_ip(target):
            return results
        
        try:
            ip_obj = ipaddress.ip_address(target)
        except ValueError:
            return results
        
        # Scanne les IPs voisines
        for offset in range(-self.scan_range, self.scan_range + 1):
            if offset == 0:
                continue  # Skip l'IP elle-même
            
            try:
                # Calcule l'IP voisine
                neighbor_ip = ip_obj + offset
                neighbor_str = str(neighbor_ip)
                
                # Ajoute l'IP aux résultats
                results.add(self._create_result(
                    'ip',
                    neighbor_str,
                    f'Neighbor of {target}',
                    {'offset': offset, 'distance': abs(offset)}
                ))
                
                # Tente un reverse DNS
                ptr_domain = reverse_dns(neighbor_str)
                if ptr_domain and not self.should_exclude(ptr_domain):
                    results.add(self._create_result(
                        'domain',
                        ptr_domain,
                        f'Reverse DNS of neighbor {neighbor_str}',
                        {'neighbor_ip': neighbor_str, 'offset': offset}
                    ))
                    
            except (ipaddress.AddressValueError, OverflowError):
                # IP hors limites (ex: 255.255.255.255 + 1)
                continue
        
        return results
    
    def _create_result(self, type_: str, value: str, source: str,
                      metadata: Dict[str, Any]) -> tuple:
        """Crée un tuple de résultat hashable."""
        return (type_, value, source, tuple(sorted(metadata.items())))
