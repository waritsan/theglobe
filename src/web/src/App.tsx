import './App.css'
import { useState, useEffect } from 'react'
import NewsFeed from './components/NewsFeed'
import AdminPage from './components/AdminPage'
import BlogPostDetail from './components/BlogPostDetail'
import LanguageSwitcher from './components/LanguageSwitcher'
import SearchPage from './components/SearchPage'
import ChatPage from './components/ChatPage'
import { useTranslation } from 'react-i18next'

type ViewType = 'blog' | 'admin' | 'post-detail' | 'search' | 'chat'

function App() {
  const [currentView, setCurrentView] = useState<ViewType>('blog')
  const [selectedPostId, setSelectedPostId] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const { t } = useTranslation()

  // Handle browser back/forward navigation
  useEffect(() => {
    const handlePopState = (event: PopStateEvent) => {
      if (event.state?.view) {
        setCurrentView(event.state.view)
        setSelectedPostId(event.state.postId || '')
      }
    }

    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  }, [])

  const navigateToPost = (postId: string) => {
    setSelectedPostId(postId)
    setCurrentView('post-detail')
    // Update browser history
    window.history.pushState({ view: 'post-detail', postId }, '', `/post/${postId}`)
  }

  const navigateToBlog = () => {
    setCurrentView('blog')
    setSelectedPostId('')
    // Update browser history
    window.history.pushState({ view: 'blog' }, '', '/')
  }

  const navigateToAdmin = () => {
    setCurrentView('admin')
    setSelectedPostId('')
    // Update browser history
    window.history.pushState({ view: 'admin' }, '', '/admin')
  }

  const navigateToSearch = () => {
    setCurrentView('search')
    setSelectedPostId('')
    // Update browser history
    window.history.pushState({ view: 'search' }, '', '/search')
  }

  const navigateToChat = () => {
    setCurrentView('chat')
    setSelectedPostId('')
    // Update browser history
    window.history.pushState({ view: 'chat' }, '', '/chat')
  }

  // Handle initial load with URL parameters
  useEffect(() => {
    const path = window.location.pathname
    if (path.startsWith('/post/')) {
      const postId = path.split('/post/')[1]
      if (postId) {
        setSelectedPostId(postId)
        setCurrentView('post-detail')
      }
    } else if (path === '/admin') {
      setCurrentView('admin')
    } else if (path === '/search') {
      setCurrentView('search')
    } else if (path === '/chat') {
      setCurrentView('chat')
    } else {
      setCurrentView('blog')
    }
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <button
                onClick={navigateToBlog}
                className={`p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors ${
                  currentView === 'blog' ? 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-400' : ''
                }`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <line x1="3" y1="6" x2="21" y2="6"></line>
                  <line x1="3" y1="12" x2="21" y2="12"></line>
                  <line x1="3" y1="18" x2="21" y2="18"></line>
                </svg>
              </button>
            </div>
            <div className="flex items-center gap-x-3">
              <img className="size-8 shrink-0" src="/theglobe-icon.jpg" alt="The Globe Logo" />
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">{t('header.title')}</h1>
            </div>
            <nav className="flex items-center gap-x-3">
              <LanguageSwitcher />
              <button
                onClick={navigateToAdmin}
                className={`p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors ${
                  currentView === 'admin' ? 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-400' : ''
                }`}
                title="Admin Panel"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 1l3 6 6 3-6 3-3 6-3-6-6-3 6-3z"></path>
                </svg>
              </button>
              <button 
                onClick={navigateToSearch}
                className="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title={t('nav.search')}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="11" cy="11" r="8"></circle>
                  <path d="m21 21-4.35-4.35"></path>
                </svg>
              </button>
              <button
                onClick={navigateToChat}
                className={`p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors ${
                  currentView === 'chat' ? 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-400' : ''
                }`}
                title={t('nav.chat')}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
              </button>
              <button className="relative p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M6 8a6 6 0 1 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path>
                  <path d="m13.73 21a2 2 0 0 1-3.46 0"></path>
                </svg>
                {/* Notification badge */}
                <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                  3
                </span>
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="py-8">
        {currentView === 'blog' && <NewsFeed onPostClick={navigateToPost} />}
        {currentView === 'admin' && <AdminPage />}
        {currentView === 'search' && (
          <SearchPage 
            onPostClick={navigateToPost} 
            onBack={navigateToBlog}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
          />
        )}
        {currentView === 'chat' && (
          <ChatPage onBack={navigateToBlog} />
        )}
        {currentView === 'post-detail' && (
          <BlogPostDetail postId={selectedPostId} onBack={navigateToBlog} />
        )}
      </main>
    </div>
  )
}

export default App
