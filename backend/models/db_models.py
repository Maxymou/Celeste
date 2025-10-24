"""
Modèles de base de données partagés pour CELESTE X
Utilisés par backend_admin et scripts d'import
"""
from typing import ClassVar, Optional
from sqlalchemy import Integer, String, Float, Column, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """Modèle d'utilisateur pour l'authentification"""
    __tablename__ = "user"
    __allow_unmapped__ = True  # Permet d'avoir des attributs non mappés par SQLAlchemy

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # Nom complet de l'utilisateur
    email = Column(String, nullable=False, unique=True, index=True)  # Email unique
    hashed_password = Column(String, nullable=False)  # Mot de passe hashé avec bcrypt
    is_active = Column(Boolean, default=True, nullable=False)  # Compte actif/désactivé
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Propriété temporaire pour le formulaire admin (non persistée en BDD)
    password: str = None  # type: ignore

    def __repr__(self):
        return f"<User(email='{self.email}', name='{self.name}', active={self.is_active})>"


class Cable(Base):
    """Modèle de câble électrique"""
    __tablename__ = "cable"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True, index=True)
    type = Column(String, nullable=False)  # conducteur/garde/mixte
    
    # Propriétés mécaniques
    mass_lin_greased = Column(Float, nullable=False)  # kg/m avec graisse
    E_MPa = Column(Float, nullable=False)  # Module d'élasticité (MPa)
    section_mm2 = Column(Float, nullable=False)  # Section (mm²)
    alpha_1e6_per_C = Column(Float, nullable=False)  # Coeff. dilatation (×10⁻⁶/°C)
    
    # Charges
    rupture_dan = Column(Float, nullable=False)  # Charge rupture à neuf (daN)
    admissible_dan = Column(Float, nullable=False)  # Charge admissible (daN)
    
    # Géométrie
    diameter_mm = Column(Float, nullable=False)  # Diamètre (mm)
    
    def __repr__(self):
        return f"<Cable(name='{self.name}', type='{self.type}', mass={self.mass_lin_greased} kg/m)>"


class Layer(Base):
    """Modèle de couche de câble (composition interne)"""
    __tablename__ = "layer"
    
    id = Column(Integer, primary_key=True)
    cable_id = Column(Integer, nullable=False, index=True)  # FK vers Cable
    
    # Propriétés de la couche
    nature = Column(String, nullable=False)  # acier, alu, almelec, ...
    wire_shape = Column(String)  # cylindrique, Z, trapézoïdal
    strands = Column(Integer, nullable=False)  # Nombre de brins
    strand_diameter_mm = Column(Float, nullable=False)  # Diamètre brin (mm)
    
    def __repr__(self):
        return f"<Layer(cable_id={self.cable_id}, nature='{self.nature}', strands={self.strands})>"
