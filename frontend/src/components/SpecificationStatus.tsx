import React from 'react'
import type { FieldStatus } from '../types'

interface SpecificationStatusProps {
  status: FieldStatus | string
  rationale?: string
  note?: string
  showText?: boolean
}

export const SpecificationStatus: React.FC<SpecificationStatusProps> = ({
  status,
  rationale,
  note,
  showText = true,
}) => {
  const normStatus = (status || '').toLowerCase()

  if (normStatus === 'verified' || normStatus === 'specified / given') {
    return (
      <span
        className="origin-tag origin-tag-given"
        title="Manufacturer-published and verified technical specification"
      >
        {showText ? 'Verified' : 'V'}
      </span>
    )
  }

  if (normStatus === 'assumed') {
    return (
      <span
        className="origin-tag origin-tag-assumed"
        title={rationale ? `Assumed: ${rationale}` : 'Engineering modelling assumption'}
      >
        {showText ? 'Assumed' : 'A'}
      </span>
    )
  }

  if (normStatus === 'unavailable') {
    return (
      <span
        className="origin-tag"
        style={{ background: '#f1f5f9', color: '#64748b', border: '1px solid #cbd5e1' }}
        title={note ? `Unavailable: ${note}` : 'Data not published by manufacturer'}
      >
        {showText ? 'Unavailable' : 'N/A'}
      </span>
    )
  }

  return (
    <span className="origin-tag origin-tag-const">
      {status}
    </span>
  )
}
