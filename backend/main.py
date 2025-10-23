import logging
from pathlib import Path
from fastapi import FastAPI, APIRouter, Request, HTTPException, Query, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError as PydanticValidationError
from typing import Optional

from backend.domain.mechanical import (
    MechanicalCalculator,
    CableProperties,
    SpanGeometry,
    span_result_to_dict
)
from backend.exceptions import (
    CelesteException,
    ValidationError,
    CalculationError
)
from backend.auth import (
    LoginRequest,
    TokenResponse,
    authenticate_user,
    create_access_token
)
from datetime import timedelta

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CELESTE X",
    description="Application de calcul mécanique pour lignes électriques aériennes",
    version="1.0.0"
)
api = APIRouter(prefix="/api")


# ===== EXCEPTION HANDLERS =====

@app.exception_handler(CelesteException)
async def celeste_exception_handler(request: Request, exc: CelesteException):
    """Handler pour les exceptions métier CELESTE"""
    logger.error(f"Erreur métier: {exc.message}", extra={"details": exc.details})
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handler pour les erreurs de validation métier"""
    logger.warning(f"Erreur de validation: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(CalculationError)
async def calculation_exception_handler(request: Request, exc: CalculationError):
    """Handler pour les erreurs de calcul"""
    logger.error(f"Erreur de calcul: {exc.message}", extra={"details": exc.details})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Calculation error",
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handler pour les exceptions non gérées"""
    logger.exception(f"Erreur inattendue: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "Une erreur inattendue s'est produite"
        }
    )


# ===== MODÈLES DE DONNÉES =====

class CableInput(BaseModel):
    """Propriétés d'un câble pour les calculs"""
    name: str = Field(..., description="Nom du câble")
    mass_lin_kg_per_m: float = Field(..., gt=0, description="Masse linéique (kg/m)")
    E_MPa: float = Field(..., gt=0, description="Module d'élasticité (MPa)")
    section_mm2: float = Field(..., gt=0, description="Section (mm²)")
    alpha_1e6_per_C: float = Field(..., description="Coeff. dilatation (×10⁻⁶/°C)")
    rupture_dan: float = Field(..., gt=0, description="Charge de rupture (daN)")
    diameter_mm: float = Field(..., gt=0, description="Diamètre (mm)")


class SpanCalcInput(BaseModel):
    """Entrées pour le calcul d'une portée"""
    # Géométrie
    span_length_m: float = Field(..., gt=0, description="Longueur portée (m)")
    delta_h_m: float = Field(..., description="Dénivelé entre supports (m)")
    
    # Câble
    cable: CableInput = Field(..., description="Propriétés du câble")
    
    # Paramètre de calcul
    rho_m: float = Field(..., gt=0, description="Paramètre chaînette (m)")
    
    # Optionnel
    wind_pressure_daPa: Optional[float] = Field(None, ge=0, description="Pression vent (daPa)")
    angle_topo_grade: Optional[float] = Field(None, description="Angle topographique (grades)")


class EquivalentSpanInput(BaseModel):
    """Entrées pour le calcul de portée équivalente"""
    spans_m: list[float] = Field(..., min_items=1, description="Liste des portées (m)")


class CRRInput(BaseModel):
    """Entrées pour le calcul de charge de rupture résiduelle"""
    cra_dan: float = Field(..., gt=0, description="Charge rupture à neuf (daN)")
    broken_wires: list[tuple[int, float]] = Field(
        default=[],
        description="Liste de (nb_brins_cassés, charge_rupture_brin)"
    )


class VHLInput(BaseModel):
    """Entrées pour le calcul d'effort VHL"""
    H_dan: float = Field(..., description="Composante horizontale (daN)")
    L_dan: float = Field(..., description="Composante longitudinale (daN)")


# ===== ENDPOINTS =====

@api.get("/health")
def health():
    """Endpoint de santé"""
    return {"status": "ok", "version": "1.0.0"}


