import { useMemo, useState } from "react";

import "./App.css";

const TABS = ["Canton", "Portée", "Support", "Câble", "Température"] as const;

type Tab = (typeof TABS)[number];

type HealthStatus = {
  status: string;
};

type Project = {
  id: number;
  title: string;
  range: string;
  pylons: string;
  description: string;
  updatedAt: string;
};

const PROJECTS: Project[] = [
  {
    id: 1,
    title: "63kV Asasp - Legugnon",
    range: "Du 92 au 100",
    pylons: "8 pylônes",
    description: "Proximité géométrique dans la portée 93-94",
    updatedAt: "Mise à jour le 10 Octobre 2025",
  },
  {
    id: 2,
    title: "63kV Aire - Hagetmau",
    range: "Du 102 au 118",
    pylons: "12 pylônes",
    description: "Raccordement prévu le 15 septembre 2025",
    updatedAt: "Mise à jour le 7 Juin 2025",
  },
  {
    id: 3,
    title: "150kV Bastillac - Jurançon",
    range: "Du 18 au 32",
    pylons: "16 pylônes",
    description: "Changement d'isolateurs aux pylônes 15, 16 et 17",
    updatedAt: "Mise à jour le 27 Mai 2025",
  },
  {
    id: 4,
    title: "225kV Berge - Marsillon",
    range: "Du 10 au 32",
    pylons: "18 pylônes",
    description: "Inspection thermique programmée",
    updatedAt: "Mise à jour le 12 Avril 2025",
  },
];

function App() {
  const [activeTab, setActiveTab] = useState<Tab>(TABS[0]);
  const [loading, setLoading] = useState(false);
  const [healthMessage, setHealthMessage] = useState<string | null>(null);
  const tabDescription = useMemo(
    () => `La section ${activeTab.toLowerCase()} sera bientôt disponible.`,
    [activeTab],
  );

  const runHealthCheck = async () => {
    setLoading(true);
    setHealthMessage(null);
    try {
      const response = await fetch("/api/health");
      if (!response.ok) {
        throw new Error(`Erreur ${response.status}`);
      }
      const data = (await response.json()) as HealthStatus;
      setHealthMessage(`API status: ${data.status}`);
    } catch (error) {
      if (error instanceof Error) {
        setHealthMessage(`Échec du contrôle: ${error.message}`);
      } else {
        setHealthMessage("Échec du contrôle: erreur inconnue");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="screen">
        <header className="app-header">
          <div className="app-branding">
            <span className="app-subtitle">Celeste</span>
            <h1>Mes chantiers</h1>
          </div>
          <button className="profile" type="button" aria-label="Mon profil">
            <span>MB</span>
          </button>
        </header>

        <section className="tab-section" aria-label="Sections de l'application">
          <div className="tab-row">
            {TABS.map((tab) => (
              <button
                key={tab}
                className={tab === activeTab ? "chip active" : "chip"}
                onClick={() => setActiveTab(tab)}
                type="button"
              >
                {tab}
              </button>
            ))}
          </div>
          <p className="tab-description">{tabDescription}</p>
        </section>

        <section className="projects" aria-labelledby="projects-title">
          <h2 id="projects-title" className="sr-only">
            Liste des chantiers
          </h2>
          <div className="project-list">
            {PROJECTS.map((project) => (
              <article key={project.id} className="project-card">
                <header className="project-header">
                  <p className="project-voltage">{project.title}</p>
                  <span className="project-pylons">{project.pylons}</span>
                </header>
                <div className="project-body">
                  <p className="project-range">{project.range}</p>
                  <p className="project-description">{project.description}</p>
                </div>
                <footer className="project-footer">{project.updatedAt}</footer>
              </article>
            ))}
          </div>
        </section>

        <section className="health" aria-live="polite">
          <button
            className="health-button"
            type="button"
            onClick={runHealthCheck}
            disabled={loading}
          >
            {loading ? "Vérification..." : "Health check"}
          </button>
          {healthMessage && <p className="health-message">{healthMessage}</p>}
        </section>
      </div>

      <button className="fab" type="button" aria-label="Ajouter un chantier">
        <span>+</span>
      </button>

      <nav className="bottom-nav" aria-label="Navigation principale">
        <button className="nav-item active" type="button">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M3 10.5 12 3l9 7.5V21H3z" />
          </svg>
          <span>Accueil</span>
        </button>
        <button className="nav-item" type="button">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12 4 2 20h20zm0 4.3L17.74 18H6.26z" />
          </svg>
          <span>Favoris</span>
        </button>
        <div className="nav-spacer" aria-hidden="true" />
        <button className="nav-item" type="button">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12 22a2 2 0 0 0 2-2h-4a2 2 0 0 0 2 2Zm6.36-6A7 7 0 0 0 19 10V8a7 7 0 1 0-14 0v2a7 7 0 0 0 .64 6L4 18v1h16v-1z" />
          </svg>
          <span>Alerts</span>
        </button>
        <button className="nav-item" type="button">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8Zm8 4a8 8 0 1 1-16 0 8 8 0 0 1 16 0ZM4 4.5 5.5 6A9.97 9.97 0 0 1 12 4c2.43 0 4.66.87 6.5 2l1.5-1.5" />
          </svg>
          <span>Profil</span>
        </button>
      </nav>
    </div>
  );
}

export default App;
