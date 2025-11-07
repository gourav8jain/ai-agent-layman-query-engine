import React, { useState, useEffect } from 'react'
import ChatInterface from './components/ChatInterface'
import DatabaseConfig from './components/DatabaseConfig'
import axios from 'axios'
import { API_BASE_URL } from './config'
import './App.css'

function App() {
  const [connections, setConnections] = useState([])
  const [activeConnection, setActiveConnection] = useState(null)
  const [showConfig, setShowConfig] = useState(false)

  useEffect(() => {
    fetchConnections()
  }, [])

  const fetchConnections = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/databases`)
      setConnections(response.data.connections || {})
    } catch (error) {
      console.error('Error fetching connections:', error)
    }
  }

  const handleConnectionAdded = () => {
    fetchConnections()
    setShowConfig(false)
  }

  const handleDeleteConnection = async (connectionId) => {
    try {
      await axios.delete(`${API_BASE_URL}/api/databases/${connectionId}`)
      fetchConnections()
      if (activeConnection === connectionId) {
        setActiveConnection(null)
      }
    } catch (error) {
      console.error('Error deleting connection:', error)
      alert('Error deleting connection')
    }
  }

  const connectionsList = Object.entries(connections).map(([id, conn]) => ({
    id,
    name: conn.name,
    database: conn.database
  }))

  return (
    <div className="app">
      <div className="sidebar">
        <div className="sidebar-header">
          <h1>AI Query Engine</h1>
          <button 
            className="btn-primary" 
            onClick={() => setShowConfig(!showConfig)}
          >
            {showConfig ? 'Back to Chat' : '+ Add Database'}
          </button>
        </div>

        <div className="connections-list">
          <h3>Database Connections</h3>
          {connectionsList.length === 0 ? (
            <p className="no-connections">No connections configured</p>
          ) : (
            <div className="connections">
              {connectionsList.map((conn) => (
                <div 
                  key={conn.id} 
                  className={`connection-item ${activeConnection === conn.id ? 'active' : ''}`}
                  onClick={() => setActiveConnection(conn.id)}
                >
                  <div className="connection-info">
                    <strong>{conn.name}</strong>
                    <span>{conn.database}</span>
                  </div>
                  <button 
                    className="delete-btn"
                    onClick={(e) => {
                      e.stopPropagation()
                      if (window.confirm(`Delete ${conn.name}?`)) {
                        handleDeleteConnection(conn.id)
                      }
                    }}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="main-content">
        {showConfig ? (
          <DatabaseConfig onConnectionAdded={handleConnectionAdded} />
        ) : (
          <ChatInterface 
            connectionId={activeConnection} 
            connectionName={connectionsList.find(c => c.id === activeConnection)?.name}
          />
        )}
      </div>
    </div>
  )
}

export default App

