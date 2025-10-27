import React, { useState } from 'react'
import DataTable from './DataTable'
import Chart from './Chart'
import './QueryResult.css'

function QueryResult({ result }) {
  const [activeTab, setActiveTab] = useState('table')

  const { visualizations } = result
  const { summary } = visualizations

  return (
    <div className="query-result">
      <div className="result-header">
        <h3>Query Results</h3>
        <div className="result-summary">
          {summary.row_count > 0 && (
            <span className="result-count">
              {summary.row_count} row{summary.row_count !== 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>

      <div className="result-tabs">
        <button 
          className={activeTab === 'table' ? 'active' : ''}
          onClick={() => setActiveTab('table')}
        >
          Table
        </button>
        <button 
          className={activeTab === 'charts' ? 'active' : ''}
          onClick={() => setActiveTab('charts')}
        >
          Charts
        </button>
        <button 
          className={activeTab === 'summary' ? 'active' : ''}
          onClick={() => setActiveTab('summary')}
        >
          Summary
        </button>
      </div>

      <div className="result-content">
        {activeTab === 'table' && (
          <DataTable data={visualizations.table} />
        )}
        {activeTab === 'charts' && (
          <Chart charts={visualizations.charts} />
        )}
        {activeTab === 'summary' && (
          <div className="summary-content">
            {summary ? (
              <>
                <div className="summary-info">
                  <div className="summary-item">
                    <span className="summary-label">Total Rows:</span>
                    <span className="summary-value">{summary.row_count || summary.total_rows || 0}</span>
                  </div>
                  <div className="summary-item">
                    <span className="summary-label">Columns:</span>
                    <span className="summary-value">{summary.columns ? summary.columns.length : 0}</span>
                  </div>
                </div>

                {summary.columns && summary.columns.length > 0 && (
                  <div className="column-list">
                    <h4>Columns in Results</h4>
                    <div className="column-tags">
                      {summary.columns.map((col, idx) => (
                        <span key={idx} className="column-tag">{col}</span>
                      ))}
                    </div>
                  </div>
                )}

                {summary.numeric_summary && summary.numeric_summary.length > 0 && (
                  <div className="numeric-stats">
                    <h4>Numeric Statistics</h4>
                    <table className="summary-table">
                      <thead>
                        <tr>
                          <th>Column</th>
                          <th>Count</th>
                          <th>Min</th>
                          <th>Max</th>
                          <th>Average</th>
                        </tr>
                      </thead>
                      <tbody>
                        {summary.numeric_summary.map((stat, idx) => (
                          <tr key={idx}>
                            <td>{stat.column}</td>
                            <td>{stat.count}</td>
                            <td>{typeof stat.min === 'number' ? stat.min.toFixed(2) : stat.min}</td>
                            <td>{typeof stat.max === 'number' ? stat.max.toFixed(2) : stat.max}</td>
                            <td>{typeof stat.avg === 'number' ? stat.avg.toFixed(2) : stat.avg}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {(!summary.numeric_summary || summary.numeric_summary.length === 0) && (
                  <div className="no-numeric-stats">
                    <p>No numeric columns found in the results.</p>
                  </div>
                )}
              </>
            ) : (
              <div className="summary-loading">
                <p>Loading summary data...</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default QueryResult

