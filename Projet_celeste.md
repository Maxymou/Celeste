# Projet_CELESTE — Cahier des charges (v1.2)

> **But du document** — Spécifier clairement les besoins, l’architecture et les livrables de l’application CELESTE pour permettre l’implémentation automatique par un agent de développement (ex. Codex/“Godex”) connecté au dépôt GitHub et à la VM Debian 13 sous Proxmox.

---

## 1. Contexte & objectifs

* **Contexte** : Calculs de lignes aériennes (conducteurs & câbles de garde) à partir d’un **catalogue câble** (XML/MDB) et de **règles métier** (chaînette, VHL, Blondel, CR/CRR, vent, température CIGRE, tranchée forestière, etc.).
* **Objectif général** : Une **application web** qui :

  1. importe/maintient le catalogue câble,
  2. permet de créer des projets/portées/supports/scénarios météo,
  3. calcule et **visualise en 2D/3D** (profil en long + scène 3D),
  4. produit des **exports** (PDF/CSV/PNG/GLB),
  5. garde une **traçabilité** (formules utilisées, versions catalogue),
  6. s’intègre à un **pipeline GitHub → VM** pour déploiement rapide.

---

## 2. Périmètre fonctionnel

### 2.1 Données & référentiels

* **Catalogue câble** : issu des fichiers `Câble.xml` et `Couche câble.xml` (composition par couches), et optionnellement de `.mdb` historiques. Champs typiques : désignation, type (conducteur/câble de garde), section, masse linéique, module d’Young E, coefficient de dilatation α, diamètre extérieur, résistivité R20, coefficient de température, charges CRA/CR max, pas & sens de câblage, nature (CU/AL/AA/…), nom PLS‑CADD, commentaires.
* **Versionning catalogue** : stocker la source, la date d’import, et un hash de lot.

### 2.2 Modélisation projet

* **Projet** → **Supports** (ancrage/suspension, coordonnées, altitude d’accrochage, chaîne d’isolateurs, angle de ligne) → **Portées** (distance A‑B).
* **Scénarios** : paramètres météo (vent en daPa et/ou vitesse → pression), température, hypothèses (âge câble/émissivité…), options de validité (contrôles).

### 2.3 Modules de calcul

* **Chaînette & géométrie** : flèche médiane/localisée, corde, point bas, creux, dénivelés — cohérence multi‑portées.
* **Portée équivalente (méthode Blondel)** : calcul de $a_{eq}$ et $K$ pour agrégation.
* **Efforts sur support (VHL)** : composantes H/L, résultante R au droit de chaque support.
* **Vent** : pression/vitesse, limitations de validité (ex. 36 daPa), incidence sur efforts.
* **Température (CIGRE)** : modèle thermique simplifié incluant émissivité (fonction de l’âge) et vitesse de vent minimale (ex. 0,5 m/s), incidence sur allongement/flèches.
* **Charges de rupture** : CRR = CRA − Σ(nbc×crb), CR = min(0,95×CRA, CRR) → **marges** vis‑à‑vis des efforts.
* **Réglage sur poulie/pince** : cas d’équilibre en tirage/détente (rappels statique/moments).
* **Haubanage/levage** : répartition de charge, mouflage (effort au treuil, course).
* **Tranchée forestière** : ½ largeurs AT/DT, hauteur de tranchée (avec marges sécurité).

> **Exigence** : Les résultats doivent préciser les **formules** et **hypothèses** utilisées (références internes aux chapitres), dans les exports et le journal de calcul.

### 2.4 IHM & visualisations

* **2D (profil en long)** : supports, portées (distances), altitudes d’accrochage, flèches, point bas, n° pylône, **VHL & Tacc par côté**.
* **3D (react‑three‑fiber)** :

  * Pylônes matérialisés, chainettes 3D par portée,
  * Visualisation des **angles de ligne** (arc + valeur),
  * Vecteurs **VHL** en 3D au droit des supports,
  * Outils : orbite, zoom, **clipping**, **mise à l’échelle verticale**, grille et gizmo,
  * **Overlays** interactifs (altitudes, portées, flèches),
  * **Exports** : PNG (snapshot) et GLB (scène) en option.
