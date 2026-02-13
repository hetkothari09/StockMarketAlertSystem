import React from 'react';

const IntensityFilters = ({ filters, onToggle }) => {
    return (
        <div className="panel intensity-filters-panel">
            <h3 className="panel-header">Movement Filters</h3>
            <div className="toggle-group">
                {/* <label className="toggle-item">
                    <div className="toggle-switch">
                        <input
                            type="checkbox"
                            checked={filters.has('NORMAL')}
                            onChange={() => onToggle('NORMAL')}
                        />
                        <span className="slider"></span>
                    </div>
                    <span>Normal</span>
                </label> */}

                <label className="toggle-item">
                    <div className="toggle-switch">
                        <input
                            type="checkbox"
                            checked={filters.has('HIGH')}
                            onChange={() => onToggle('HIGH')}
                        />
                        <span className="slider"></span>
                    </div>
                    <span style={{ color: 'var(--color-accent)' }}>High</span>
                </label>

                <label className="toggle-item">
                    <div className="toggle-switch">
                        <input
                            type="checkbox"
                            checked={filters.has('VERY HIGH')}
                            onChange={() => onToggle('VERY HIGH')}
                        />
                        <span className="slider"></span>
                    </div>
                    <span style={{ color: 'var(--color-down)', fontWeight: 'bold', fontSize: '11px' }}>Very High</span>
                </label>
            </div>
        </div>
    );
};

export default IntensityFilters;
