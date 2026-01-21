"""
Stratégie Reverse DNS.
Résout les IPs en noms de domaine via reverse DNS (PTR).
"""
from typing import Set, Dict, Any
from .base import Strategy
from ..dns_functions import reverse_dns, query_dns, is_valid_ip, is_valid_domain


class ReverseDNSStrategy(Strategy):
    """Effectue des résolutions DNS inverses sur les IPs."""
    
    @property
    def name(self) -> str:
        return "Reverse DNS"
    
    def discover(self, target: str, context: Dict[str, Any]) -> Set[Dict[str, Any]]:
        """
        Résout un domaine en IP, puis l'IP en domaine via reverse DNS.
        
        Exemple:
            dig A se.com +short
            → 34.227.236.7
            dig -x 34.227.236.7 +short
            → ec2-34-227-236-7.compute-1.amazonaws.com.
        """
        results = set()
        
        # Si c'est déjà une IP, on fait directement le reverse
        if is_valid_ip(target):
            ptr_domain = reverse_dns(target)
            if ptr_domain and not self.should_exclude(ptr_domain):
                results.add(self._create_result(
                    'domain',
                    ptr_domain,
                    f'Reverse DNS of {target}',
                    {'ip': target}
                ))
            return results
        
        # Sinon, on résout le domaine en IPs puis on fait le reverse
        if not is_valid_domain(target):
            return results
        
        # Récupère les IPs (A et AAAA)
        ips = []
        ips.extend(query_dns(target, 'A'))
        ips.extend(query_dns(target, 'AAAA'))
        
        for ip in ips:
            ip = ip.strip()
            
            # Ajoute l'IP aux résultats
            results.add(self._create_result(
                'ip',
                ip,
                f'A/AAAA record of {target}',
                {'version': 'v6' if ':' in ip else 'v4'}
            ))
            
            # Reverse DNS sur l'IP
            ptr_domain = reverse_dns(ip)
            if ptr_domain and not self.should_exclude(ptr_domain):
                results.add(self._create_result(
                    'domain',
                    ptr_domain,
                    f'Reverse DNS of {ip} (from {target})',
                    {'ip': ip, 'original_domain': target}
                ))
        
        return results
    
    def _create_result(self, type_: str, value: str, source: str,
                      metadata: Dict[str, Any]) -> tuple:
        """Crée un tuple de résultat hashable."""
        return (type_, value, source, tuple(sorted(metadata.items())))
