"""Classe de base pour les formatters de sortie."""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseFormatter(ABC):
    """Classe abstraite pour les formatters."""
    
    @abstractmethod
    def format(self, results: Dict[str, Any]) -> str:
        """
        Formate les résultats pour l'affichage.
        
        Args:
            results: Résultats de l'analyse
        
        Returns:
            Chaîne formatée prête à afficher
        """
        pass
    
    @abstractmethod
    def save(self, results: Dict[str, Any], filepath: str) -> None:
        """
        Sauvegarde les résultats dans un fichier.
        
        Args:
            results: Résultats de l'analyse
            filepath: Chemin du fichier de sortie
        """
        pass
