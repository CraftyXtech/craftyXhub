import React from 'react'
import PropTypes from 'prop-types'
import { formatDistanceToNow } from '../../utils/dateUtils'

const AutoSaveIndicator = ({ status, lastSaved, error }) => {
    const getStatusIcon = () => {
        switch (status) {
            case 'saving':
                return <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            case 'saved':
                return <i className="feather-check-circle me-2" aria-hidden="true"></i>
            case 'error':
                return <i className="feather-alert-circle me-2" aria-hidden="true"></i>
            default:
                return null
        }
    }

    const getStatusText = () => {
        switch (status) {
            case 'saving':
                return 'Saving...'
            case 'saved':
                return lastSaved ? `Saved ${formatDistanceToNow(lastSaved)}` : 'Saved'
            case 'error':
                return error || 'Failed to save'
            case 'idle':
                return 'No changes'
            default:
                return ''
        }
    }

    const getStatusClass = () => {
        switch (status) {
            case 'saving':
                return 'text-gray-500'
            case 'saved':
                return 'text-green-600'
            case 'error':
                return 'text-red-600'
            default:
                return 'text-gray-400'
        }
    }

    return (
        <div className={`auto-save-indicator d-flex align-items-center text-sm ${getStatusClass()}`}>
            {getStatusIcon()}
            <span className="d-none d-sm-inline">{getStatusText()}</span>
        </div>
    )
}

AutoSaveIndicator.propTypes = {
    status: PropTypes.oneOf(['idle', 'saving', 'saved', 'error']).isRequired,
    lastSaved: PropTypes.number,
    error: PropTypes.string
}

export default AutoSaveIndicator
