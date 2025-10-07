import React, { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { getApiUrl } from '../config'
import ReactMarkdown from 'react-markdown'
import rehypeSanitize from 'rehype-sanitize'

interface Message {
  id: string
  text: string
  sender: 'user' | 'ai'
  timestamp: Date
}

interface ChatPageProps {
  onBack: () => void
}

const ChatPage: React.FC<ChatPageProps> = ({ onBack }) => {
  const { t } = useTranslation()
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: t('chat.welcome'),
      sender: 'ai',
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [conversationId, setConversationId] = useState<string>('')
  const [retryUntil, setRetryUntil] = useState<number | null>(null)
  const [retrySecondsLeft, setRetrySecondsLeft] = useState<number>(0)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const clearChatHistory = () => {
    setMessages([
      {
        id: '1',
        text: t('chat.welcome'),
        sender: 'ai',
        timestamp: new Date()
      }
    ])
    setConversationId('')
    localStorage.removeItem('chatMessages')
    localStorage.removeItem('conversationId')
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Load conversation history from localStorage on component mount
  useEffect(() => {
    const savedMessages = localStorage.getItem('chatMessages')
    const savedConversationId = localStorage.getItem('conversationId')
    
    if (savedMessages) {
      try {
        const parsedMessages = JSON.parse(savedMessages)
        // Only load if there are actual conversation messages (more than just welcome)
        if (parsedMessages.length > 1) {
          // Normalize timestamps (they are serialized as strings in localStorage)
          const normalized = parsedMessages.map((m: any) => ({
            ...m,
            timestamp: m.timestamp ? new Date(m.timestamp) : new Date()
          }))
          setMessages(normalized)
        }
      } catch (error) {
        console.error('Failed to parse saved messages:', error)
      }
    }
    
    if (savedConversationId) {
      setConversationId(savedConversationId)
    }
  }, [])

  // Save conversation history to localStorage whenever messages change
  useEffect(() => {
    if (messages.length > 1) { // Don't save if only welcome message
      localStorage.setItem('chatMessages', JSON.stringify(messages))
    }
  }, [messages])

  // Save conversation ID to localStorage
  useEffect(() => {
    if (conversationId) {
      localStorage.setItem('conversationId', conversationId)
    }
  }, [conversationId])

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue.trim(),
      sender: 'user',
      timestamp: new Date()
    }

    // Add user message to state immediately for UI feedback
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsTyping(true)

    try {
      // Prepare conversation history (exclude welcome message only - don't include current message)
      const conversationHistory = messages
        .filter(msg => !msg.text.includes('สวัสดีค่ะ ดิฉันเป็นผู้ช่วย AI')) // Exclude welcome message
        .slice(-10) // Keep last 10 messages to avoid token limits
        .map(msg => ({
          role: msg.sender === 'user' ? 'user' : 'assistant',
          content: msg.text
        }))

      // Call the actual chat API with conversation history
      const response = await fetch(getApiUrl('/chat'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: userMessage.text,
          conversation_history: conversationHistory,
          conversation_id: conversationId || undefined
        }),
      })

      if (!response.ok) {
        if (response.status === 429) {
          // Try to get Retry-After header (seconds) or parse body
          const ra = response.headers.get('Retry-After')
          let retrySec = 60
          if (ra) {
            const asNum = parseInt(ra, 10)
            if (!isNaN(asNum)) retrySec = asNum
          } else {
            try {
              const body = await response.json()
              const m = (body?.detail || '').match(/(\d+)\s*second/)
              if (m) retrySec = parseInt(m[1], 10)
            } catch (e) {
              // ignore
            }
          }

          const until = Date.now() + retrySec * 1000
          setRetryUntil(until)
          setRetrySecondsLeft(retrySec)

          const errorMessage: Message = {
            id: (Date.now() + 1).toString(),
            text: `Rate limit exceeded. Try again in ${retrySec} seconds.`,
            sender: 'ai',
            timestamp: new Date()
          }
          setMessages(prev => [...prev, errorMessage])
          setIsTyping(false)
          return
        }

        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response,
        sender: 'ai',
        timestamp: new Date()
      }
      
      // Add AI message to state
      setMessages(prev => [...prev, aiMessage])
      
      // Store conversation ID
      if (data.conversation_id) {
        setConversationId(data.conversation_id)
      }
    } catch (error) {
      console.error('Chat API error:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error. Please try again later.',
        sender: 'ai',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  // Countdown effect for retry
  useEffect(() => {
    if (!retryUntil) {
      setRetrySecondsLeft(0)
      return
    }
    const tick = () => {
      const secs = Math.max(0, Math.ceil((retryUntil - Date.now()) / 1000))
      setRetrySecondsLeft(secs)
      if (secs <= 0) setRetryUntil(null)
    }

    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [retryUntil])

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          {t('chat.backToBlog')}
        </button>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          {t('chat.title')}
        </h1>
        <div className="flex items-center gap-2">
          <button
            onClick={clearChatHistory}
            className="flex items-center gap-2 px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
            title="Clear chat history"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Clear
          </button>
        </div>
      </div>

      {/* Chat Container */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 h-[600px] flex flex-col">
        {/* Retry banner when rate-limited */}
        {retryUntil && (
          <div className="bg-yellow-100 dark:bg-yellow-900 text-yellow-900 dark:text-yellow-200 px-4 py-2 rounded-t-lg">
            Rate limit in effect. Please wait {retrySecondsLeft} second{retrySecondsLeft === 1 ? '' : 's'} before sending more messages.
          </div>
        )}
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.sender === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                }`}
              >
                {message.sender === 'ai' ? (
                  <div className="prose prose-sm max-w-none dark:prose-invert">
                    <ReactMarkdown rehypePlugins={[rehypeSanitize]}>
                      {message.text}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <p className="text-sm">{message.text}</p>
                )}
                <p className={`text-xs mt-1 ${
                  message.sender === 'user'
                    ? 'text-blue-100'
                    : 'text-gray-500 dark:text-gray-400'
                }`}>
                  {(
                    (message.timestamp instanceof Date) ? message.timestamp : new Date(message.timestamp)
                  ).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-gray-100 dark:bg-gray-700 px-4 py-2 rounded-lg">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-4">
          <div className="flex gap-2">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={t('chat.placeholder')}
              disabled={isTyping || !!retryUntil}
              className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
              
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isTyping || !!retryUntil}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatPage
