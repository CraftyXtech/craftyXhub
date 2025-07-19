import React from 'react'

const PortfolioPlaceholder = ({ data, ...props }) => {
  return (
    <div className="portfolio-placeholder">
      <div className="text-center py-20">
        <h3 className="text-darkgray font-medium mb-4">Portfolio Section</h3>
        <p className="text-mediumgray">Portfolio components have been removed for blog-focused design.</p>
      </div>
    </div>
  )
}

export default PortfolioPlaceholder 