/**
 * Dashboard Menu Configuration
 * Role-based navigation for Author, Editor, and Admin
 */

// Icons from @tabler/icons-react
export const menuItems = [
  {
    id: 'dashboard',
    title: 'Dashboard',
    icon: 'IconLayoutGrid',
    url: '/dashboard',
    roles: ['user', 'moderator', 'admin'],
    breadcrumbs: false
  },
  {
    id: 'posts',
    title: 'My Posts',
    icon: 'IconFileText',
    roles: ['user', 'moderator', 'admin'],
    children: [
      { 
        id: 'posts-list', 
        title: 'All Posts', 
        url: '/dashboard/posts' 
      },
      { 
        id: 'posts-create', 
        title: 'Create New', 
        url: '/dashboard/posts/create' 
      },
      { 
        id: 'posts-drafts', 
        title: 'Drafts', 
        url: '/dashboard/drafts' 
      }
    ]
  },
  {
    id: 'media',
    title: 'Media Library',
    icon: 'IconPhoto',
    url: '/dashboard/media',
    roles: ['user', 'moderator', 'admin']
  },
  {
    id: 'ai-writer',
    title: 'AI Writer',
    icon: 'IconSparkles',
    url: '/dashboard/ai-writer',
    roles: ['moderator', 'admin'] // Authors don't have access
  },
  {
    id: 'moderation',
    title: 'Moderation',
    icon: 'IconShieldCheck',
    roles: ['moderator', 'admin'],
    children: [
      { 
        id: 'mod-comments', 
        title: 'Comments', 
        url: '/dashboard/moderation/comments' 
      },
      { 
        id: 'mod-reports', 
        title: 'Reports', 
        url: '/dashboard/moderation/reports' 
      }
    ]
  },
  {
    id: 'admin',
    title: 'Administration',
    icon: 'IconSettings',
    roles: ['admin'],
    children: [
      { 
        id: 'admin-users', 
        title: 'Users', 
        url: '/dashboard/users' 
      },
      { 
        id: 'admin-analytics', 
        title: 'Analytics', 
        url: '/dashboard/analytics' 
      },
      { 
        id: 'admin-categories', 
        title: 'Categories', 
        url: '/dashboard/categories' 
      },
      { 
        id: 'admin-tags', 
        title: 'Tags', 
        url: '/dashboard/tags' 
      },
      { 
        id: 'admin-settings', 
        title: 'Settings', 
        url: '/dashboard/settings' 
      }
    ]
  }
];

export default menuItems;
