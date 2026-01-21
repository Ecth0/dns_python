from typing import Set, Dict, Any
from .base import Strategy
from ..dns_functions import query_dns, is_valid_domain


class SRVScannerStrategy(Strategy):
    """Scanne les enregistrements SRV pour trouver des services."""
    
    # Liste des services SRV connus (RFC 2782)
    COMMON_SERVICES = [
        # SIP / VoIP
        ('_sip', '_tcp'),
        ('_sip', '_udp'),
        ('_sips', '_tcp'),
        
        # XMPP / Jabber
        ('_xmpp-client', '_tcp'),
        ('_xmpp-server', '_tcp'),
        ('_jabber', '_tcp'),
        
        # Email
        ('_submission', '_tcp'),
        ('_imap', '_tcp'),
        ('_imaps', '_tcp'),
        ('_pop3', '_tcp'),
        ('_pop3s', '_tcp'),
        
        # LDAP
        ('_ldap', '_tcp'),
        ('_ldaps', '_tcp'),
        ('_gc', '_tcp'),  # Global Catalog
        
        # Kerberos
        ('_kerberos', '_tcp'),
        ('_kerberos', '_udp'),
        ('_kerberos-master', '_tcp'),
        ('_kerberos-master', '_udp'),
        ('_kpasswd', '_tcp'),
        ('_kpasswd', '_udp'),
        
        # CalDAV / CardDAV
        ('_caldav', '_tcp'),
        ('_caldavs', '_tcp'),
        ('_carddav', '_tcp'),
        ('_carddavs', '_tcp'),
        
        # Microsoft services
        ('_sipfederationtls', '_tcp'),
        ('_autodiscover', '_tcp'),
        
        # Autres
        ('_matrix', '_tcp'),
        ('_minecraft', '_tcp'),
        ('_teamspeak', '_udp'),
    ]
    
    @property
    def name(self) -> str:
        return "SRV Scanner"
    
    def discover(self, target: str, context: Dict[str, Any]) -> Set[Dict[str, Any]]:
        """
        Scanne les enregistrements SRV pour découvrir des services.
        
        Exemple:
            dig SRV _sip._tcp.se.com +short
            → 0 0 443 sipdir.online.lync.com.
        """
        results = set()
        
        if not is_valid_domain(target):
            return results
        
        # Teste chaque combinaison service/protocole
        for service, protocol in self.COMMON_SERVICES:
            srv_query = f"{service}.{protocol}.{target}"
            
            srv_records = query_dns(srv_query, 'SRV')
            
            for record in srv_records:
                # Format SRV: priority weight port target
                # Exemple: "0 0 443 sipdir.online.lync.com."
                parts = record.split()
                
                if len(parts) >= 4:
                    priority, weight, port, srv_target = parts[0], parts[1], parts[2], parts[3]
                    srv_target = srv_target.rstrip('.')
                    
                    if is_valid_domain(srv_target) and not self.should_exclude(srv_target):
                        results.add(self._create_result(
                            'domain',
                            srv_target,
                            f'SRV record {srv_query}',
                            {
                                'service': service,
                                'protocol': protocol,
                                'priority': priority,
                                'weight': weight,
                                'port': port,
                            }
                        ))
        
        return results
    
    def _create_result(self, type_: str, value: str, source: str,
                      metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un dictionnaire de résultat hashable."""
        return {
            'type': type_,
            'value': value,
            'source': source,
            'metadata': tuple(sorted(metadata.items()))
        }
