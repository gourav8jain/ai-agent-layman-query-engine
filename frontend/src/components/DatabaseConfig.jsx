import React, { useState } from 'react'
import axios from 'axios'
import './DatabaseConfig.css'

const API_BASE_URL = 'http://localhost:8000'

function DatabaseConfig({ onConnectionAdded }) {
  const [formData, setFormData] = useState({
    name: 'VCC-DEV',
    host: 'pgsql-server-iol-wallet-dev-westeu.postgres.database.azure.com',
    port: 5432,
    username: 'iol-dev-root',
    password: 'iol-root@1997',
    database: 'iol-vcc-wallet',
    db_type: 'postgresql'
  })
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState(null)
  const [testError, setTestError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    setTestResult(null)
    setTestError(null)
  }

  const handleTest = async () => {
    setTesting(true)
    setTestResult(null)
    setTestError(null)
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/validate-connection`, {
        ...formData,
        port: parseInt(formData.port)
      })
      
      if (response.data.valid) {
        setTestResult('success')
        setTestError(null)
      } else {
        setTestResult('error')
        setTestError(response.data.error || 'Connection failed')
      }
    } catch (error) {
      setTestResult('error')
      setTestError(error.response?.data?.detail || error.message || 'Connection failed')
    } finally {
      setTesting(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    
    try {
      await axios.post(`${API_BASE_URL}/api/databases`, {
        ...formData,
        port: parseInt(formData.port)
      })
      
      alert('Database connection added successfully!')
      onConnectionAdded()
      setFormData({
        name: '',
        host: 'localhost',
        port: 5432,
        username: '',
        password: '',
        database: '',
        db_type: 'postgresql'
      })
    } catch (error) {
      alert(`Error: ${error.response?.data?.detail || error.message}`)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="database-config">
      <div className="config-container">
        <h2>Add Database Connection</h2>
        <p className="config-subtitle">
          Configure a connection to your database. The AI will use this connection to answer your queries.
        </p>

        <form onSubmit={handleSubmit} className="config-form">
          <div className="form-group">
            <label htmlFor="name">Connection Name *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              placeholder="e.g., Production DB"
            />
          </div>

          <div className="form-group">
            <label htmlFor="db_type">Database Type *</label>
            <select
              id="db_type"
              name="db_type"
              value={formData.db_type}
              onChange={handleChange}
              required
            >
              <option value="postgresql">PostgreSQL</option>
              <option value="mysql">MySQL</option>
              <option value="sqlite">SQLite</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="host">Host *</label>
            <input
              type="text"
              id="host"
              name="host"
              value={formData.host}
              onChange={handleChange}
              required
              placeholder="localhost"
            />
          </div>

          <div className="form-group">
            <label htmlFor="port">Port *</label>
            <input
              type="number"
              id="port"
              name="port"
              value={formData.port}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="username">Username *</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password *</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="database">Database Name *</label>
            <input
              type="text"
              id="database"
              name="database"
              value={formData.database}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={handleTest}
              disabled={testing || submitting}
              className="btn-test"
            >
              {testing ? 'Testing...' : 'Test Connection'}
            </button>
          </div>

          {testResult === 'success' && (
            <div className="test-feedback test-success-message">
              <span className="test-icon">✓</span>
              Connection successful! You can now add the database.
            </div>
          )}

          {testResult === 'error' && testError && (
            <div className="test-feedback test-error-message">
              <span className="test-icon">✗</span>
              {testError}
            </div>
          )}

          <button
            type="submit"
            disabled={submitting || testResult !== 'success'}
            className="btn-submit"
          >
            {submitting ? 'Adding...' : 'Add Database'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default DatabaseConfig

