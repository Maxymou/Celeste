# Guide de contribution - CELESTE X

Merci de votre intérêt pour contribuer à CELESTE X ! Ce document vous guide dans le processus de contribution.

## 🚀 Démarrage rapide

### Installation pour le développement

```bash
# Cloner le repository
git clone https://github.com/Maxymou/CELESTE.git
cd CELESTE

# Frontend
cd frontend
npm install
npm run dev

# Backend (nouveau terminal)
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install sqladmin
uvicorn main:app --reload

# Admin (nouveau terminal)
cd backend_admin
source ../.venv/bin/activate
export CELESTEX_DB_PATH=../data/celestex.db
export ADMIN_USER=admin
export ADMIN_PASS=admin123
export ADMIN_SECRET=change-me
uvicorn main:app --reload --port 8000
```

## 📋 Processus de contribution

1. **Fork** le repository
2. **Créer** une branche pour votre fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`)
3. **Commiter** vos changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. **Pousser** vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. **Créer** une Pull Request

## 🧪 Tests

### Tests backend
```bash
cd backend
python -m pytest
```

### Tests frontend
```bash
cd frontend
npm test
```

### Tests d'intégration
```bash
./check.sh
```

## 📝 Standards de code

### Python
- Utiliser `black` pour le formatage
- Suivre PEP 8
- Ajouter des docstrings pour les fonctions
- Type hints recommandés

### TypeScript/React
- Utiliser `prettier` pour le formatage
- ESLint pour la qualité du code
- Composants fonctionnels avec hooks
- Props typées avec TypeScript

### Git
- Messages de commit clairs et descriptifs
- Une fonctionnalité par commit
- Branches nommées selon le type : `feature/`, `fix/`, `docs/`, `refactor/`

## 🐛 Signaler un bug

Utilisez le template d'issue GitHub avec :
- Description claire du problème
- Étapes pour reproduire
- Environnement (OS, versions)
- Logs d'erreur si applicable

## ✨ Proposer une fonctionnalité

Utilisez le template d'issue GitHub avec :
- Description de la fonctionnalité
- Cas d'usage
- Mockups/wireframes si applicable
- Impact sur l'existant

## 📚 Documentation

- Mettre à jour le README si nécessaire
- Ajouter des commentaires dans le code
- Documenter les nouvelles API
- Mettre à jour le CHANGELOG

## 🔒 Sécurité

Pour signaler des vulnérabilités de sécurité, contactez-nous en privé plutôt que d'ouvrir une issue publique.

## 📞 Support

- Issues GitHub pour les bugs et fonctionnalités
- Discussions GitHub pour les questions générales
- Email pour les questions privées

Merci de contribuer à CELESTE X ! 🎉
