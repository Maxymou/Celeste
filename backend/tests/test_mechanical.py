"""
Tests unitaires pour les calculs mécaniques
"""
import pytest
import math
from backend.domain.mechanical import (
    MechanicalCalculator,
    CableProperties,
    SpanGeometry,
    SpanResult
)


# ===== FIXTURES =====

@pytest.fixture
def cable_aster570():
    """Câble Aster 570 pour les tests"""
    return CableProperties(
        name="Aster 570",
        mass_lin_kg_per_m=1.631,
        E_MPa=78000,
        section_mm2=564.6,
        alpha_1e6_per_C=19.1,
        rupture_dan=17200,
        diameter_mm=31.5
    )


@pytest.fixture
def geometry_horizontal():
    """Géométrie horizontale simple (pas de dénivelé)"""
    return SpanGeometry(a=100, h=0)


@pytest.fixture
def geometry_with_slope():
    """Géométrie avec dénivelé"""
    return SpanGeometry(a=500, h=10)


# ===== TESTS GÉOMÉTRIE =====

def test_span_geometry_cord_length():
    """Test du calcul de la longueur de corde"""
    geometry = SpanGeometry(a=100, h=0)
    assert geometry.b == 100.0

    geometry_slope = SpanGeometry(a=300, h=40)
    expected_b = math.sqrt(300**2 + 40**2)
    assert geometry_slope.b == pytest.approx(expected_b, abs=0.01)


# ===== TESTS FLÈCHES =====

def test_calculate_sag_horizontal_span():
    """Test du calcul de flèche pour une portée horizontale"""
    geometry = SpanGeometry(a=100, h=0)
    rho = 2000

    F1, F2, H = MechanicalCalculator.calculate_sag(geometry, rho)

    # F1 = (a × b) / (8 × ρ) = (100 × 100) / (8 × 2000) = 0.625 m
    assert F1 == pytest.approx(0.625, abs=0.01)

    # Pour h=0, F2 devrait être égal à F1
    assert F2 == pytest.approx(F1, abs=0.01)

    # H = F2 + |h| = 0.625 + 0 = 0.625
    assert H == pytest.approx(0.625, abs=0.01)


def test_calculate_sag_with_slope():
    """Test du calcul de flèche avec dénivelé"""
    geometry = SpanGeometry(a=500, h=10)
    rho = 2000

    F1, F2, H = MechanicalCalculator.calculate_sag(geometry, rho)

    # F1 = (a × b) / (8 × ρ)
    b = geometry.b
    expected_F1 = (500 * b) / (8 * 2000)
    assert F1 == pytest.approx(expected_F1, abs=0.01)

    # F2 < F1 car il y a du dénivelé
    assert F2 < F1

    # H = F2 + |h|
    assert H == pytest.approx(F2 + abs(10), abs=0.01)


# ===== TESTS TENSIONS =====

def test_calculate_tensions(cable_aster570):
    """Test du calcul des tensions"""
    geometry = SpanGeometry(a=500, h=10)
    rho = 2000

    T0, TA, TB = MechanicalCalculator.calculate_tensions(geometry, cable_aster570, rho)

    # T0 = ρ × ω × g
    omega = cable_aster570.mass_lin_kg_per_m
    g = 9.81 / 10  # Conversion en daN/kg
    expected_T0 = rho * omega * g

    assert T0 == pytest.approx(expected_T0, abs=1)

    # TA < TB car support A est plus bas
    assert TA < TB

    # T0 < TA < TB
    assert T0 < TA < TB


# ===== TESTS PORTÉE ÉQUIVALENTE =====

def test_calculate_equivalent_span_single():
    """Test avec une seule portée"""
    spans = [400.0]
    a_eq, K = MechanicalCalculator.calculate_equivalent_span(spans)

    assert a_eq == pytest.approx(400.0, abs=0.1)
    assert K == pytest.approx(1.0, abs=0.01)


def test_calculate_equivalent_span_multiple():
    """Test avec plusieurs portées"""
    spans = [400, 500, 450, 380]
    a_eq, K = MechanicalCalculator.calculate_equivalent_span(spans)

    # Calcul manuel
    sum_a = sum(spans)
    sum_a3 = sum(a**3 for a in spans)
    expected_a_eq = math.sqrt(sum_a3 / sum_a)
    expected_K = sum_a / expected_a_eq

    assert a_eq == pytest.approx(expected_a_eq, abs=0.1)
    assert K == pytest.approx(expected_K, abs=0.01)


def test_calculate_equivalent_span_empty():
    """Test avec une liste vide"""
    spans = []
    a_eq, K = MechanicalCalculator.calculate_equivalent_span(spans)

    assert a_eq == 0.0
    assert K == 0.0


# ===== TESTS CRR =====

def test_calculate_crr_no_broken_wires():
    """Test CRR sans brins cassés"""
    cra = 17200
    broken_wires = []

    CRR, CR = MechanicalCalculator.calculate_crr(cra, broken_wires)

    assert CRR == 17200
    assert CR == pytest.approx(cra * 0.95, abs=1)


