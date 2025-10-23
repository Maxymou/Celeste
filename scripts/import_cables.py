#!/usr/bin/env python3
"""
Script d'import des câbles depuis fichiers XML vers la base de données
Usage: python import_cables.py --xml-cable Câble.xml --xml-layer "Couche câble.xml"
"""
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.db_models import Base, Cable, Layer


def parse_cable_xml(xml_path: str) -> list[dict]:
    """
    Parse le fichier Câble.xml
    
    Structure attendue:
    <Cables>
        <Cable>
            <Nom>Aster 570</Nom>
            <Type>conducteur</Type>
            <MasseLineique>1.631</MasseLineique>
            <ModuleElasticite>78000</ModuleElasticite>
            <Section>564.6</Section>
            <CoefficientDilatation>19.1</CoefficientDilatation>
            <ChargeRupture>17200</ChargeRupture>
            <ChargeAdmissible>5160</ChargeAdmissible>
            <Diametre>31.5</Diametre>
        </Cable>
    </Cables>
    """
    cables = []
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        for cable_elem in root.findall('.//Cable'):
            cable = {
                'name': cable_elem.findtext('Nom', '').strip(),
                'type': cable_elem.findtext('Type', 'conducteur').strip(),
                'mass_lin_greased': float(cable_elem.findtext('MasseLineique', '0')),
                'E_MPa': float(cable_elem.findtext('ModuleElasticite', '0')),
                'section_mm2': float(cable_elem.findtext('Section', '0')),
                'alpha_1e6_per_C': float(cable_elem.findtext('CoefficientDilatation', '0')),
                'rupture_dan': float(cable_elem.findtext('ChargeRupture', '0')),
                'admissible_dan': float(cable_elem.findtext('ChargeAdmissible', '0')),
                'diameter_mm': 31.5
        },
        {
            'name': 'Pétunia 612',
            'type': 'conducteur',
            'mass_lin_greased': 2.311,
            'E_MPa': 63000,
            'section_mm2': 612.0,
            'alpha_1e6_per_C': 20.5,
            'rupture_dan': 19800,
            'admissible_dan': 5940,
            'diameter_mm': 34.8
        },
        {
            'name': 'Câble de garde AG7 116',
            'type': 'garde',
            'mass_lin_greased': 0.946,
            'E_MPa': 170000,
            'section_mm2': 116.0,
            'alpha_1e6_per_C': 11.5,
            'rupture_dan': 11700,
            'admissible_dan': 3510,
            'diameter_mm': 13.5
        }
    ]
    
    # Les couches seront créées après l'insertion des câbles
    layers = []
    
    return cables, layers


