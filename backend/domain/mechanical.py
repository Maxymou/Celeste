"""
Module de calculs mécaniques pour lignes électriques aériennes
Basé sur les formules RTE - Techniques Lignes et Calculs (2016)
"""
import math
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class CableProperties:
    """Propriétés d'un câble"""
    name: str
    mass_lin_kg_per_m: float  # Masse linéique (kg/m)
    E_MPa: float  # Module d'élasticité (MPa)
    section_mm2: float  # Section (mm²)
    alpha_1e6_per_C: float  # Coefficient de dilatation thermique (×10⁻⁶/°C)
    rupture_dan: float  # Charge de rupture (daN)
    diameter_mm: float  # Diamètre (mm)


@dataclass
class SpanGeometry:
    """Géométrie d'une portée"""
    a: float  # Longueur portée horizontale (m)
    h: float  # Dénivelé entre supports (m), positif si support B plus haut
    
    @property
    def b(self) -> float:
        """Longueur de la corde (m)"""
        return math.sqrt(self.a**2 + self.h**2)


@dataclass
class SpanResult:
    """Résultats de calcul pour une portée"""
    # Géométrie
    b: float  # Corde (m)
    F1: float  # Flèche médiane (m)
    F2: float  # Flèche au point bas (m)
    H: float  # Creux total (m)
    
    # Tensions
    T0: float  # Tension horizontale (daN)
    TA: float  # Tension au support A (bas) (daN)
    TB: float  # Tension au support B (haut) (daN)
    
    # Validations
    warnings: List[str]
    errors: List[str]


