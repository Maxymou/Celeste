#!/usr/bin/env python3
"""
Suite de tests pour valider l'implémentation des calculs CELESTE
Usage: python test_implementation.py
"""
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.domain.mechanical import (
    MechanicalCalculator,
    CableProperties,
    SpanGeometry
)


class TestColors:
    """Couleurs pour l'affichage"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_test_header(test_name: str):
    """Affiche l'en-tête d'un test"""
    print(f"\n{TestColors.BLUE}{TestColors.BOLD}{'='*60}{TestColors.RESET}")
    print(f"{TestColors.BLUE}{TestColors.BOLD}TEST: {test_name}{TestColors.RESET}")
    print(f"{TestColors.BLUE}{TestColors.BOLD}{'='*60}{TestColors.RESET}")


def print_success(message: str):
    """Affiche un message de succès"""
    print(f"{TestColors.GREEN}✓ {message}{TestColors.RESET}")


def print_error(message: str):
    """Affiche un message d'erreur"""
    print(f"{TestColors.RED}✗ {message}{TestColors.RESET}")


def print_warning(message: str):
    """Affiche un avertissement"""
    print(f"{TestColors.YELLOW}⚠ {message}{TestColors.RESET}")


def assert_close(actual: float, expected: float, tolerance: float = 0.1, name: str = ""):
    """Vérifie qu'une valeur est proche de la valeur attendue"""
    if abs(actual - expected) <= tolerance:
        print_success(f"{name}: {actual:.2f} ≈ {expected:.2f} (tolérance: {tolerance})")
        return True
    else:
        print_error(f"{name}: {actual:.2f} ≠ {expected:.2f} (écart: {abs(actual-expected):.2f})")
        return False


def test_example_1_rte():
    """
    Test 1 : Exemple du cahier des charges RTE page 29
    Portée 500m, dénivelé 10m, ρ=2000m
    Câble Pétunia 612
    """
    print_test_header("Exemple RTE #1 - Pétunia 612 (500m, 10m)")
    
    # Données
    geometry = SpanGeometry(a=500.0, h=10.0)
    cable = CableProperties(
        name="Pétunia 612",
        mass_lin_kg_per_m=2.311,
        E_MPa=63000,
        section_mm2=612.0,
        alpha_1e6_per_C=20.5,
        rupture_dan=19800,
        diameter_mm=34.8
    )
    rho = 2000.0
    
    # Calcul
    result = MechanicalCalculator.calculate_span(geometry, cable, rho)
    
    print(f"\nEntrées:")
    print(f"  Portée: {geometry.a} m")
    print(f"  Dénivelé: {geometry.h} m")
    print(f"  ρ: {rho} m")
    print(f"  Câble: {cable.name} ({cable.mass_lin_kg_per_m} kg/m)")
    
    print(f"\nRésultats:")
    print(f"  Corde (b): {result.b} m")
    print(f"  Flèche F1: {result.F1} m")
    print(f"  Flèche F2: {result.F2} m")
    print(f"  Creux H: {result.H} m")
    print(f"  T0: {result.T0} daN")
    print(f"  TA: {result.TA} daN")
    print(f"  TB: {result.TB} daN")
    
    print(f"\nVérification des valeurs attendues:")
    success = True
    success &= assert_close(result.b, 500.10, 0.1, "Corde (b)")
    success &= assert_close(result.F1, 15.63, 0.1, "Flèche F1")
    success &= assert_close(result.F2, 11.02, 0.5, "Flèche F2")
    success &= assert_close(result.T0, 4534, 10, "Tension T0")
    success &= assert_close(result.TA, 4560, 10, "Tension TA")
    success &= assert_close(result.TB, 4580, 10, "Tension TB")
    
    return success


def test_example_2_rte():
    """
    Test 2 : Exemple du cahier des charges RTE page 31
    Portée 900m, dénivelé 150m, ρ=2000m
    Câble Aster 570
    """
    print_test_header("Exemple RTE #2 - Aster 570 (900m, 150m)")
    
    # Données
    geometry = SpanGeometry(a=900.0, h=150.0)
    cable = CableProperties(
        name="Aster 570",
        mass_lin_kg_per_m=1.631,
        E_MPa=78000,
        section_mm2=564.6,
        alpha_1e6_per_C=19.1,
        rupture_dan=17200,
        diameter_mm=31.5
    )
    rho = 2000.0
    
    # Calcul
    result = MechanicalCalculator.calculate_span(geometry, cable, rho)
    
    print(f"\nEntrées:")
    print(f"  Portée: {geometry.a} m")
    print(f"  Dénivelé: {geometry.h} m")
    print(f"  ρ: {rho} m")
    print(f"  Câble: {cable.name} ({cable.mass_lin_kg_per_m} kg/m)")
    
    print(f"\nRésultats:")
    print(f"  Corde (b): {result.b} m")
    print(f"  Flèche F1: {result.F1} m")
    print(f"  Flèche F2: {result.F2} m")
    print(f"  Creux H: {result.H} m")
    print(f"  T0: {result.T0} daN")
    print(f"  TA: {result.TA} daN")
    print(f"  TB: {result.TB} daN")
    
    print(f"\nVérification des valeurs attendues:")
    success = True
    success &= assert_close(result.b, 912.41, 0.5, "Corde (b)")
    success &= assert_close(result.F1, 51.32, 1.0, "Flèche F1")
    success &= assert_close(result.F2, 3.72, 0.5, "Flèche F2")
    success &= assert_close(result.T0, 3200, 20, "Tension T0")
    success &= assert_close(result.TA, 3205, 20, "Tension TA")
    success &= assert_close(result.TB, 3450, 20, "Tension TB")
    
    return success


