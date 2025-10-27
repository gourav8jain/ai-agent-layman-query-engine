import React, { useState } from 'react'
import './ChatInput.css'

function ChatInput({ onSendMessage, disabled }) {
  const [input, setInput] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim() || disabled) return
    
    onSendMessage(input)
    setInput('')
  }

  return (
    <div className="chat-input-container">
      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about your data..."
          disabled={disabled}
          className="chat-input"
        />
        <button 
          type="submit" 
          disabled={disabled || !input.trim()}
          className="send-button"
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M2 10L18 2L11 19L9 11L2 10Z" fill="currentColor"/>
          </svg>
        </button>
      </form>
    </div>
  )
}

export default ChatInput

