import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import MessageList from './MessageList'
import ChatInput from './ChatInput'
import QueryResult from './QueryResult'
import './ChatInterface.css'

const API_BASE_URL = 'http://localhost:8000'

function ChatInterface({ connectionId, connectionName }) {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (message) => {
    if (!message.trim() || !connectionId) return

    const userMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setLoading(true)

    try {
      const response = await axios.post(`${API_BASE_URL}/api/chat`, {
        message,
        db_connection_id: connectionId
      })

      const assistantMessage = {
        role: 'assistant',
        content: response.data.explanation,
        sql_query: response.data.sql_query,
        timestamp: new Date().toISOString()
      }

      setMessages(prev => [...prev, assistantMessage])
      setResult(response.data)

    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${error.response?.data?.detail || error.message}`,
        error: true,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  if (!connectionId) {
    return (
      <div className="chat-empty-state">
        <div className="empty-state-content">
          <h2>No Database Selected</h2>
          <p>Please select a database connection from the sidebar or add a new one.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>{connectionName || 'Chat'}</h2>
        <span className="connection-status">● Connected</span>
      </div>

      <div className="chat-content">
        <MessageList messages={messages} loading={loading} />
        {result && <QueryResult result={result} />}
        <div ref={messagesEndRef} />
      </div>

      <ChatInput 
        onSendMessage={handleSendMessage} 
        disabled={loading}
      />
    </div>
  )
}

export default ChatInterface

