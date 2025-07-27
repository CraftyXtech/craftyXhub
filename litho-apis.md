# Litho APIs Status

This document tracks the implementation and consumption status of all APIs in the CraftyXhub project.

## Overview

- **Total Implemented APIs**: 45 (across all backend routers)
- **Consumed in Litho**: 17
- **Consumed in Admin**: 12
- **Consumed in Either Frontend**: 15
- **Not Consumed Anywhere**: 30

## API Status Legend

- ✅ **Consumed**: API is called/used in the frontend
- ❌ **Not Consumed**: API is implemented in backend but not used in frontend
- 🔄 **Required**: API should be consumed for core functionality
- ⚠️ **Optional**: API is nice-to-have but not essential
- 🚫 **Admin Only**: API is meant for admin use only

---

## Authentication APIs (`/auth`)

| Endpoint | Method | Litho | Admin | Required | Notes |
|----------|--------|-------|-------|----------|-------|
| `/register` | POST | ✅ | ❌ | 🔄 | User registration |
| `/login` | POST | ✅ | ❌ | 🔄 | User login |
| `/me` | GET | ✅ | ❌ | 🔄 | Get current user info |
| `/user/{user_uuid}` | GET | ❌ | ❌ | ⚠️ | Get specific user info |
| `/user/{user_uuid}` | PUT | ❌ | ❌ | ⚠️ | Update user profile |
| `/logout` | POST | ✅ | ❌ | 🔄 | User logout |
| `/reset-password` | PUT | ❌ | ❌ | ⚠️ | Password reset |

---

## User Management APIs (`/users`)

| Endpoint | Method | Litho | Admin | Required | Notes |
|----------|--------|-------|-------|----------|-------|
| `/{user_uuid}/follow` | POST | ❌ | ❌ | 🔄 | Follow user |
| `/{user_uuid}/follow` | POST | ❌ | ❌ | 🔄 | Unfollow user (duplicate path - bug) |
| `/{user_uuid}/followers` | GET | ❌ | ❌ | ⚠️ | Get user followers |
| `/{user_uuid}/following` | GET | ❌ | ❌ | ⚠️ | Get users being followed |

---

## Posts APIs (`/posts`)

### Content Discovery
| Endpoint | Method | Litho | Admin | Required | Notes |
|----------|--------|-------|-------|----------|-------|
| `/trending/` | GET | ❌ | ❌ | 🔄 | Trending posts for homepage |
| `/featured` | GET | ❌ | ❌ | 🔄 | Featured posts |
| `/recent` | GET | ❌ | ❌ | 🔄 | Recently published posts |
| `/popular` | GET | ❌ | ❌ | 🔄 | Most popular posts |
| `/{post_uuid}/related` | GET | ❌ | ❌ | ⚠️ | Related posts |
| `/` | GET | ✅ | ✅ | 🔄 | Get all posts (with filters) |
| `/{post_uuid}` | GET | ✅ | ✅ | 🔄 | Get single post |

### Content Management
| Endpoint | Method | Litho | Admin | Required | Notes |
|----------|--------|-------|-------|----------|-------|
| `/drafts` | GET | ❌ | ✅ | 🚫 | Get user's draft posts (admin) |
| `/` | POST | ❌ | ✅ | 🔄 | Create new post |
| `/{post_uuid}` | PUT | ❌ | ✅ | 🔄 | Update post |
| `/{post_uuid}` | DELETE | ❌ | ✅ | 🚫 | Delete post (admin) |
| `/{post_uuid}/publish` | PUT | ❌ | ✅ | 🚫 | Publish draft (admin) |
| `/{post_uuid}/unpublish` | PUT | ❌ | ✅ | 🚫 | Unpublish post (admin) |
| `/{post_uuid}/feature` | PUT | ❌ | ✅ | 🚫 | Feature post (admin) |

### Engagement & Moderation
| Endpoint | Method | Litho | Admin | Required | Notes |
|----------|--------|-------|-------|----------|-------|
| `/{post_uuid}/like` | POST | ✅ | ❌ | 🔄 | Toggle post like |
| `/{post_uuid}/bookmark` | POST | ❌ | ❌ | 🔄 | Bookmark post |
| `/users/me/bookmarks` | GET | ❌ | ❌ | 🔄 | Get user's bookmarks |
| `/{post_uuid}/report` | POST | ❌ | ❌ | ⚠️ | Report post |
| `/reports` | GET | ❌ | ✅ | 🚫 | Get reports (admin) |

