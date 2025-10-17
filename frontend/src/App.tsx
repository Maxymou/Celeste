import React from 'react'
import './styles/App.css'

const projects = [
  {
    id: 1,
    title: '63kV Asasp - Legugnon',
    range: 'Du 92 au 100',
    pylons: '8 pylônes',
    note: 'Proximité géométrique dans la portée 93',
    updated: 'Mise à jour le 12 Octobre 2025',
  },
  {
    id: 2,
    title: '63kV Aire - Hagetmau',
    range: 'Du 13 au 20',
    pylons: '12 pylônes',
    note: 'Maintenance dans la portée 16-17',
    updated: 'Mise à jour le 12 Septembre 2025',
  },
  {
    id: 3,
    title: '150kV Bastillac - Jurançon',
    range: 'Du 102 au 108',
    pylons: '12 pylônes',
    note: "Changement d'isolateurs aux pylônes 15 et 17",
    updated: 'Mise à jour le 7 Juin 2025',
  },
  {
    id: 4,
    title: '225kV Berge - Marsillon',
    range: 'Du 10 au 32',
    pylons: '12 pylônes',
    note: 'Inspection préventive sur la portée 18',
    updated: 'Mise à jour le 5 Mai 2025',
  },
]

type NavItem = {
  id: string
  label: string
  icon: () => JSX.Element
  variant?: 'primary'
  isActive?: boolean
  ariaLabel?: string
}

const navItems: NavItem[] = [
  { id: 'home', label: 'Accueil', icon: HomeIcon, isActive: true, ariaLabel: 'Revenir à l’accueil' },
  { id: 'cables', label: 'Câbles', icon: CableIcon, ariaLabel: 'Accéder aux câbles' },
  { id: 'create', label: 'Nouveau chantier', icon: PlusIcon, variant: 'primary', ariaLabel: 'Créer un nouveau chantier' },
  { id: 'pylons', label: 'Pylônes', icon: PylonIcon, ariaLabel: 'Consulter les pylônes' },
  { id: 'papoto', label: 'PAPOTO', icon: PapotoIcon, ariaLabel: 'Ouvrir la page PAPOTO' },
]

export default function App() {
  return (
    <div className="app-screen">
      <header className="screen-header">
        <button type="button" className="icon-button" aria-label="Ouvrir le menu">
          <MenuIcon />
        </button>

        <div className="header-title-block">
          <time className="screen-clock" dateTime="09:41" aria-hidden="true">
            9:41
          </time>
          <span className="app-title">CELESTE</span>
        </div>

        <button type="button" className="icon-button profile-button" aria-label="Voir le profil">
          <ProfileIcon />
        </button>
      </header>

      <main className="screen-content" role="main">
        <section className="section-heading" aria-label="Chantiers en cours">
          <h2>Mes chantiers</h2>
        </section>

        <section className="projects-list">
          {projects.map((project) => (
            <article key={project.id} className="project-card">
              <header className="project-card-header">
                <h3>{project.title}</h3>
                <span className="project-pylons">{project.pylons}</span>
              </header>
              <p className="project-range">{project.range}</p>
              <p className="project-note">{project.note}</p>
              <p className="project-updated">{project.updated}</p>
            </article>
          ))}
        </section>
      </main>

      <nav className="bottom-nav" aria-label="Navigation principale">
        {navItems.map(({ id, label, icon: Icon, isActive, variant, ariaLabel }) => {
          const classes = [
            'nav-button',
            variant ? `nav-button--${variant}` : '',
            isActive ? 'is-active' : '',
          ]
            .filter(Boolean)
            .join(' ')

          return (
            <button
              key={id}
              type="button"
              className={classes}
              aria-current={isActive ? 'page' : undefined}
              aria-label={ariaLabel}
              title={label}
            >
              <Icon />
              <span className="sr-only">{label}</span>
            </button>
          )
        })}
      </nav>
    </div>
  )
}

function MenuIcon() {
  return (
    <svg viewBox="0 0 24 24" role="img" aria-hidden="true" focusable="false">
      <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  )
}

function ProfileIcon() {
  return (
    <svg viewBox="0 0 24 24" role="img" aria-hidden="true" focusable="false">
      <circle cx="12" cy="8" r="4.25" stroke="currentColor" strokeWidth="2" fill="none" />
      <path d="M4.5 20c1.8-3.2 4.7-5 7.5-5s5.7 1.8 7.5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" fill="none" />
    </svg>
  )
}

function HomeIcon() {
  return (
    <svg viewBox="0 0 24 24" role="img" aria-hidden="true" focusable="false">
      <path
        d="M4.5 11.5 12 5l7.5 6.5V20a1 1 0 0 1-1 1h-5.5v-5h-3v5H5.5a1 1 0 0 1-1-1z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
        fill="none"
      />
    </svg>
  )
}

function CableIcon() {
  return (
    <svg viewBox="0 0 24 24" role="img" aria-hidden="true" focusable="false">
      <path
        d="M6 7h2.5a2.5 2.5 0 0 1 0 5H7m10-5h-2.5a2.5 2.5 0 0 0 0 5H17"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      <path d="M7 12v6m10-6v6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  )
}

function PlusIcon() {
  return (
    <svg viewBox="0 0 24 24" role="img" aria-hidden="true" focusable="false">
      <path d="M12 6v12M6 12h12" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
    </svg>
  )
}

function PylonIcon() {
  return (
    <svg viewBox="0 0 24 24" role="img" aria-hidden="true" focusable="false">
      <path
        d="M12 3 8.5 21m3.5-18 3.5 18M7 9h10M6 13h12M5 17h14"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
    </svg>
  )
}

function PapotoIcon() {
  return (
    <svg viewBox="0 0 24 24" role="img" aria-hidden="true" focusable="false">
      <path
        d="M6.5 5h11A2.5 2.5 0 0 1 20 7.5v5A2.5 2.5 0 0 1 17.5 15H16l-4 4v-4h-5A2.5 2.5 0 0 1 4.5 12.5v-5A2.5 2.5 0 0 1 7 5h-.5z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
        fill="none"
      />
    </svg>
  )
}