@api.get("/cables")
def get_cables():
    """
    Récupère la liste des câbles disponibles

    Retourne:
        Liste des câbles avec leurs propriétés mécaniques
    """
    logger.info("Récupération de la liste des câbles")

    # Pour l'instant, retourne les câbles hardcodés
    # TODO: À remplacer par une requête SQL quand la base sera peuplée
    cables = [
        {
            "name": "Aster 570",
            "mass_lin_kg_per_m": 1.631,
            "E_MPa": 78000,
            "section_mm2": 564.6,
            "alpha_1e6_per_C": 19.1,
            "rupture_dan": 17200,
            "diameter_mm": 31.5,
            "type": "ACSR"
        },
        {
            "name": "Pétunia 612",
            "mass_lin_kg_per_m": 2.311,
            "E_MPa": 63000,
            "section_mm2": 612.0,
            "alpha_1e6_per_C": 20.5,
            "rupture_dan": 19800,
            "diameter_mm": 34.8,
            "type": "ACSR"
        },
        {
            "name": "Phlox 228",
            "mass_lin_kg_per_m": 0.776,
            "E_MPa": 74000,
            "section_mm2": 228.0,
            "alpha_1e6_per_C": 19.3,
            "rupture_dan": 7200,
            "diameter_mm": 21.8,
            "type": "ACSR"
        }
    ]

    return {
        "success": True,
        "count": len(cables),
        "cables": cables
    }


@api.post("/calc/span")
def calc_span(payload: SpanCalcInput):
    """
    Calcul complet d'une portée

    Retourne:
        - Géométrie (corde, flèches)
        - Tensions (T0, TA, TB)
        - Avertissements et erreurs
    """
    logger.info(f"Calcul de portée: {payload.span_length_m}m, dénivelé: {payload.delta_h_m}m")

    try:
        # Validation des entrées
        if payload.rho_m <= 0:
            raise ValidationError(
                "Le paramètre ρ (rho) doit être strictement positif",
                {"rho_m": payload.rho_m}
            )

        # Conversion des données
        geometry = SpanGeometry(
            a=payload.span_length_m,
            h=payload.delta_h_m
        )

        cable = CableProperties(
            name=payload.cable.name,
            mass_lin_kg_per_m=payload.cable.mass_lin_kg_per_m,
            E_MPa=payload.cable.E_MPa,
            section_mm2=payload.cable.section_mm2,
            alpha_1e6_per_C=payload.cable.alpha_1e6_per_C,
            rupture_dan=payload.cable.rupture_dan,
            diameter_mm=payload.cable.diameter_mm
        )

        # Calcul
        result = MechanicalCalculator.calculate_span(
            geometry=geometry,
            cable=cable,
            rho=payload.rho_m,
            wind_pressure_daPa=payload.wind_pressure_daPa,
            angle_grade=payload.angle_topo_grade
        )

        logger.info(f"Calcul réussi: T0={result.T0} daN, warnings={len(result.warnings)}")

        return {
            "success": True,
            "input": payload.dict(),
            "result": span_result_to_dict(result)
        }

    except (ValidationError, CalculationError):
        # Re-lever les exceptions métier pour qu'elles soient gérées par les handlers
        raise
    except ValueError as e:
        raise ValidationError(f"Valeur invalide: {str(e)}")
    except ZeroDivisionError:
        raise CalculationError("Division par zéro dans le calcul", {"cable": payload.cable.name})


