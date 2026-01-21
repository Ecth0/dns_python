"""Stratégies de découverte DNS."""
from .base import Strategy
from .txt_parser import TXTParserStrategy
from .tld_crawler import TLDCrawlerStrategy
from .srv_scanner import SRVScannerStrategy
from .reverse_dns import ReverseDNSStrategy
from .ip_neighbors import IPNeighborsStrategy
from .subdomain_enum import SubdomainEnumStrategy
__all__ = ['Strategy']


# dns_mapper/strategies/base.py
"""
Classe de base pour toutes les stratégies de découverte.
Utilise le pattern Strategy pour rendre le code extensible.
"""
from abc import ABC, abstractmethod
from typing import Set, Dict, Any


class Strategy(ABC):
    """Classe abstraite pour les stratégies de découverte DNS."""
    
    def __init__(self, exclude_domains: Set[str] = None):
        """
        Initialise la stratégie.
        
        Args:
            exclude_domains: Domaines à exclure des résultats
        """
        self.exclude_domains = exclude_domains or set()
    
    @abstractmethod
    def discover(self, target: str, context: Dict[str, Any]) -> Set[Dict[str, Any]]:
        """
        Découvre de nouvelles informations à partir d'une cible.
        
        Args:
            target: Domaine ou IP à analyser
            context: Contexte partagé (résultats précédents, etc.)
        
        Returns:
            Set de dictionnaires contenant:
                - type: 'domain' ou 'ip'
                - value: la valeur découverte
                - source: comment elle a été découverte
                - metadata: informations additionnelles
        """
        pass
    
    def should_exclude(self, domain: str) -> bool:
        """Vérifie si un domaine doit être exclu."""
        return any(excluded in domain for excluded in self.exclude_domains)
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nom de la stratégie pour les logs."""
        pass