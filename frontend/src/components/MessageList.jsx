import React from 'react'
import './MessageList.css'

function MessageList({ messages, loading }) {
  if (messages.length === 0 && !loading) {
    return (
      <div className="empty-chat">
        <h3>Start a conversation</h3>
        <p>Ask questions about your database in plain English.</p>
        <div className="example-questions">
          <p>Example questions:</p>
          <ul>
            <li>"Show me all customers"</li>
            <li>"How many orders are there?"</li>
            <li>"What are the top 10 products by sales?"</li>
            <li>"Show me users where status is active"</li>
          </ul>
        </div>
      </div>
    )
  }

  return (
    <div className="messages-container">
      {messages.map((message, index) => (
        <div key={index} className={`message ${message.role}`}>
          {message.role === 'user' ? (
            <div className="message-content">
              <div className="message-header">
                <strong>You</strong>
              </div>
              <p>{message.content}</p>
            </div>
          ) : (
            <div className="message-content">
              <div className="message-header">
                <strong>Assistant</strong>
              </div>
              <p>{message.content}</p>
              {message.sql_query && (
                <div className="sql-query">
                  <details>
                    <summary>View SQL Query</summary>
                    <pre><code>{message.sql_query}</code></pre>
                  </details>
                </div>
              )}
            </div>
          )}
        </div>
      ))}
      {loading && (
        <div className="message assistant">
          <div className="message-content">
            <div className="loading-indicator">
              <div className="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MessageList

