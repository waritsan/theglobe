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

interface NewsItem {
  id: string;
  title: string;
  summary: string;
  author: string;
  publishedAt: string;
  category: string;
  imageUrl?: string;
  slug: string;
}

// Get placeholder image based on tags or title
const getPlaceholderImage = (tags: string[], title: string): string => {
  // Default images based on common blog topics
  const defaultImages = [
    'https://images.unsplash.com/photo-1486312338219-ce68e2c6f44d?w=400&h=200&fit=crop', // Laptop/Tech
    'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=200&fit=crop', // Writing
    'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400&h=200&fit=crop', // Learning
    'https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=200&fit=crop', // Ideas
    'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=200&fit=crop', // Mountains
  ];

  // Try to match tags to appropriate images
  if (tags.some(tag => tag.toLowerCase().includes('tech') || tag.toLowerCase().includes('code'))) {
    return 'https://images.unsplash.com/photo-1486312338219-ce68e2c6f44d?w=400&h=200&fit=crop';
  }
  if (tags.some(tag => tag.toLowerCase().includes('writing') || tag.toLowerCase().includes('blog'))) {
    return 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=200&fit=crop';
  }
  if (tags.some(tag => tag.toLowerCase().includes('welcome') || tag.toLowerCase().includes('introduction'))) {
    return 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400&h=200&fit=crop';
  }
  if (tags.some(tag => tag.toLowerCase().includes('nature') || tag.toLowerCase().includes('photography'))) {
    return 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=200&fit=crop';
  }

  // Use title hash to consistently pick the same image for the same title
  const hash = title.split('').reduce((a, b) => {
    a = ((a << 5) - a) + b.charCodeAt(0);
    return a & a;
  }, 0);
  return defaultImages[Math.abs(hash) % defaultImages.length];
};

interface NewsFeedProps {
  onPostClick?: (postId: string) => void;
}

const NewsFeed: React.FC<NewsFeedProps> = ({ onPostClick }) => {
  const { t } = useTranslation();
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>(t('blog.category.all'));

  // Transform blog posts to news feed format
  const transformBlogPosts = (blogPosts: BlogPost[]): NewsItem[] => {
    return blogPosts
      .filter(post => post.published) // Only show published posts
      .map(post => ({
        id: post.id,
        title: post.title,
        summary: post.excerpt || post.content.substring(0, 150) + '...', // Use excerpt or truncate content
        author: post.author,
        publishedAt: post.publishedDate,
        category: post.tags.length > 0 ? post.tags[0] : 'General', // Use first tag as category
        imageUrl: post.imageUrl || getPlaceholderImage(post.tags, post.title), // Use provided image or placeholder
        slug: post.slug
      }));
  };  useEffect(() => {
    const fetchBlogPosts = async () => {
      try {
        setLoading(true);
        const response = await fetch(getApiUrl('/posts'));
        if (!response.ok) {
          throw new Error('Failed to fetch blog posts');
        }
        const blogPosts: BlogPost[] = await response.json();
        setPosts(blogPosts);
        setNews(transformBlogPosts(blogPosts));
      } catch (error) {
        console.error('Error fetching blog posts:', error);
        // Fallback to empty array
        setPosts([]);
        setNews([]);
      } finally {
        setLoading(false);
      }
    };

    fetchBlogPosts();
  }, []);

  const categories = [t('blog.category.all'), ...Array.from(new Set(posts.flatMap(post => post.tags)))];

  const filteredNews = selectedCategory === t('blog.category.all')
    ? news
    : news.filter(item => item.category === selectedCategory);

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
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-6"></div>
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
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          {t('blog.title')}
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          {t('blog.subtitle')}
        </p>
      </div>

      {/* Category Filter */}
      <div className="mb-6">
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                selectedCategory === category
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
              }`}
            >
              {category}
            </button>
          ))}
        </div>
      </div>

      {/* Blog Posts */}
      <div className="space-y-6">
        {filteredNews.map((item) => (
          <article
            key={item.id}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden border border-gray-200 dark:border-gray-700"
          >
            {item.imageUrl && (
              <div className="h-48 bg-gray-200 dark:bg-gray-700 overflow-hidden cursor-pointer" onClick={() => onPostClick?.(item.id)}>
                <img
                  src={item.imageUrl}
                  alt={item.title}
                  className="w-full h-full object-cover hover:scale-105 transition-transform duration-200"
                />
              </div>
            )}
            <div className="p-6">
              <div className="flex items-center justify-between mb-3">
                <span className="inline-block px-2 py-1 text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full">
                  {item.category}
                </span>
                <time className="text-sm text-gray-500 dark:text-gray-400">
                  {formatDate(item.publishedAt)}
                </time>
              </div>
              <h2
                className="text-xl font-semibold text-gray-900 dark:text-white mb-3 hover:text-blue-600 dark:hover:text-blue-400 cursor-pointer transition-colors"
                onClick={() => onPostClick?.(item.id)}
              >
                {item.title}
              </h2>

              <p className="text-gray-600 dark:text-gray-300 mb-4 leading-relaxed">
                {item.summary}
              </p>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center mr-3">
                    <span className="text-sm font-medium text-gray-600 dark:text-gray-300">
                      {item.author.split(' ').map(n => n[0]).join('')}
                    </span>
                  </div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {item.author}
                  </span>
                </div>

                <button
                  className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm font-medium transition-colors"
                  onClick={() => onPostClick?.(item.id)}
                >
                  {t('blog.readMore')}
                </button>
              </div>
            </div>
          </article>
        ))}
      </div>

      {filteredNews.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">
            {t('blog.noPosts')}
          </p>
        </div>
      )}
    </div>
  );
};

export default NewsFeed;
