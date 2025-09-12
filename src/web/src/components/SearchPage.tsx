import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { getApiUrl } from '../config';

interface BlogPost {
  id: string;
  title: string;
  content: string;
  excerpt: string | null;
  author: string;
  categoryId: string | null;
  tags: string[];
  slug: string;
  published: boolean;
  publishedDate: string;
  createdDate: string;
  updatedDate: string | null;
  imageUrl?: string | null;
}

interface SearchPageProps {
  onPostClick: (postId: string) => void;
  onBack: () => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
}

const SearchPage: React.FC<SearchPageProps> = ({ onPostClick, onBack, searchQuery, setSearchQuery }) => {
  const { t } = useTranslation();
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [filteredPosts, setFilteredPosts] = useState<BlogPost[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoading(true);
        const response = await fetch(getApiUrl('/posts'));
        if (!response.ok) {
          throw new Error('Failed to fetch posts');
        }
        const blogPosts: BlogPost[] = await response.json();
        setPosts(blogPosts);
        setFilteredPosts(blogPosts.filter(post => post.published));
      } catch (error) {
        console.error('Error fetching posts:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []);

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredPosts(posts.filter(post => post.published));
    } else {
      const query = searchQuery.toLowerCase();
      const filtered = posts.filter(post =>
        post.published && (
          post.title.toLowerCase().includes(query) ||
          post.content.toLowerCase().includes(query) ||
          post.excerpt?.toLowerCase().includes(query) ||
          post.author.toLowerCase().includes(query) ||
          post.tags.some(tag => tag.toLowerCase().includes(query))
        )
      );
      setFilteredPosts(filtered);
    }
  }, [searchQuery, posts]);

  const getPlaceholderImage = (tags: string[], title: string): string => {
    const defaultImages = [
      'https://images.unsplash.com/photo-1486312338219-ce68e2c6f44d?w=400&h=200&fit=crop',
      'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=200&fit=crop',
      'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400&h=200&fit=crop',
      'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop',
      'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=200&fit=crop',
    ];

    if (tags.some(tag => tag.toLowerCase().includes('tech') || tag.toLowerCase().includes('code'))) {
      return 'https://images.unsplash.com/photo-1486312338219-ce68e2c6f44d?w=400&h=200&fit=crop';
    }
    if (tags.some(tag => tag.toLowerCase().includes('writing') || tag.toLowerCase().includes('blog'))) {
      return 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=200&fit=crop';
    }

    const hash = title.split('').reduce((a, b) => {
      a = ((a << 5) - a) + b.charCodeAt(0);
      return a & a;
    }, 0);
    return defaultImages[Math.abs(hash) % defaultImages.length];
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="w-full max-w-4xl mx-auto p-6">
        <div className="animate-pulse">
          <div className="h-12 bg-gray-200 dark:bg-gray-700 rounded mb-6"></div>
          {[...Array(3)].map((_, i) => (
            <div key={i} className="border border-gray-200 dark:border-gray-700 rounded-lg p-6 mb-4">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-4"></div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-full mb-2"></div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      {/* Header with Back Button */}
      <div className="mb-6">
        <button
          onClick={onBack}
          className="inline-flex items-center px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors mb-4"
        >
          ← {t('post.backToBlog')}
        </button>
      </div>

      {/* Search Input */}
      <div className="mb-8">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="m21 21-4.35-4.35"></path>
            </svg>
          </div>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t('search.placeholder')}
            className="block w-full pl-10 pr-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            autoFocus
          />
        </div>
      </div>

      {/* Search Results */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          {t('search.title')} {searchQuery && ` - "${searchQuery}"`}
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          {filteredPosts.length} {filteredPosts.length === 1 ? t('search.result') : t('search.results')}
        </p>
      </div>

      {/* Results */}
      <div className="space-y-6">
        {filteredPosts.map((post) => (
          <article
            key={post.id}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden border border-gray-200 dark:border-gray-700"
          >
            {(post.imageUrl || getPlaceholderImage(post.tags, post.title)) && (
              <div className="h-48 bg-gray-200 dark:bg-gray-700 overflow-hidden cursor-pointer" onClick={() => onPostClick(post.id)}>
                <img
                  src={post.imageUrl || getPlaceholderImage(post.tags, post.title)}
                  alt={post.title}
                  className="w-full h-full object-cover hover:scale-105 transition-transform duration-200"
                />
              </div>
            )}
            <div className="p-6">
              <div className="flex items-center justify-between mb-3">
                <span className="inline-block px-2 py-1 text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full">
                  {post.tags.length > 0 ? post.tags[0] : 'Article'}
                </span>
                <time className="text-sm text-gray-500 dark:text-gray-400">
                  {formatDate(post.publishedDate)}
                </time>
              </div>
              <h2
                className="text-xl font-semibold text-gray-900 dark:text-white mb-3 hover:text-blue-600 dark:hover:text-blue-400 cursor-pointer transition-colors"
                onClick={() => onPostClick(post.id)}
              >
                {post.title}
              </h2>

              <p className="text-gray-600 dark:text-gray-300 mb-4 leading-relaxed">
                {post.excerpt || post.content.substring(0, 150) + '...'}
              </p>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center mr-3">
                    <span className="text-sm font-medium text-gray-600 dark:text-gray-300">
                      {post.author.split(' ').map(n => n[0]).join('')}
                    </span>
                  </div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {post.author}
                  </span>
                </div>

                <button
                  className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm font-medium transition-colors"
                  onClick={() => onPostClick(post.id)}
                >
                  {t('blog.readMore')}
                </button>
              </div>
            </div>
          </article>
        ))}
      </div>

      {filteredPosts.length === 0 && searchQuery && (
        <div className="text-center py-12">
          <div className="mb-4">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="m21 21-4.35-4.35"></path>
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            {t('search.noResults')}
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            {t('search.noResultsMessage')}
          </p>
        </div>
      )}

      {filteredPosts.length === 0 && !searchQuery && (
        <div className="text-center py-12">
          <div className="mb-4">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="m21 21-4.35-4.35"></path>
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            {t('search.startSearching')}
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            {t('search.startSearchingMessage')}
          </p>
        </div>
      )}
    </div>
  );
};

export default SearchPage;
