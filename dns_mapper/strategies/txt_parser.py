"""
Stratégie de parsing des enregistrements TXT.
Extrait les IPs et domaines des enregistrements TXT.
"""
import re
from typing import Set, Dict, Any
from .base import Strategy
from ..dns_functions import query_dns, is_valid_domain, is_valid_ip


class TXTParserStrategy(Strategy):
    """Parse les enregistrements TXT pour trouver IPs et domaines."""
    
    # Regex pour trouver des domaines
    DOMAIN_PATTERN = re.compile(
        r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}'
    )
    
    # Regex pour IPv4
    IPV4_PATTERN = re.compile(
        r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    )
    
    # Regex pour IPv6
    IPV6_PATTERN = re.compile(
        r'(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|'
        r'::(?:[0-9a-fA-F]{1,4}:){0,6}[0-9a-fA-F]{1,4}'
    )
    
    @property
    def name(self) -> str:
        return "TXT Parser"
    
    def discover(self, target: str, context: Dict[str, Any]) -> Set[Dict[str, Any]]:
        """Parse les enregistrements TXT pour extraire domaines et IPs."""
        results = set()
        
        # Récupère tous les enregistrements TXT
        txt_records = query_dns(target, 'TXT')
        
        if not txt_records:
            return results
        
        # Affiche tous les TXT (même vides, pour OSINT)
        for record in txt_records:
            # Nettoie les guillemets
            record_clean = record.strip('"').strip("'")
            
            # Cherche des domaines
            domains = self.DOMAIN_PATTERN.findall(record_clean)
            for domain in domains:
                domain = domain.lower().rstrip('.')
                if is_valid_domain(domain) and not self.should_exclude(domain):
                    results.add(self._create_result(
                        'domain', domain, f'TXT record of {target}',
                        {'txt_content': record_clean[:100]}  # Limite pour lisibilité
                    ))
            
            # Cherche des IPv4
            ipv4s = self.IPV4_PATTERN.findall(record_clean)
            for ip in ipv4s:
                if is_valid_ip(ip):
                    results.add(self._create_result(
                        'ip', ip, f'TXT record of {target}',
                        {'version': 'v4', 'txt_content': record_clean[:100]}
                    ))
            
            # Cherche des IPv6
            ipv6s = self.IPV6_PATTERN.findall(record_clean)
            for ip in ipv6s:
                if is_valid_ip(ip):
                    results.add(self._create_result(
                        'ip', ip, f'TXT record of {target}',
                        {'version': 'v6', 'txt_content': record_clean[:100]}
                    ))
        
        return results
    
    def _create_result(self, type_: str, value: str, source: str,
                      metadata: Dict[str, Any]) -> tuple:
        """Crée un tuple de résultat hashable."""
        return (type_, value, source, tuple(sorted(metadata.items())))