class MechanicalCalculator:
    """Calculateur mécanique pour lignes électriques"""
    
    G = 9.81  # Gravité (m/s²)
    
    @staticmethod
    def validate_celeste_domain(a1: float, a2: float, h_max: float) -> List[str]:
        """
        Valide le domaine d'application mécanique CELESTE
        
        Args:
            a1: Plus grande portée du canton (m)
            a2: Plus petite portée du canton (m)
            h_max: Dénivelé maximum du canton (m)
        
        Returns:
            Liste des erreurs de validation
        """
        errors = []
        
        ratio = a1 / a2 if a2 > 0 else 0
        h_ratio = h_max / a2 if a2 > 0 else 0
        
        if ratio < 3:
            if h_ratio > 0.8:
                errors.append(
                    f"Domaine CELESTE non respecté: h_max/a2 = {h_ratio:.2f} > 0.8 "
                    f"(pour a1/a2 = {ratio:.2f} < 3)"
                )
        else:
            if h_ratio > 0.4:
                errors.append(
                    f"Domaine CELESTE non respecté: h_max/a2 = {h_ratio:.2f} > 0.4 "
                    f"(pour a1/a2 = {ratio:.2f} ≥ 3)"
                )
        
        return errors
    
    @staticmethod
    def calculate_sag(geometry: SpanGeometry, rho: float) -> Tuple[float, float, float]:
        """
        Calcule les flèches selon les formules de la chaînette simplifiée
        
        Args:
            geometry: Géométrie de la portée
            rho: Paramètre de la chaînette (m)
        
        Returns:
            (F1, F2, H) où:
                F1 = flèche médiane (m)
                F2 = flèche au point bas (m)
                H = creux total (m)
        """
        a = geometry.a
        b = geometry.b
        h = geometry.h
        
        # F1 = (a × b) / (8 × ρ)
        F1 = (a * b) / (8 * rho)
        
        # F2 = F1 × (1 - (h / (4×F1))²)
        if F1 > 0:
            F2 = F1 * (1 - (h / (4 * F1))**2)
        else:
            F2 = 0
        
        # H = creux total
        H = F2 + abs(h)
        
        return F1, F2, H
    
    @staticmethod
    def calculate_tensions(
        geometry: SpanGeometry,
        cable: CableProperties,
        rho: float
    ) -> Tuple[float, float, float]:
        """
        Calcule les tensions dans le câble
        
        Args:
            geometry: Géométrie de la portée
            cable: Propriétés du câble
            rho: Paramètre de la chaînette (m)
        
        Returns:
            (T0, TA, TB) où:
                T0 = tension horizontale (daN)
                TA = tension au support bas (daN)
                TB = tension au support haut (daN)
        """
        omega = cable.mass_lin_kg_per_m
        g = MechanicalCalculator.G / 10  # Conversion en daN/kg
        
        # T0 = ρ × (ω × g)
        T0 = rho * omega * g
        
        # Calcul des flèches
        _, F2, H = MechanicalCalculator.calculate_sag(geometry, rho)
        
        # TA = (ρ + F2) × (ω × g)
        TA = (rho + F2) * omega * g
        
        # TB = (ρ + H) × (ω × g)
        TB = (rho + H) * omega * g
        
        return T0, TA, TB
    
    @staticmethod
    def calculate_equivalent_span(spans: List[float]) -> Tuple[float, float]:
        """
        Calcule la portée équivalente selon la méthode de Blondel
        
        Args:
            spans: Liste des longueurs de portées (m)
        
        Returns:
            (a_eq, K) où:
                a_eq = portée équivalente (m)
                K = coefficient
        """
        if not spans:
            return 0.0, 0.0
        
        sum_a = sum(spans)
        sum_a3 = sum(a**3 for a in spans)
        
        # a_eq = √(Σ ai³ / Σ ai)
        a_eq = math.sqrt(sum_a3 / sum_a) if sum_a > 0 else 0
        
        # K = Σ ai / a_eq
        K = sum_a / a_eq if a_eq > 0 else 0
        
        return a_eq, K
    
    @staticmethod
    def calculate_crr(
        cra: float,
        broken_wires: List[Tuple[int, float]]
    ) -> Tuple[float, float]:
        """
        Calcule la Charge de Rupture Résiduelle (CRR)
        
        Args:
            cra: Charge de rupture à neuf (daN)
            broken_wires: Liste de (nombre_brins, charge_rupture_brin) en daN
        
        Returns:
            (CRR, CR) où:
                CRR = charge de rupture résiduelle (daN)
                CR = charge admissible (daN)
        """
        # CRR = CRA - Σ(nbc × crb)
        total_broken = sum(nbc * crb for nbc, crb in broken_wires)
        CRR = cra - total_broken
        
        # CR = min(CRA × 0.95, CRR)
        CR = min(cra * 0.95, CRR)
        
        return CRR, CR
    
    @staticmethod
    def calculate_vhl_effort(H: float, L: float) -> float:
        """
        Calcule l'effort résultant sur un support (VHL)
        
        Args:
            H: Composante horizontale (daN)
            L: Composante longitudinale (daN)
        
        Returns:
            R: Effort résultant (daN)
        """
        # R = √(H² + L²)
        return math.sqrt(H**2 + L**2)
    
    @staticmethod
    def calculate_cable_temperature_cigre(
        age_years: float = 10.0
    ) -> float:
        """
        Calcule l'émissivité du câble selon l'équation CIGRE
        
        Args:
            age_years: Âge du câble (années)
        
        Returns:
            epsilon: Émissivité
        """
        # ε = 0.23 + (0.7 × Age) / (1.22 + Age)
        epsilon = 0.23 + (0.7 * age_years) / (1.22 + age_years)
        return epsilon
    
    @classmethod
    def calculate_span(
        cls,
        geometry: SpanGeometry,
        cable: CableProperties,
        rho: float,
        wind_pressure_daPa: Optional[float] = None,
        angle_grade: Optional[float] = None
    ) -> SpanResult:
        """
        Calcul complet d'une portée
        
        Args:
            geometry: Géométrie de la portée
            cable: Propriétés du câble
            rho: Paramètre de la chaînette (m)
            wind_pressure_daPa: Pression du vent (daPa), optionnel
            angle_grade: Angle topographique (grades), optionnel
        
        Returns:
            SpanResult avec tous les résultats et validations
        """
        warnings = []
        errors = []
        
        # Validation du vent
        if wind_pressure_daPa and wind_pressure_daPa > 36:
            warnings.append(
                f"⚠️ Vent de {wind_pressure_daPa} daPa > 36 daPa "
                "(au-delà des conditions CELESTE)"
            )
        
        # Validation de l'angle
        if angle_grade and abs(angle_grade) > 15:
            warnings.append(
                f"⚠️ Angle de {angle_grade} grades > 15 grades "
                "(au-delà des conditions CELESTE)"
            )
        
        # Calcul de la corde
        b = geometry.b
        
        # Calcul des flèches
        F1, F2, H = cls.calculate_sag(geometry, rho)
        
        # Calcul des tensions
        T0, TA, TB = cls.calculate_tensions(geometry, cable, rho)
        
        # Arrondi à 1 daN comme spécifié
        T0 = round(T0)
        TA = round(TA)
        TB = round(TB)
        
        return SpanResult(
            b=round(b, 2),
            F1=round(F1, 2),
            F2=round(F2, 2),
            H=round(H, 2),
            T0=T0,
            TA=TA,
            TB=TB,
            warnings=warnings,
            errors=errors
        )


# Fonction utilitaire pour convertir les résultats en dict
def span_result_to_dict(result: SpanResult) -> Dict:
    """Convertit un SpanResult en dictionnaire pour l'API"""
    return {
        "geometry": {
            "b_m": result.b,
            "F1_m": result.F1,
            "F2_m": result.F2,
            "H_m": result.H
        },
        "tensions": {
            "T0_dan": result.T0,
            "TA_dan": result.TA,
            "TB_dan": result.TB
        },
        "warnings": result.warnings,
        "errors": result.errors
    }
