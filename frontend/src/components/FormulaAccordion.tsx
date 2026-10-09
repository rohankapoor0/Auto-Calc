import React, { useState } from 'react'
import { ChevronDown, ChevronRight, HelpCircle } from 'lucide-react'

interface FormulaAccordionProps {
  title?: string
  formulas: Record<string, string>
}

export const FormulaAccordion: React.FC<FormulaAccordionProps> = ({
  title = 'Engineering Formulas & Implementation Details',
  formulas,
}) => {
  const [isOpen, setIsOpen] = useState(false)

  if (!formulas || Object.keys(formulas).length === 0) return null

  return (
    <div className="formula-accordion">
      <div
        className="formula-accordion-header"
        onClick={() => setIsOpen(!isOpen)}
        title="Click to toggle formula details"
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <HelpCircle size={15} color="#0284c7" />
          {title}
        </span>
        {isOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
      </div>
      {isOpen && (
        <div className="formula-accordion-content">
          {Object.entries(formulas).map(([key, formula]) => (
            <div key={key} className="formula-item">
              <span className="formula-name">• {key}:</span>
              <span>{formula}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
