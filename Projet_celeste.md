# Projet_CELESTE — Cahier des charges (v2.0)

> **But du document** — Spécifier les besoins, comportements, et livrables de l’application CELESTE pour permettre son développement progressif et modulaire par un agent de type Codex/Godex, avec déploiement sur VM Debian sous Proxmox.

---

## 1. Objectif de l’application

Créer une application métier destinée à modéliser, calculer et analyser des lignes électriques aériennes dans un cadre de **maintenance**, en s’inspirant des fonctionnalités historiques de CELESTE v2/v3.

L’application permettra :
- Le **calcul des tensions, flèches, efforts** et autres paramètres mécaniques d’une ligne.
- L’analyse de situations réelles terrain, d’**interventions** et d’**incidents** (travaux, surcharge, obstacle).
- La **traçabilité chantier par chantier**.

---

## 2. Architecture fonctionnelle

### 2.1 Pages principales

1. **Page de connexion**
   - Login obligatoire
   - Authentification par **liste blanche d’emails autorisés**
   - Redirection vers la liste des chantiers après connexion

2. **Gestion des chantiers**
   - Liste de tous les chantiers enregistrés
   - Filtre, recherche, tri
   - Bouton “Créer un chantier” avec : 
     - Nom du chantier
     - Nom de la ligne
     - Date automatique à la création
     - Nombre de pylônes (ou supports)
     - Données topographiques (portées, altitudes, chaînes, etc.)
     - Champs supplémentaires :
       - Date de relevé terrain
       - Commentaires terrain
       - Version

3. **Modules de calcul**

   #### A. État initial
   - Saisie des données terrain (pylônes, portées, chaînes, accrochage, etc.)
   - Choix portée réelle / portée équivalente
   - Données câble issues du catalogue interne
   - Pression de vent (alerte si > 36 daPa)
   - Résultat : tensions de référence (Tacc), flèches, point bas

   #### B. Intervention sur câbles
   - Simulation d’une descente ou levage
   - Impact d’un hauban, isolateur, poulie
   - Calcule les nouvelles tensions (VHL) et efforts par support

   #### C. Situation particulière
   - Surcharge ponctuelle (ex. arbre)
   - Calcul flèche max et descente de câble
   - Message simple affiché : “⚠️ Attention obstacle” ou “⚠️ Attention surcharge”

4. **Catalogue câble**
   - Import automatique des fichiers `Câble.xml` et `Couche câble.xml`
   - Possibilité de modifier/ajouter des câbles
   - Données issues des fichiers XML fournis (désignation, masse, E, alpha, CRA, couches, etc.)

5. **Méthode Papoto**
   - Méthode incluse mais **formule manquante**
   - Saisie des visées tangentes, température, vent, heure
   - Résultat non obligatoire, non bloquant, à documenter dans les exports plus tard

---

## 3. Calculs et formules intégrées

Toutes les formules sont arrondies à **1 daN**.

### A. Domaine mécanique CELESTE (validité)
- Si a1/a2 < 3 → h_max / a2 ≤ 0.8
- Si a1/a2 ≥ 3 → h_max / a2 ≤ 0.4

### B. Température du câble (CIGRE)
- ε = 0.23 + (0.7 × Age) / (1.22 + Age)
- v_min = 0.5 m/s

### C. Charge de rupture résiduelle (CRR)
- CRR = CRA - Σ(nbc × crb)
- CR = min(CRA × 0.95, CRR)

### D. Portée équivalente (Blondel)
- a_eq = √(Σ a_i³ / Σ a_i)
- K = Σ a_i / a_eq

### E. Efforts support (VHL)
- R = √(H² + L²)

### F. Flèches et géométrie
- Flèche médiane : F1 = y_milieu − y_corde
- Dénivelé : F2 = y_bas accrochage − y_point bas
- Creux : H = y_haut accrochage − y_point bas
- Flèche en un point : F(x) = y(x) − y_corde(x)

### G. Tranchée forestière
- ½ Largeur AT = d_câble/axe + d_sécurité_AT
- ½ Largeur DT = d_câble/axe + d_sécurité_DT
- Hauteur tranchée = h_câble − h_point − d_sécurité

### H. Alerte en cas de dépassement
- ⚠️ “Vent > 36 daPa” : message non bloquant
- ⚠️ “Angle > 15 grades” : message non bloquant

---

## 4. Visualisation

- **Vue 2D** : profil en long, VHL, flèches, altitudes, distances, support, point bas
- **Vue 3D (react-three-fiber)** :
  - Pylônes, chaînes, flèches, câbles, point bas
  - Affichage VHL (vecteurs)
  - Sens du vent : flèche directionnelle ou animation
  - Toggle avant/après intervention
  - Export GLB, PNG (plus tard)

---

## 5. Exports & traçabilité

- Pas de PDF pour le moment
- Journal de calcul conservé en base
- Résultats incluent : version, date de création, scénario, canton, etc.
- Bouton “Dupliquer ce chantier”

---

## 6. Sécurité

- Authentification email (liste blanche)
- Pas de rôles complexes
- Pas d’OAuth / 2FA pour le moment

---

## 7. Environnement technique cible

- **Backend** : FastAPI + Pydantic + SQLAlchemy
- **Frontend** : Next.js + Tailwind + react-three-fiber
- **DB** : PostgreSQL 16
- **Conteneurs** : Docker Compose (api, web, db)
- **Reverse proxy** : déjà en place sur autre VM
- **Ports** : 3000 (web), 8000 (api) ouverts uniquement depuis reverse proxy

---

## 8. Fonctionnalités spécifiques à venir

- Ajout d’un **canton type** pour servir d’exemple test
- Intégration des variations météo (vent/température) dans un module futur
- Export PDF, CSV, PNG à ajouter plus tard
- Historique des modifications météo par scénario à ajouter plus tard