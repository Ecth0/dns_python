"""
Utilitaires pour les requêtes DNS.
Wrapper autour de dnspython pour simplifier les requêtes.
"""
import dns.resolver
import dns.reversename
from typing import List, Optional


def query_dns(domain: str, record_type: str) -> List[str]:
    """
    Effectue une requête DNS et retourne les résultats.
    
    Args:
        domain: Nom de domaine à interroger
        record_type: Type d'enregistrement (A, AAAA, MX, TXT, etc.)
    
    Returns:
        Liste des réponses (vide si erreur)
    """
    try:
        answers = dns.resolver.resolve(domain, record_type)
        return [str(rdata) for rdata in answers]
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, 
            dns.resolver.NoNameservers, dns.exception.Timeout):
        return []
    except Exception as e:
        # Log l'erreur mais continue
        print(f"Erreur DNS pour {domain} ({record_type}): {e}")
        return []


def reverse_dns(ip: str) -> Optional[str]:
    """
    Effectue une résolution DNS inverse.
    
    Args:
        ip: Adresse IP (v4 ou v6)
    
    Returns:
        Nom de domaine ou None
    """
    try:
        addr = dns.reversename.from_address(ip)
        answers = dns.resolver.resolve(addr, 'PTR')
        return str(answers[0]).rstrip('.')
    except Exception:
        return None


def is_valid_domain(domain: str) -> bool:
    """Vérifie si une chaîne ressemble à un nom de domaine valide."""
    if not domain or len(domain) > 253:
        return False
    
    # Simple validation (peut être améliorée)
    parts = domain.rstrip('.').split('.')
    return len(parts) >= 2 and all(
        part and len(part) <= 63 and part[0].isalnum() 
        for part in parts
    )


def is_valid_ip(ip: str) -> bool:
    """Vérifie si une chaîne est une IP valide (v4 ou v6)."""
    import ipaddress
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False