def test_equivalent_span():
    """Test 3 : Calcul de portée équivalente (Blondel)"""
    print_test_header("Portée équivalente (Blondel)")
    
    spans = [300, 350, 400, 380, 420]
    a_eq, K = MechanicalCalculator.calculate_equivalent_span(spans)
    
    print(f"\nEntrées:")
    print(f"  Portées: {spans}")
    
    print(f"\nRésultats:")
    print(f"  Portée équivalente (a_eq): {a_eq:.2f} m")
    print(f"  Coefficient K: {K:.3f}")
    
    # Vérification manuelle
    sum_a = sum(spans)
    sum_a3 = sum(a**3 for a in spans)
    expected_aeq = (sum_a3 / sum_a) ** 0.5
    expected_K = sum_a / expected_aeq
    
    print(f"\nVérification:")
    success = True
    success &= assert_close(a_eq, expected_aeq, 0.1, "Portée équivalente")
    success &= assert_close(K, expected_K, 0.01, "Coefficient K")
    
    return success


def test_crr_calculation():
    """Test 4 : Calcul de la charge de rupture résiduelle"""
    print_test_header("Charge de Rupture Résiduelle (CRR)")
    
    cra = 17200  # Aster 570
    broken_wires = [
        (2, 150),  # 2 brins cassés à 150 daN chacun
        (1, 200)   # 1 brin cassé à 200 daN
    ]
    
    CRR, CR = MechanicalCalculator.calculate_crr(cra, broken_wires)
    
    print(f"\nEntrées:")
    print(f"  CRA (charge rupture à neuf): {cra} daN")
    print(f"  Brins cassés: {broken_wires}")
    
    print(f"\nRésultats:")
    print(f"  CRR (charge rupture résiduelle): {CRR} daN")
    print(f"  CR (charge admissible): {CR} daN")
    
    # Vérification
    expected_CRR = cra - (2*150 + 1*200)  # 17200 - 500 = 16700
    expected_CR = min(cra * 0.95, expected_CRR)  # min(16340, 16700) = 16340
    
    print(f"\nVérification:")
    success = True
    success &= assert_close(CRR, expected_CRR, 0.1, "CRR")
    success &= assert_close(CR, expected_CR, 0.1, "CR")
    
    return success


def test_vhl_effort():
    """Test 5 : Calcul d'effort VHL"""
    print_test_header("Effort VHL sur support")
    
    H = 3000  # daN
    L = 4000  # daN
    
    R = MechanicalCalculator.calculate_vhl_effort(H, L)
    
    print(f"\nEntrées:")
    print(f"  Composante horizontale (H): {H} daN")
    print(f"  Composante longitudinale (L): {L} daN")
    
    print(f"\nRésultats:")
    print(f"  Effort résultant (R): {R} daN")
    
    # Vérification
    expected_R = (H**2 + L**2) ** 0.5  # √(3000² + 4000²) = 5000
    
    print(f"\nVérification:")
    success = assert_close(R, expected_R, 1, "Effort résultant")
    
    return success


def test_cigre_emissivity():
    """Test 6 : Calcul d'émissivité CIGRE"""
    print_test_header("Émissivité CIGRE")
    
    ages = [0, 5, 10, 15, 20]
    
    print(f"\nCalcul de l'émissivité selon l'âge du câble:")
    print(f"{'Âge (ans)':<15} {'Émissivité':<15} {'Formule'}")
    print("-" * 50)
    
    for age in ages:
        epsilon = MechanicalCalculator.calculate_cable_temperature_cigre(age)
        formula = f"0.23 + (0.7×{age})/(1.22+{age})"
        print(f"{age:<15} {epsilon:<15.3f} {formula}")
    
    # Vérification pour age=10 ans (mentionné dans les specs)
    epsilon_10 = MechanicalCalculator.calculate_cable_temperature_cigre(10)
    expected_10 = 0.854  # Valeur donnée dans les specs
    
    print(f"\nVérification pour âge = 10 ans:")
    success = assert_close(epsilon_10, expected_10, 0.001, "Émissivité")
    
    return success


