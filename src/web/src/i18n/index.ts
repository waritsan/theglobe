import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Translation resources
const resources = {
  en: {
    translation: {
      // Navigation
      "nav.blog": "Blog",
      "nav.admin": "Admin",
      "nav.search": "Search",
      "nav.notifications": "Notifications",
      "nav.chat": "AI Chat",

      // Header
      "header.title": "The Globe",
      "header.subtitle": "Live Development!",

      // Blog Feed
      "blog.title": "Blog Posts",
      "blog.subtitle": "Discover insights, tutorials, and stories from our community",
      "blog.category.all": "All",
      "blog.readMore": "Read full post →",
      "blog.noPosts": "No blog posts found in this category.",
      "blog.loading": "Loading blog posts...",

      // Post Detail
      "post.backToBlog": "Back to Blog",
      "post.backToPosts": "Back to All Posts",
      "post.notFound": "Post not found",
      "post.notFoundMessage": "The blog post you're looking for doesn't exist or has been removed.",
      "post.loading": "Loading post...",
      "post.error": "Failed to load the blog post. Please try again.",

      // Admin
      "admin.title": "Blog Admin",
      "admin.createPost": "Create New Post",
      "admin.editPost": "Edit Post",
      "admin.deletePost": "Delete Post",
      "admin.save": "Save",
      "admin.cancel": "Cancel",
      "admin.confirmDelete": "Are you sure you want to delete this post?",
      "admin.postTitle": "Title",
      "admin.postContent": "Content",
      "admin.postExcerpt": "Excerpt",
      "admin.postAuthor": "Author",
      "admin.postTags": "Tags",
      "admin.postImageUrl": "Image URL",
      "admin.postPublished": "Published",
      "admin.postSlug": "Slug",

      // Chat
      "chat.title": "AI Assistant",
      "chat.welcome": "Hello! I'm your AI assistant powered by Azure AI. I'm now live and ready to help you!",
      "chat.placeholder": "Type your message here...",
      "chat.backToBlog": "Back to Blog",
      "chat.info.title": "AI Chat",
      "chat.info.description": "Chat with our AI assistant powered by Azure AI Foundry. Now live with real AI responses!",

      // Common
      "common.loading": "Loading...",
      "common.error": "An error occurred",
      "common.retry": "Try again",
      "common.yes": "Yes",
      "common.no": "No",
      "common.save": "Save",
      "common.cancel": "Cancel",
      "common.delete": "Delete",
      "common.edit": "Edit",
      "common.view": "View",

      // Language
      "lang.english": "English",
      "lang.thai": "ไทย",
      "lang.french": "Français",
      "lang.german": "Deutsch",
      "lang.chinese": "中文",
      "lang.japanese": "日本語",

      // Date/Time
      "date.format": "{{date, dd/MM/yyyy}}",
      "date.relative.now": "Just now",
      "date.relative.minutes": "{{count}} minute ago",
      "date.relative.minutes_plural": "{{count}} minutes ago",
      "date.relative.hours": "{{count}} hour ago",
      "date.relative.hours_plural": "{{count}} hours ago",
      "date.relative.days": "{{count}} day ago",
      "date.relative.days_plural": "{{count}} days ago",

      // Search
      "search.title": "Search Articles",
      "search.placeholder": "Search articles...",
      "search.results": "results found",
      "search.result": "result found",
      "search.noResults": "No results found",
      "search.noResultsMessage": "Try adjusting your search terms or browse all posts.",
      "search.startSearching": "Start searching",
      "search.startSearchingMessage": "Enter keywords to search through blog posts.",
    }
  },
  th: {
    translation: {
      // Navigation
      "nav.blog": "ข่าวสาร",
      "nav.admin": "ผู้ดูแลระบบ",
      "nav.search": "ค้นหา",
      "nav.notifications": "การแจ้งเตือน",
      "nav.chat": "แชท AI",

      // Header
      "header.title": "The Globe",
      "header.subtitle": "การพัฒนาสด!",

      // Blog Feed
      "blog.title": "ข่าวสาร",
      "blog.subtitle": "ค้นพบข่าวสารและสิทธิประโยชน์จากภาครัฐฯ",
      "blog.category.all": "ทั้งหมด",
      "blog.readMore": "อ่านข่าวเต็ม →",
      "blog.noPosts": "ไม่พบข่าวข่าวสารในหมวดหมู่นี้",
      "blog.loading": "กำลังโหลดข่าวข่าวสาร...",

      // Post Detail
      "post.backToBlog": "กลับไปที่ข่าวสาร",
      "post.backToPosts": "กลับไปที่ข่าวทั้งหมด",
      "post.notFound": "ไม่พบข่าว",
      "post.notFoundMessage": "ข่าวข่าวสารที่คุณกำลังมองหาไม่มีอยู่หรือถูกลบไปแล้ว",
      "post.loading": "กำลังโหลดข่าว...",
      "post.error": "ไม่สามารถโหลดข่าวข่าวสารได้ กรุณาลองใหม่อีกครั้ง",

      // Admin
      "admin.title": "ผู้ดูแลระบบข่าวสาร",
      "admin.createPost": "สร้างข่าวใหม่",
      "admin.editPost": "แก้ไขข่าว",
      "admin.deletePost": "ลบข่าว",
      "admin.save": "บันทึก",
      "admin.cancel": "ยกเลิก",
      "admin.confirmDelete": "คุณแน่ใจหรือไม่ว่าต้องการลบข่าวนี้?",
      "admin.postTitle": "หัวข้อ",
      "admin.postContent": "เนื้อหา",
      "admin.postExcerpt": "สรุป",
      "admin.postAuthor": "ผู้เขียน",
      "admin.postTags": "แท็ก",
      "admin.postImageUrl": "URL รูปภาพ",
      "admin.postPublished": "เผยแพร่",
      "admin.postSlug": "Slug",

      // Chat
      "chat.title": "ผู้ช่วย AI",
      "chat.welcome": "สวัสดีค่ะ ดิฉันเป็นผู้ช่วย AI จะมาช่วยตอบคำถามและให้ข้อมูลเกี่ยวกับสวัสดิการภาครัฐ ยินดีให้ความช่วยเหลือค่ะ",
      "chat.placeholder": "พิมพ์ข้อความของคุณที่นี่...",
      "chat.backToBlog": "กลับไปที่ข่าวสาร",
      "chat.info.title": "แชท AI",
      "chat.info.description": "สนทนากับผู้ช่วย AI ของเราโดยใช้ Azure AI Foundry พร้อมการตอบกลับ AI จริงแล้ว!",

      // Common
      "common.loading": "กำลังโหลด...",
      "common.error": "เกิดข้อผิดพลาด",
      "common.retry": "ลองใหม่",
      "common.yes": "ใช่",
      "common.no": "ไม่",
      "common.save": "บันทึก",
      "common.cancel": "ยกเลิก",
      "common.delete": "ลบ",
      "common.edit": "แก้ไข",
      "common.view": "ดู",

      // Language
      "lang.english": "English",
      "lang.thai": "ไทย",
      "lang.french": "Français",
      "lang.german": "Deutsch",
      "lang.chinese": "中文",
      "lang.japanese": "日本語",

      // Date/Time
      "date.format": "{{date, dd/MM/yyyy}}",
      "date.relative.now": "เมื่อสักครู่",
      "date.relative.minutes": "{{count}} นาทีที่แล้ว",
      "date.relative.minutes_plural": "{{count}} นาทีที่แล้ว",
      "date.relative.hours": "{{count}} ชั่วโมงที่แล้ว",
      "date.relative.hours_plural": "{{count}} ชั่วโมงที่แล้ว",
      "date.relative.days": "{{count}} วันที่แล้ว",
      "date.relative.days_plural": "{{count}} วันที่แล้ว",

      // Search
      "search.title": "ค้นหาบทความ",
      "search.placeholder": "ค้นหาบทความ...",
      "search.results": "ผลลัพธ์ที่พบ",
      "search.result": "ผลลัพธ์ที่พบ",
      "search.noResults": "ไม่พบผลลัพธ์",
      "search.noResultsMessage": "ลองปรับคำค้นหาหรือเรียกดูข่าวทั้งหมด",
      "search.startSearching": "เริ่มค้นหา",
      "search.startSearchingMessage": "ป้อนคำสำคัญเพื่อค้นหาในข่าวข่าวสาร",
    }
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    lng: 'th', // Default language set to Thai
    fallbackLng: 'th',
    debug: import.meta.env.DEV,

    interpolation: {
      escapeValue: false, // React already escapes values
    },

    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    },

    react: {
      useSuspense: false,
    },
  });

export default i18n;