def test_calculate_crr_with_broken_wires():
    """Test CRR avec brins cassés"""
    cra = 17200
    broken_wires = [(2, 500), (1, 500)]  # 3 brins × 500 daN = 1500 daN

    CRR, CR = MechanicalCalculator.calculate_crr(cra, broken_wires)

    expected_CRR = 17200 - 1500
    assert CRR == expected_CRR

    # CR = min(CRA × 0.95, CRR)
    assert CR == min(cra * 0.95, CRR)


# ===== TESTS VHL =====

def test_calculate_vhl_effort():
    """Test du calcul d'effort VHL"""
    H = 3000
    L = 4000

    R = MechanicalCalculator.calculate_vhl_effort(H, L)

    expected_R = math.sqrt(H**2 + L**2)
    assert R == pytest.approx(expected_R, abs=1)


def test_calculate_vhl_effort_zero():
    """Test VHL avec composantes nulles"""
    R = MechanicalCalculator.calculate_vhl_effort(0, 0)
    assert R == 0.0


# ===== TESTS ÉMISSIVITÉ CIGRE =====

def test_calculate_cable_temperature_cigre():
    """Test du calcul d'émissivité CIGRE"""
    age_years = 10.0

    epsilon = MechanicalCalculator.calculate_cable_temperature_cigre(age_years)

    # ε = 0.23 + (0.7 × 10) / (1.22 + 10) = 0.23 + 7 / 11.22
    expected_epsilon = 0.23 + (0.7 * 10) / (1.22 + 10)

    assert epsilon == pytest.approx(expected_epsilon, abs=0.001)


def test_calculate_cable_temperature_cigre_new():
    """Test émissivité pour câble neuf"""
    epsilon = MechanicalCalculator.calculate_cable_temperature_cigre(0)

    # Pour age=0: ε = 0.23 + 0 = 0.23
    assert epsilon == pytest.approx(0.23, abs=0.001)


# ===== TESTS VALIDATION DOMAINE CELESTE =====

def test_validate_celeste_domain_valid():
    """Test validation domaine CELESTE valide"""
    errors = MechanicalCalculator.validate_celeste_domain(
        a1=400, a2=200, h_max=100
    )

    # a1/a2 = 2 < 3, h_max/a2 = 0.5 < 0.8 → valide
    assert len(errors) == 0


def test_validate_celeste_domain_invalid_ratio_low():
    """Test validation domaine CELESTE invalide (ratio < 3)"""
    errors = MechanicalCalculator.validate_celeste_domain(
        a1=400, a2=200, h_max=180
    )

    # a1/a2 = 2 < 3, h_max/a2 = 0.9 > 0.8 → invalide
    assert len(errors) > 0
    assert "0.8" in errors[0]


def test_validate_celeste_domain_invalid_ratio_high():
    """Test validation domaine CELESTE invalide (ratio ≥ 3)"""
    errors = MechanicalCalculator.validate_celeste_domain(
        a1=600, a2=200, h_max=100
    )

    # a1/a2 = 3 ≥ 3, h_max/a2 = 0.5 > 0.4 → invalide
    assert len(errors) > 0
    assert "0.4" in errors[0]


# ===== TESTS CALCUL COMPLET =====

def test_calculate_span_complete(cable_aster570):
    """Test du calcul complet de portée"""
    geometry = SpanGeometry(a=500, h=10)
    rho = 2000

    result = MechanicalCalculator.calculate_span(
        geometry=geometry,
        cable=cable_aster570,
        rho=rho
    )

    assert isinstance(result, SpanResult)
    assert result.b > 0
    assert result.F1 > 0
    assert result.T0 > 0
    assert result.TA > 0
    assert result.TB > 0


def test_calculate_span_with_warnings(cable_aster570):
    """Test calcul avec warnings (vent/angle élevés)"""
    geometry = SpanGeometry(a=500, h=10)
    rho = 2000

    result = MechanicalCalculator.calculate_span(
        geometry=geometry,
        cable=cable_aster570,
        rho=rho,
        wind_pressure_daPa=50,  # > 36
        angle_grade=20  # > 15
    )

    assert len(result.warnings) >= 2
    assert any("Vent" in w for w in result.warnings)
    assert any("Angle" in w for w in result.warnings)


def test_calculate_span_tension_exceeds_rupture(cable_aster570):
    """Test calcul avec tension dépassant la charge de rupture"""
    geometry = SpanGeometry(a=5000, h=100)
    rho = 50  # Très faible rho pour créer des tensions énormes

    result = MechanicalCalculator.calculate_span(
        geometry=geometry,
        cable=cable_aster570,
        rho=rho
    )

    # Devrait avoir une erreur de rupture
    assert len(result.errors) > 0
    assert any("rupture" in e.lower() for e in result.errors)


def test_calculate_span_rho_warning_low(cable_aster570):
    """Test warning pour rho très faible"""
    geometry = SpanGeometry(a=100, h=0)
    rho = 50  # Très faible

    result = MechanicalCalculator.calculate_span(
        geometry=geometry,
        cable=cable_aster570,
        rho=rho
    )

    assert any("ρ très faible" in w for w in result.warnings)


def test_calculate_span_rho_warning_high(cable_aster570):
    """Test warning pour rho très élevé"""
    geometry = SpanGeometry(a=100, h=0)
    rho = 15000  # Très élevé

    result = MechanicalCalculator.calculate_span(
        geometry=geometry,
        cable=cable_aster570,
        rho=rho
    )

    assert any("ρ très élevé" in w for w in result.warnings)
