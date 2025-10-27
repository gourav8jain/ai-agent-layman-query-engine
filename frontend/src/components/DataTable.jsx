import React from 'react'
import './DataTable.css'

function DataTable({ data }) {
  if (!data || !data.rows || data.rows.length === 0) {
    return <div className="no-data">No data available</div>
  }

  const columns = data.columns || []
  const rows = data.rows || []

  return (
    <div className="data-table-container">
      <div className="table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              {columns.map((col, idx) => (
                <th key={idx}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIdx) => (
              <tr key={rowIdx}>
                {columns.map((col, colIdx) => (
                  <td key={colIdx}>{row[col] !== null ? String(row[col]) : 'null'}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {data.row_count > 10 && (
        <div className="table-footer">
          Showing first {Math.min(10, data.row_count)} of {data.row_count} rows
        </div>
      )}
    </div>
  )
}

export default DataTable

