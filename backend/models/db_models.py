"""
Modèles de base de données partagés pour CELESTE X
Utilisés par backend_admin et scripts d'import
"""
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import declarative_base

Base = declarative_base()


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
