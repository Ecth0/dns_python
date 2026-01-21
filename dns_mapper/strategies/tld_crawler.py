"""
Stratégie Crawl to TLD.
Remonte la hiérarchie DNS jusqu'au TLD pour découvrir les domaines parents.
"""
from typing import Set, Dict, Any
from .base import Strategy
from ..dns_functions import query_dns, is_valid_domain


class TLDCrawlerStrategy(Strategy):
    """Remonte vers le TLD pour trouver les domaines parents."""
    
    # Liste des TLDs connus (simplifiée, peut être étendue)
    # Source : https://data.iana.org/TLD/tlds-alpha-by-domain.txt
    COMMON_TLDS = {
        'com', 'org', 'net', 'edu', 'gov', 'mil', 'int',
        'fr', 'de', 'uk', 'it', 'es', 'nl', 'be', 'ch',
        'ca', 'au', 'jp', 'cn', 'in', 'br', 'ru',
        # TLDs avec point
        'co.uk', 'gouv.fr', 'ac.uk', 'gov.uk', 'com.au',
        'co.jp', 'ne.jp', 'or.jp', 'go.jp',
    }
    
    @property
    def name(self) -> str:
        return "TLD Crawler"
    
    def discover(self, target: str, context: Dict[str, Any]) -> Set[Dict[str, Any]]:
        """
        Remonte la hiérarchie pour trouver les domaines parents.
        
        Exemple:
            sirena.integration.dev.atlas.fabrique.social.gouv.fr
            → integration.dev.atlas.fabrique.social.gouv.fr
            → dev.atlas.fabrique.social.gouv.fr
            → atlas.fabrique.social.gouv.fr
            → fabrique.social.gouv.fr
            → social.gouv.fr
            (s'arrête car gouv.fr est un TLD)
        """
        results = set()
        
        # Nettoie le domaine
        domain = target.lower().rstrip('.')
        
        if not is_valid_domain(domain):
            return results
        
        # Découpe le domaine en parties
        parts = domain.split('.')
        
        # Trouve le TLD (peut contenir un point comme gouv.fr)
        tld_index = self._find_tld_index(parts)
        
        if tld_index is None:
            # Pas de TLD connu, on s'arrête
            return results
        
        # Remonte la hiérarchie
        for i in range(len(parts) - tld_index - 1):
            # Construit le domaine parent
            parent_parts = parts[i + 1:]
            parent_domain = '.'.join(parent_parts)
            
            # Vérifie que ce n'est pas le TLD lui-même
            if self._is_tld(parent_domain):
                break
            
            # Vérifie que le domaine existe (au moins un enregistrement)
            if self._domain_exists(parent_domain) and not self.should_exclude(parent_domain):
                results.add(self._create_result(
                    'domain',
                    parent_domain,
                    f'Parent domain of {target}',
                    {'relationship': 'parent', 'levels_up': i + 1}
                ))
        
        return results
    
    def _find_tld_index(self, parts: list) -> int:
        """
        Trouve l'index du TLD dans les parties du domaine.
        Gère les TLDs avec point (gouv.fr, co.uk, etc.)
        
        Returns:
            Index du début du TLD, ou None si pas trouvé
        """
        # Vérifie d'abord les TLDs avec 2 parties (gouv.fr, co.uk)
        if len(parts) >= 2:
            two_part_tld = '.'.join(parts[-2:])
            if two_part_tld in self.COMMON_TLDS:
                return len(parts) - 2
        
        # Vérifie les TLDs simples
        if len(parts) >= 1:
            one_part_tld = parts[-1]
            if one_part_tld in self.COMMON_TLDS:
                return len(parts) - 1
        
        # TLD inconnu, on suppose que c'est le dernier élément
        return len(parts) - 1 if len(parts) > 0 else None
    
    def _is_tld(self, domain: str) -> bool:
        """Vérifie si un domaine est un TLD."""
        return domain in self.COMMON_TLDS
    
    def _domain_exists(self, domain: str) -> bool:
        """
        Vérifie si un domaine existe en testant plusieurs types d'enregistrements.
        """
        # Teste plusieurs types d'enregistrements
        for record_type in ['A', 'AAAA', 'MX', 'NS', 'SOA']:
            if query_dns(domain, record_type):
                return True
        return False
    
    def _create_result(self, type_: str, value: str, source: str,
                      metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un dictionnaire de résultat hashable."""
        return {
            'type': type_,
            'value': value,
            'source': source,
            'metadata': tuple(sorted(metadata.items()))
        }