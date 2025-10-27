import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts'
import './Chart.css'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658', '#ff7c7c']

function Chart({ charts }) {
  if (!charts || charts.length === 0) {
    return <div className="no-data">No charts available for this data</div>
  }

  return (
    <div className="charts-container">
      {charts.map((chart, idx) => {
        if (chart.type === 'bar') {
          return (
            <div key={idx} className="chart-wrapper">
              <h4>{chart.title}</h4>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chart.data}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="label" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" fill="#10a37f" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )
        }

        if (chart.type === 'pie') {
          return (
            <div key={idx} className="chart-wrapper">
              <h4>{chart.title}</h4>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={chart.data}
                    dataKey="value"
                    nameKey="label"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label
                  >
                    {chart.data.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )
        }

        if (chart.type === 'line') {
          return (
            <div key={idx} className="chart-wrapper">
              <h4>{chart.title}</h4>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chart.data}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="x" />
                  <YAxis dataKey="y" />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="y" stroke="#10a37f" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )
        }

        return null
      })}
    </div>
  )
}

export default Chart