### Categories & Tags
| Endpoint | Method | Litho | Admin | Required | Notes |
|----------|--------|-------|-------|----------|-------|
| `/categories/` | GET | ✅ | ✅ | 🔄 | Get all categories |
| `/categories/` | POST | ❌ | ✅ | 🚫 | Create category (admin) |
| `/tags/` | GET | ✅ | ✅ | 🔄 | Get all tags |
| `/tags/` | POST | ❌ | ✅ | 🚫 | Create tag (admin) |

### Analytics & Media
| Endpoint | Method | Litho | Admin | Required | Notes |
|----------|--------|-------|-------|----------|-------|
| `/stats/` | GET | ✅ | ✅ | 🔄 | Post statistics |
| `/images/{filename}` | GET | ✅ | ❌ | 🔄 | Get post images |

---

## Comments APIs (`/comments`)

| Endpoint | Method | Litho | Admin | Required | Notes |
|----------|--------|-------|-------|----------|-------|
| `/{post_uuid}/comments` | GET | ❌ | ❌ | 🔄 | Get post comments |
| `/{post_uuid}/comments` | POST | ❌ | ❌ | 🔄 | Create comment |
| `/{comment_uuid}` | PUT | ❌ | ❌ | ⚠️ | Update comment |
| `/{comment_uuid}/approve` | PUT | ❌ | ❌ | 🚫 | Approve comment (admin) |
| `/{comment_uuid}` | DELETE | ❌ | ❌ | ⚠️ | Delete comment |

---

## Profile APIs (`/profiles`)

| Endpoint | Method | Litho | Admin | Required | Notes |
|----------|--------|-------|-------|----------|-------|
| `/` | POST | ✅ | ❌ | 🔄 | Create profile |
| `/{user_uuid}` | GET | ✅ | ❌ | 🔄 | Get profile |
| `/{user_uuid}` | PUT | ✅ | ❌ | 🔄 | Update profile |
| `/{user_uuid}` | DELETE | ✅ | ❌ | ⚠️ | Delete profile |

---

## Priority Implementation Plan

### High Priority (Core Functionality)
1. **Content Discovery APIs** - Essential for homepage and browsing
   - GET `/posts/trending/`
   - GET `/posts/featured`
   - GET `/posts/recent`
   - GET `/posts/popular`

2. **Content Creation APIs** - For user-generated content
   - POST `/posts/` (create post)
   - PUT `/posts/{post_uuid}` (edit post)

3. **Engagement APIs** - For user interaction
   - POST `/posts/{post_uuid}/bookmark`
   - GET `/posts/users/me/bookmarks`

4. **Comments System** - For post discussions
   - GET `/comments/{post_uuid}/comments`
   - POST `/comments/{post_uuid}/comments`

### Medium Priority (Enhanced Features)
1. **User Social Features**
   - POST `/users/{user_uuid}/follow`
   - GET `/users/{user_uuid}/followers`
   - GET `/users/{user_uuid}/following`

2. **Content Discovery Enhancement**
   - GET `/posts/{post_uuid}/related`

### Low Priority (Optional Features)
1. **Content Moderation**
   - POST `/posts/{post_uuid}/report`
   - PUT `/comments/{comment_uuid}/approve`

2. **User Management**
   - PUT `/auth/reset-password`
   - GET `/auth/user/{user_uuid}`

---

## Implementation Notes

### Frontend Hooks Needed
- `useTrendingPosts()` - for trending posts
- `useFeaturedPosts()` - for featured posts
- `useRecentPosts()` - for recent posts
- `usePopularPosts()` - for popular posts
- `useCreatePost()` - for post creation
- `useUpdatePost()` - for post editing
- `useBookmarkPost()` - for bookmarking
- `useUserBookmarks()` - for saved posts
- `useComments()` - for comment system
- `useFollowUser()` - for following users

### Backend Issues to Fix
1. **Duplicate Route**: User follow/unfollow both use POST `/{user_uuid}/follow`
   - Should be: POST for follow, DELETE for unfollow

### Security Considerations
- Admin-only endpoints should not be exposed to public frontend
- Authentication required for user-specific operations
- Proper authorization checks for post editing/deletion

---

## Last Updated
- **Date**: January 2025
- **Backend Version**: Current implementation
- **Frontend Status**: Litho and Admin consumption tracked 