* **Contrôles de validité** : alertes si domaine dépassé (vent, dénivelés, etc.).
* **Exports** : PDF « fiche de calcul » (entrées, formules, résultats, marges), CSV/Excel, image 2D/3D.

---

## 3. Exigences non fonctionnelles

* **Exactitude** : tolérances numériques configurables, tests unitaires sur cas types.
* **Perf** : chargement catalogue (≥ milliers d’entrées) < 2 s en cache, calcul d’un projet test (< 10 portées) < 200 ms côté API.
* **Sécu** : Auth JWT (admin/standard), CORS configuré, journal de calculs.
* **Traçabilité** : version catalogue, paramètres scénario, empreinte (hash) d’inputs.
* **Portabilité** : déploiement via Docker Compose, variables d’environnement.

---

## 4. Architecture cible

### 4.1 Stack

* **DB** : PostgreSQL 16
* **Backend** : FastAPI + Pydantic + SQLAlchemy, Alembic, Uvicorn
* **Frontend** : Next.js (React) + Tailwind + shadcn/ui + react‑three‑fiber (+ drei)
* **Exports PDF** : WeasyPrint (ou wkhtmltopdf)
* **Conteneurs** : Docker Compose

### 4.2 Topologie (sans Nginx local)

* La VM **héberge API (port 8000)** et **WEB (port 3000)** directement.
* Un **reverse proxy Nginx externe** (sur une autre VM Proxmox que possède déjà l’utilisateur) publie :

  * `https://celeste.example.com` → front (port 3000 VM CELESTE)
  * `https://api.celeste.example.com` → API (port 8000 VM CELESTE)
* Points durs :

  * Ouvrir les ports 3000/8000 en firewall **uniquement** depuis l’IP du reverse proxy,
  * Activer TLS sur le Nginx externe, gérer CORS côté API.

---

## 5. Schéma de données (proposé)

```
cables(
  id PK, designation, indice, type_usage, section, masse_lineique, E, alpha,
  diam_ext, R20, coeff_temp_R, CRA, CR_max_adm, pas, sens, nature,
  fichier_plscadd, commentaires, source, version_batch, created_at
)

cable_layers(
  id PK, cable_id FK, ordre, nature, sens, diam_brin, nb_brins, cra_brin
)

projects(id PK, name, description, created_by, created_at)

supports(
  id PK, project_id FK, name, type, x, y, z_accrochage, angle_deg,
  chaine_isol_m, extra jsonb
)

spans(id PK, project_id FK, support_a_id FK, support_b_id FK, distance_m)

scenarios(
  id PK, project_id FK, temp_C, vent_daPa, vent_v_ms, age_annees,
  emissivite, v_min_ms, options jsonb
)

results(
  id PK, project_id FK, scenario_id FK, span_id FK,
  fleche_mid_m, fleche_max_m, point_bas_z,
  H, L, R, marge_CR, journal jsonb, created_at
)
```

---

## 6. API — endpoints (exemples)

* `POST /auth/login` — JWT
* `POST /catalog/import?source=xml|mdb` — charge `data/xml/` et `data/mdb/`
* `GET /catalog/cables?query=...` — recherche catalogue
* `POST /projects` / `GET /projects/{id}` / `DELETE /projects/{id}`
* `POST /projects/{id}/supports` — batch create
* `POST /projects/{id}/spans` — batch create
* `POST /projects/{id}/scenarios` — crée un scénario et déclenche `/compute`
* `POST /compute` — {projectId, scenarioId} → calcule et **persiste** `results`
* `GET /projects/{id}/results` — tableaux d’exploitation
* `GET /projects/{id}/profile2d` — DTO dédié à la vue 2D
* `GET /projects/{id}/scene3d` — géométrie/mesh pour la 3D
* `GET /export/pdf?projectId=...&scenarioId=...` — fiche de calcul

**Remarque** : Fournir des **DTO stables** (contrats) + schema OpenAPI.

---

## 7. Frontend — exigences UI

* Page **Catalogue** : recherche + fiche câble (données & couches).
* Page **Projet** : table supports/portées, scénarios, contrôles de validité.
* **Profil 2D** : annotations (altitudes, flèches, distances), VHL/Tacc par côté.
* **Scène 3D** : r3f + drei, interactions, capture **PNG**, export **GLB** (option).
* **Exports** : boutons PDF/CSV/PNG.

---

## 8. Import & ETL