def import_to_database(cables: list[dict], layers: list[dict], db_path: str):
    """Importe les câbles et couches dans la base de données"""
    
    # Créer la connexion
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        print(f"\n📊 Importation dans {db_path}...")
        
        # Nettoyer les tables existantes
        session.query(Layer).delete()
        session.query(Cable).delete()
        session.commit()
        print("  ✓ Tables nettoyées")
        
        # Insérer les câbles
        cable_name_to_id = {}
        for cable_data in cables:
            cable = Cable(**cable_data)
            session.add(cable)
            session.flush()  # Pour obtenir l'ID
            cable_name_to_id[cable.name] = cable.id
            print(f"  ✓ Câble importé: {cable.name} (ID: {cable.id})")
        
        session.commit()
        
        # Insérer les couches
        for layer_data in layers:
            layer = Layer(**layer_data)
            session.add(layer)
            print(f"  ✓ Couche importée pour câble ID {layer.cable_id}")
        
        session.commit()
        
        print(f"\n✅ Import terminé: {len(cables)} câbles, {len(layers)} couches")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Erreur lors de l'import: {e}")
        raise
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(
        description="Importe les câbles depuis XML vers la base de données"
    )
    parser.add_argument(
        '--xml-cable',
        type=str,
        help='Chemin vers le fichier Câble.xml'
    )
    parser.add_argument(
        '--xml-layer',
        type=str,
        help='Chemin vers le fichier Couche câble.xml'
    )
    parser.add_argument(
        '--db',
        type=str,
        default='./data/celestex.db',
        help='Chemin vers la base de données SQLite (défaut: ./data/celestex.db)'
    )
    parser.add_argument(
        '--sample',
        action='store_true',
        help='Créer des données d\'exemple au lieu d\'importer depuis XML'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📦 Import des câbles - CELESTE X")
    print("=" * 60)
    
    cables = []
    layers = []
    
    # Créer le répertoire data si nécessaire
    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    if args.sample:
        # Créer des données d'exemple
        cables, layers = create_sample_data()
    else:
        # Import depuis XML
        if not args.xml_cable:
            print("❌ Erreur: --xml-cable est requis (ou utilisez --sample)")
            sys.exit(1)
        
        print(f"\n📖 Lecture de {args.xml_cable}...")
        if not Path(args.xml_cable).exists():
            print(f"❌ Fichier introuvable: {args.xml_cable}")
            sys.exit(1)
        
        cables = parse_cable_xml(args.xml_cable)
        
        if args.xml_layer:
            print(f"\n📖 Lecture de {args.xml_layer}...")
            if not Path(args.xml_layer).exists():
                print(f"❌ Fichier introuvable: {args.xml_layer}")
                sys.exit(1)
            
            # On a besoin d'un mapping nom -> id, mais on ne les a pas encore
            # On fera l'import des layers dans import_to_database
            layers = []
        
        if not cables:
            print("\n❌ Aucun câble trouvé dans le fichier XML")
            sys.exit(1)
    
    # Import dans la base
    import_to_database(cables, layers, str(db_path))
    
    print("\n" + "=" * 60)
    print("✅ Import terminé avec succès !")
    print("=" * 60)


if __name__ == '__main__':
    main()
float(cable_elem.findtext('Diametre', '0'))
            }
            
            if cable['name']:  # Ne garder que les câbles avec un nom
                cables.append(cable)
                print(f"  ✓ Câble trouvé: {cable['name']} ({cable['type']})")
        
    except ET.ParseError as e:
        print(f"❌ Erreur de parsing XML: {e}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    return cables


def parse_layer_xml(xml_path: str, cable_name_to_id: dict) -> list[dict]:
    """
    Parse le fichier Couche câble.xml
    
    Structure attendue:
    <Couches>
        <Couche>
            <CableNom>Aster 570</CableNom>
            <Nature>acier</Nature>
            <FormeFilamentaire>cylindrique</FormeFilamentaire>
            <NombreFilamentaires>7</NombreFilamentaires>
            <DiametreFilamentaire>3.15</DiametreFilamentaire>
        </Couche>
    </Couches>
    """
    layers = []
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        for layer_elem in root.findall('.//Couche'):
            cable_name = layer_elem.findtext('CableNom', '').strip()
            cable_id = cable_name_to_id.get(cable_name)
            
            if not cable_id:
                print(f"  ⚠️  Couche pour câble inconnu: {cable_name}")
                continue
            
            layer = {
                'cable_id': cable_id,
                'nature': layer_elem.findtext('Nature', '').strip(),
                'wire_shape': layer_elem.findtext('FormeFilamentaire', '').strip(),
                'strands': int(layer_elem.findtext('NombreFilamentaires', '0')),
                'strand_diameter_mm': float(layer_elem.findtext('DiametreFilamentaire', '0'))
            }
            
            layers.append(layer)
            print(f"  ✓ Couche trouvée: {cable_name} - {layer['nature']} ({layer['strands']} brins)")
        
    except ET.ParseError as e:
        print(f"❌ Erreur de parsing XML: {e}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    return layers


def create_sample_data() -> tuple[list[dict], list[dict]]:
    """Crée des données d'exemple si les fichiers XML ne sont pas disponibles"""
    print("\n📝 Création de données d'exemple...")
    
    cables = [
        {
            'name': 'Aster 570',
            'type': 'conducteur',
            'mass_lin_greased': 1.631,
            'E_MPa': 78000,
            'section_mm2': 564.6,
            'alpha_1e6_per_C': 19.1,
            'rupture_dan': 17200,
            'admissible_dan': 5160,
            'diameter_mm': 
