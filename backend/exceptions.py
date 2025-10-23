"""
Exceptions personnalisées pour l'application CELESTE X
"""


class CelesteException(Exception):
    """Exception de base pour toutes les exceptions métier CELESTE"""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(CelesteException):
    """Erreur de validation des données d'entrée"""

    pass


class CalculationError(CelesteException):
    """Erreur lors d'un calcul mécanique"""

    pass


class CableNotFoundError(CelesteException):
    """Câble non trouvé dans la base de données"""

    pass


class DomainValidationError(CelesteException):
    """Erreur de validation du domaine CELESTE"""

    pass