@api.post("/calc/equivalent-span")
def calc_equivalent_span(payload: EquivalentSpanInput):
    """
    Calcule la portée équivalente selon Blondel
    
    Retourne:
        - a_eq: portée équivalente (m)
        - K: coefficient
    """
    try:
        a_eq, K = MechanicalCalculator.calculate_equivalent_span(payload.spans_m)
        
        return {
            "success": True,
            "input": {"spans_m": payload.spans_m},
            "result": {
                "a_eq_m": round(a_eq, 2),
                "K": round(K, 3)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api.post("/calc/crr")
def calc_crr(payload: CRRInput):
    """
    Calcule la Charge de Rupture Résiduelle
    
    Retourne:
        - CRR: charge de rupture résiduelle (daN)
        - CR: charge admissible (daN)
    """
    try:
        CRR, CR = MechanicalCalculator.calculate_crr(
            payload.cra_dan,
            payload.broken_wires
        )
        
        return {
            "success": True,
            "input": payload.dict(),
            "result": {
                "CRR_dan": round(CRR),
                "CR_dan": round(CR)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api.post("/calc/vhl")
def calc_vhl(payload: VHLInput):
    """
    Calcule l'effort résultant sur un support (VHL)
    
    Retourne:
        - R: effort résultant (daN)
    """
    try:
        R = MechanicalCalculator.calculate_vhl_effort(
            payload.H_dan,
            payload.L_dan
        )
        
        return {
            "success": True,
            "input": payload.dict(),
            "result": {
                "R_dan": round(R)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api.get("/calc/cigre-emissivity")
def calc_cigre_emissivity(age_years: float = 10.0):
    """
    Calcule l'émissivité selon CIGRE
    
    Paramètres:
        - age_years: âge du câble (années)
    
    Retourne:
        - epsilon: émissivité
    """
    try:
        epsilon = MechanicalCalculator.calculate_cable_temperature_cigre(age_years)
        
        return {
            "success": True,
            "input": {"age_years": age_years},
            "result": {
                "epsilon": round(epsilon, 3)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api.post("/calc/validate-domain")
def validate_domain(
    a1_m: float = Query(..., gt=0, description="Plus grande portée (m)"),
    a2_m: float = Query(..., gt=0, description="Plus petite portée (m)"),
    h_max_m: float = Query(..., ge=0, description="Dénivelé max canton (m)")
):
    """
    Valide le domaine d'application mécanique CELESTE
    
    Retourne:
        - valid: booléen
        - errors: liste des erreurs
    """
    try:
        errors = MechanicalCalculator.validate_celeste_domain(a1_m, a2_m, h_max_m)
        
        return {
            "success": True,
            "input": {
                "a1_m": a1_m,
                "a2_m": a2_m,
                "h_max_m": h_max_m
            },
            "result": {
                "valid": len(errors) == 0,
                "errors": errors
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@api.post("/auth/login", response_model=TokenResponse)
def login(credentials: LoginRequest):
    """
    Endpoint d'authentification

    Authentifie un utilisateur par email (liste blanche) et génère un token JWT

    Returns:
        Token JWT et informations utilisateur
    """
    logger.info(f"Tentative de connexion pour: {credentials.email}")

    # Authentifier l'utilisateur
    if not authenticate_user(credentials.email, credentials.password):
        logger.warning(f"Échec d'authentification pour: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect, ou accès non autorisé"
        )

    # Créer le token JWT
    access_token, expires_at = create_access_token(
        data={"sub": credentials.email},
        expires_delta=timedelta(minutes=480)  # 8 heures
    )

    logger.info(f"Connexion réussie pour: {credentials.email}")

    return TokenResponse(
        token=access_token,
        email=credentials.email,
        expires_at=expires_at.isoformat()
    )


app.include_router(api)

# Servage des fichiers statiques React
DIST_DIR = Path(__file__).resolve().parents[1] / "frontend" / "dist"
INDEX_FILE = DIST_DIR / "index.html"

if DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=str(DIST_DIR), html=True), name="static")

    @app.middleware("http")
    async def spa_fallback(request: Request, call_next):
        response = await call_next(request)
        if response.status_code == 404 and request.method == "GET":
            path = request.url.path
            if not path.startswith("/api/") and INDEX_FILE.exists():
                return FileResponse(str(INDEX_FILE))
        return response
