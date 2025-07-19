import React, { memo } from 'react'
import { Row } from 'react-bootstrap'

const BlogFilter = ({ title, filterData, onFilterChange }) => {
  if (!filterData) return null;

  return (
    <Row className="justify-center">
      <div className="col-12 text-center">
        {title && <h5 className="font-serif font-semibold text-darkgray mb-0">{title}</h5>}
        <div className="filter-menu border-0 text-center">
          <ul>
            <li className="mx-3">
              <span 
                className="cursor-pointer text-lg font-serif font-medium text-darkgray hover:text-fastblue transition-default"
                onClick={() => onFilterChange && onFilterChange('*')}
              >
                All
              </span>
            </li>
            {filterData.map((item, i) => (
              <li key={i} className="mx-3">
                <span 
                  className="cursor-pointer text-lg font-serif font-medium text-darkgray hover:text-fastblue transition-default"
                  onClick={() => onFilterChange && onFilterChange(`.${item.category.toLowerCase()}`)}
                >
                  {item.category}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Row>
  )
}

BlogFilter.defaultProps = {
  filterData: []
}

export default memo(BlogFilter) 