def test_celeste_domain_validation():
    """Test 7 : Validation du domaine CELESTE"""
    print_test_header("Validation domaine CELESTE")
    
    test_cases = [
        # (a1, a2, h_max, should_be_valid, description)
        (400, 200, 150, True, "a1/a2=2 < 3, h_max/a2=0.75 ≤ 0.8 → VALIDE"),
        (400, 200, 170, False, "a1/a2=2 < 3, h_max/a2=0.85 > 0.8 → INVALIDE"),
        (600, 150, 50, True, "a1/a2=4 ≥ 3, h_max/a2=0.33 ≤ 0.4 → VALIDE"),
        (600, 150, 70, False, "a1/a2=4 ≥ 3, h_max/a2=0.47 > 0.4 → INVALIDE"),
    ]
    
    print(f"\n{'a1 (m)':<10} {'a2 (m)':<10} {'h_max (m)':<12} {'Attendu':<10} {'Résultat':<10} {'Description'}")
    print("-" * 90)
    
    all_success = True
    for a1, a2, h_max, expected_valid, description in test_cases:
        errors = MechanicalCalculator.validate_celeste_domain(a1, a2, h_max)
        is_valid = len(errors) == 0
        
        status = "✓" if is_valid == expected_valid else "✗"
        color = TestColors.GREEN if is_valid == expected_valid else TestColors.RED
        
        print(f"{a1:<10} {a2:<10} {h_max:<12} {str(expected_valid):<10} "
              f"{color}{str(is_valid):<10}{TestColors.RESET} {description}")
        
        if errors:
            for error in errors:
                print(f"    → {error}")
        
        all_success &= (is_valid == expected_valid)
    
    return all_success


def test_warning_generation():
    """Test 8 : Génération d'avertissements"""
    print_test_header("Génération d'avertissements")
    
    geometry = SpanGeometry(a=500.0, h=10.0)
    cable = CableProperties(
        name="Test Cable",
        mass_lin_kg_per_m=2.0,
        E_MPa=70000,
        section_mm2=500,
        alpha_1e6_per_C=20,
        rupture_dan=15000,
        diameter_mm=30
    )
    rho = 2000
    
    # Test avec vent élevé
    result_wind = MechanicalCalculator.calculate_span(
        geometry, cable, rho,
        wind_pressure_daPa=40  # > 36
    )
    
    print(f"\nTest 1: Vent élevé (40 daPa > 36 daPa)")
    print(f"  Avertissements: {len(result_wind.warnings)}")
    if result_wind.warnings:
        for warning in result_wind.warnings:
            print_warning(f"  {warning}")
    
    # Test avec angle élevé
    result_angle = MechanicalCalculator.calculate_span(
        geometry, cable, rho,
        angle_grade=18  # > 15
    )
    
    print(f"\nTest 2: Angle élevé (18 grades > 15 grades)")
    print(f"  Avertissements: {len(result_angle.warnings)}")
    if result_angle.warnings:
        for warning in result_angle.warnings:
            print_warning(f"  {warning}")
    
    # Test combiné
    result_both = MechanicalCalculator.calculate_span(
        geometry, cable, rho,
        wind_pressure_daPa=40,
        angle_grade=18
    )
    
    print(f"\nTest 3: Vent et angle élevés")
    print(f"  Avertissements: {len(result_both.warnings)}")
    if result_both.warnings:
        for warning in result_both.warnings:
            print_warning(f"  {warning}")
    
    success = (len(result_wind.warnings) >= 1 and 
               len(result_angle.warnings) >= 1 and 
               len(result_both.warnings) >= 2)
    
    return success


def run_all_tests():
    """Exécute tous les tests"""
    print(f"\n{TestColors.BOLD}{'='*60}")
    print(f"SUITE DE TESTS - CELESTE X")
    print(f"Validation des calculs mécaniques")
    print(f"{'='*60}{TestColors.RESET}\n")
    
    tests = [
        ("Exemple RTE #1 (Pétunia 612)", test_example_1_rte),
        ("Exemple RTE #2 (Aster 570)", test_example_2_rte),
        ("Portée équivalente (Blondel)", test_equivalent_span),
        ("Charge de Rupture Résiduelle", test_crr_calculation),
        ("Effort VHL", test_vhl_effort),
        ("Émissivité CIGRE", test_cigre_emissivity),
        ("Validation domaine CELESTE", test_celeste_domain_validation),
        ("Génération d'avertissements", test_warning_generation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print_error(f"Exception dans le test '{test_name}': {e}")
            results.append((test_name, False))
    
    # Résumé final
    print(f"\n{TestColors.BOLD}{'='*60}")
    print(f"RÉSUMÉ DES TESTS")
    print(f"{'='*60}{TestColors.RESET}\n")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = f"{TestColors.GREEN}✓ RÉUSSI{TestColors.RESET}" if success else f"{TestColors.RED}✗ ÉCHOUÉ{TestColors.RESET}"
        print(f"  {test_name:<40} {status}")
    
    print(f"\n{TestColors.BOLD}{'='*60}{TestColors.RESET}")
    
    if passed == total:
        print(f"{TestColors.GREEN}{TestColors.BOLD}✓ TOUS LES TESTS RÉUSSIS ({passed}/{total}){TestColors.RESET}")
        return 0
    else:
        print(f"{TestColors.RED}{TestColors.BOLD}✗ {total - passed} TEST(S) ÉCHOUÉ(S) ({passed}/{total}){TestColors.RESET}")
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