* **XML** (par défaut) : parsing robuste, normalisation unités, upsert sans doublon par `(designation, indice)`.
* **MDB** (option) : via `mdbtools` (CLI `mdb-export` → CSV → import `COPY` Postgres).
* **Scripts** : `etl/import_catalogue.py` (source=xml|mdb), logs d’import, gestion des erreurs.

---

## 9. Déploiement & environnement

### 9.1 Variables d’environnement (exemple `.env`)

```
POSTGRES_USER=celeste_user
POSTGRES_PASSWORD=change_me
POSTGRES_DB=celeste
POSTGRES_HOST=db
POSTGRES_PORT=5432
API_PORT=8000
WEB_PORT=3000
CORS_ORIGINS=https://celeste.example.com
```

### 9.2 Docker Compose (sans Nginx local)

* Services : `db`, `api`, `web` uniquement.
* Ports exposés : `3000:3000` (web), `8000:8000` (api).
* Santé DB (`pg_isready`), dépendances `api` → `db`, `web` → `api`.

### 9.3 Reverse proxy externe (autre VM)

* Deux hôtes : `celeste.example.com` (→ web:3000) et `api.celeste.example.com` (→ api:8000).
* TLS, headers de sécurité, timeouts pour fichiers 3D/PDF.

---

## 10. Sécurité

* Auth **JWT** (Admin/Standard), hachage mots de passe (argon2/bcrypt).
* **CORS** strict (origines autorisées = domaine front).
* Journalisation (audit) : création projets, imports, calculs, exports.
* Exposition API privée (8000) **limitée** au reverse proxy par firewall.

---

## 11. Qualité & tests

* **Unit tests** : modules de calcul (cas types documentés).
* **E2E** : création projet → import catalogue → saisie supports/portées → calcul → export PDF.
* **CI** : lint (ruff/eslint), tests, build images, publication d’artefacts.

---

## 12. Workflow Dev (GitHub ↔ VM ↔ Agent)

1. **Repo GitHub** : dossier type

```
celeste-app/
  backend/
  frontend/
  etl/
  data/xml/            # Câble.xml, Couche câble.xml
  data/mdb/            # *.mdb (si fourni)
  docker-compose.yml
  .env.example
  README.md
  .github/workflows/ci.yml
```

2. **Clés SSH** : générer une clé **sur la VM** (utilisateur dédié), ajouter la **clé publique** au repo (Deploy Key en lecture/écriture) **OU** à un bot user.
3. **GitHub Actions Runner (self‑hosted)** sur la VM (service) pour permettre :

   * `git pull` / build Docker / `docker compose up -d` automatisés,
   * déploiements sur branche `main` ou sur release tag.
4. **Agent (Codex/“Godex”)** : travailler via PRs sur GitHub + pipeline CI ; l’agent **n’a pas besoin d’accès SSH direct** à la VM si le runner déploie.

> **Option**: si l’agent doit aussi lire/écrire des fichiers au runtime (ex. importer les MDB déposés manuellement), exposer un volume `data/` versionné et/ou un job manuel `workflow_dispatch`.

---

## 13. Roadmap & jalons

* **M1 — Skeleton** : structure repo + Compose + Hello API/WEB + import XML minimal + page catalogue (liste).
* **M2 — Calculs cœur** : chaînette, Blondel, VHL, température, CR/CRR; tests unitaires; profil 2D de base.
* **M3 — 3D** : scène r3f (supports, câbles), angles, VHL 3D, captures.
* **M4 — Exports** : PDF/CSV/PNG/GLB, fiche de calcul complète.
* **M5 — Sécurité & CI/CD** : JWT, CORS strict, logs, runner & pipeline.

**Critères d’acceptation** :

* Import XML passe sur les fichiers fournis; au moins 500 entrées câble chargées.
* Projet démo (≥ 4 supports, 3 portées) : résultats numériques plausibles et cohérents.
* Exports PDF/CSV générés sans erreurs.
* Déploiement automatique réussi via GitHub Actions Runner sur la VM.

---

## 14. Annexes

* Formats d’import : conventions d’unités, gestion arrondis, clés de dédoublonnage.
* DTO OpenAPI (à générer dans `backend/openapi.json`).
* Snippets proxy externe (Nginx/Caddy) et firewall.

