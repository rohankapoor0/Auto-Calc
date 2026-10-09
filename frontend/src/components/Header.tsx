import React from 'react'
import { Play, RotateCcw } from 'lucide-react'

interface HeaderProps {
  title: string
  subtitle?: string
  isCalculating: boolean
  onCalculateAll: () => void
  onResetDefaults?: () => void
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle = 'Hyundai Creta 1.5 U2 CRDi Diesel | 6-Speed Manual | FWD',
  isCalculating,
  onCalculateAll,
  onResetDefaults,
}) => {
  return (
    <header className="top-header">
      <div className="header-titles">
        <h1 className="header-main-title">{title}</h1>
        <div className="header-subtitle">{subtitle}</div>
      </div>

      <div className="header-actions">
        {onResetDefaults && (
          <button
            className="btn btn-outline"
            onClick={onResetDefaults}
            disabled={isCalculating}
            title="Reset all modified specifications to Python defaults"
          >
            <RotateCcw size={15} />
            <span>Reset Defaults</span>
          </button>
        )}

        <button
          className="btn btn-primary"
          onClick={onCalculateAll}
          disabled={isCalculating}
        >
          {isCalculating ? (
            <>
              <div className="spinner" />
              <span>Calculating...</span>
            </>
          ) : (
            <>
              <Play size={16} fill="currentColor" />
              <span>Calculate All</span>
            </>
          )}
        </button>
      </div>
    </header>
  )
}
