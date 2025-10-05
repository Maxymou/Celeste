import React from 'react'

const tabs = ["Support", "Câble"] as const
type Tab = typeof tabs[number]

export function Tabs({ active, onChange }: { active: Tab; onChange: (t: Tab) => void }) {
  return (
    <div className="tabs" role="tablist" aria-label="Navigation principale">
      {tabs.map((tab) => {
        const isActive = tab === active

        return (
          <button
            key={tab}
            type="button"
            role="tab"
            aria-selected={isActive}
            className={`tab-button${isActive ? ' is-active' : ''}`}
            onClick={() => onChange(tab)}
          >
            {tab}
          </button>
        )
      })}
    </div>
  )
}
