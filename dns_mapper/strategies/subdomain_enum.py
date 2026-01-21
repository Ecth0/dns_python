"""
Stratégie Subdomain Enumeration.
Bruteforce de sous-domaines courants.
"""
from typing import Set, Dict, Any
from .base import Strategy
from ..dns_functions import query_dns, is_valid_domain


class SubdomainEnumStrategy(Strategy):
    """Énumère les sous-domaines courants."""
    
    # Liste de sous-domaines courants à tester
    COMMON_SUBDOMAINS = [
        'www', 'mail', 'ftp', 'smtp', 'pop', 'imap',
        'webmail', 'admin', 'test', 'dev', 'staging',
        'preprod', 'prod', 'api', 'app', 'mobile',
        'blog', 'shop', 'store', 'forum', 'support',
        'help', 'docs', 'cdn', 'static', 'assets',
        'img', 'images', 'video', 'media', 'download',
        'vpn', 'remote', 'ssh', 'ftp', 'sftp',
        'git', 'gitlab', 'jenkins', 'ci', 'cd',
        'status', 'monitor', 'grafana', 'prometheus',
        'cloud', 'portal', 'intranet', 'extranet',
        'owa', 'exchange', 'autodiscover', 'lyncdiscover',
        'sip', 'voip', 'conference', 'meet', 'zoom',
        'ns1', 'ns2', 'ns3', 'dns1', 'dns2',
        'mx1', 'mx2', 'relay', 'gateway',
        'localhost', 'demo', 'sandbox', 'beta',
        'old', 'new', 'legacy', 'v2', 'v3',
        'secure', 'ssl', 'tls', 'vpn',
        'news', 'events', 'community', 'jobs',
        'careers', 'about', 'contact', 'service',
    ]
    
    @property
    def name(self) -> str:
        return "Subdomain Enum"
    
    def discover(self, target: str, context: Dict[str, Any]) -> Set[Dict[str, Any]]:
        """
        Teste des sous-domaines courants.
        
        Exemple:
            Connaissant tf1.fr, on devine www.tf1.fr, mail.tf1.fr, etc.
        """
        results = set()
        
        if not is_valid_domain(target):
            return results
        
        # Teste chaque sous-domaine
        for subdomain in self.COMMON_SUBDOMAINS:
            test_domain = f"{subdomain}.{target}"
            
            # Teste si le sous-domaine existe
            if self._subdomain_exists(test_domain) and not self.should_exclude(test_domain):
                results.add(self._create_result(
                    'domain',
                    test_domain,
                    f'Subdomain enumeration of {target}',
                    {'subdomain': subdomain, 'method': 'bruteforce'}
                ))
                
                # Récupère aussi les CNAME si présents
                cnames = query_dns(test_domain, 'CNAME')
                for cname in cnames:
                    cname = cname.rstrip('.')
                    if is_valid_domain(cname) and not self.should_exclude(cname):
                        results.add(self._create_result(
                            'domain',
                            cname,
                            f'CNAME of {test_domain}',
                            {'cname_source': test_domain}
                        ))
        
        return results
    
    def _subdomain_exists(self, domain: str) -> bool:
        """Vérifie si un sous-domaine existe."""
        # Teste plusieurs types d'enregistrements
        for record_type in ['A', 'AAAA', 'CNAME']:
            if query_dns(domain, record_type):
                return True
        return False
    
    def _create_result(self, type_: str, value: str, source: str,
                      metadata: Dict[str, Any]) -> tuple:
        """Crée un tuple de résultat hashable."""
        return (type_, value, source, tuple(sorted(metadata.items())))
