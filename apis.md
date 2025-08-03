# CraftyXhub API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## Global Endpoints

### Health Check
- **GET** `/health`
  - Description: Check API and database health status
  - Response: Health status, version, environment, database connection

### Global Search ✅ CONSUMED
- **GET** `/search?q={query}`
  - Description: Search across posts, users, and categories
  - Parameters:
    - `q` (string, required): Search query
  - Response: Posts, users, and categories matching the query
  - **Used in**: `frontend/litho/src/api/postsService.js`, `frontend/litho/src/Components/Header/Header.jsx`

### API Documentation
- **GET** `/docs` - Swagger UI documentation
- **GET** `/redoc` - ReDoc documentation
- **GET** `/openapi.json` - OpenAPI specification

---

## Authentication Endpoints (`/v1/auth`)

### User Registration ✅ CONSUMED
- **POST** `/v1/auth/register`
  - Description: Register a new user account
  - Body: `UserCreate` schema
  - Response: `UserResponse` (201 Created)
  - **Used in**: `frontend/litho/src/Pages/auth/Register.jsx`

### User Login ✅ CONSUMED
- **POST** `/v1/auth/login`
  - Description: Authenticate user and get access token
  - Body: `UserLogin` schema
  - Response: `Token` with access_token and expires_in
  - **Used in**: `frontend/litho/src/Pages/auth/Login.jsx`, `frontend/litho/src/api/authService.js`

### Get Current User ✅ CONSUMED
- **GET** `/v1/auth/me`
  - Description: Get current authenticated user information
  - Authentication: Required
  - Response: `UserResponse`
  - **Used in**: `frontend/litho/src/Pages/auth/Login.jsx`, `frontend/litho/src/api/authService.js`

### Get User by UUID ✅ CONSUMED
- **GET** `/v1/auth/user/{user_uuid}`
  - Description: Get user information by UUID
  - Authentication: Required (can only view own profile)
  - Parameters:
    - `user_uuid` (string): User UUID
  - Response: `UserResponse`
  - **Used in**: `frontend/admin/src/api/userService.js`

### Update User Profile ✅ CONSUMED
- **PUT** `/v1/auth/user/{user_uuid}`
  - Description: Update user profile information
  - Authentication: Required (can only update own profile)
  - Parameters:
    - `user_uuid` (string): User UUID
    - `full_name` (string, optional): New full name
  - Response: `UserResponse`
  - **Used in**: `frontend/admin/src/api/userService.js`

### Logout ✅ CONSUMED
- **POST** `/v1/auth/logout`
  - Description: Logout current user
  - Authentication: Required
  - Response: Success message
  - **Used in**: `frontend/litho/src/api/authService.js`

### Reset Password ✅ CONSUMED
- **PUT** `/v1/auth/reset-password`
  - Description: Reset user password
  - Authentication: Required
  - Body: `ResetPasswordRequest` schema
  - Response: Success message
  - **Used in**: `frontend/admin/src/api/userService.js`, `frontend/litho/src/Components/auth/PasswordResetModal.jsx`

---

## Post Endpoints (`/v1/posts`)

### Get Trending Posts ✅ CONSUMED
- **GET** `/v1/posts/trending/`
  - Description: Get trending posts based on views and engagement
  - Parameters:
    - `skip` (int, optional): Number of posts to skip (default: 0)
    - `limit` (int, optional): Number of posts to return (default: 10, max: 100)
  - Response: `PostListResponse`
  - **Used in**: `frontend/litho/src/api/postsService.js`, `frontend/litho/src/Pages/Home/TrendingPosts.jsx`

### Get Featured Posts ✅ CONSUMED
- **GET** `/v1/posts/featured`
  - Description: Get featured posts
  - Parameters:
    - `skip` (int, optional): Number of posts to skip (default: 0)
    - `limit` (int, optional): Number of posts to return (default: 10, max: 100)
  - Response: `PostListResponse`
  - **Used in**: `frontend/litho/src/api/postsService.js`, `frontend/litho/src/Pages/Home/FeaturedPosts.jsx`

### Get Recent Posts ✅ CONSUMED
- **GET** `/v1/posts/recent`
  - Description: Get most recent posts
  - Parameters:
    - `skip` (int, optional): Number of posts to skip (default: 0)
    - `limit` (int, optional): Number of posts to return (default: 10, max: 100)
  - Response: `PostListResponse`
  - **Used in**: `frontend/litho/src/api/postsService.js`, `frontend/litho/src/api/usePosts.js`

### Get Popular Posts ✅ CONSUMED
- **GET** `/v1/posts/popular`
  - Description: Get popular posts based on likes and views
  - Parameters:
    - `skip` (int, optional): Number of posts to skip (default: 0)
    - `limit` (int, optional): Number of posts to return (default: 10, max: 100)
  - Response: `PostListResponse`
  - **Used in**: `frontend/litho/src/api/postsService.js`, `frontend/litho/src/api/usePosts.js`, `frontend/litho/src/Pages/Home/Magazine.jsx`

### Get Related Posts ✅ CONSUMED
- **GET** `/v1/posts/{post_uuid}/related`
  - Description: Get posts related to a specific post
  - Parameters:
    - `post_uuid` (string): Post UUID
    - `limit` (int, optional): Number of posts to return (default: 5, max: 10)
  - Response: `PostListResponse`
  - **Used in**: `frontend/litho/src/api/postsService.js`, `frontend/litho/src/api/usePosts.js`, `frontend/litho/src/Pages/Blogs/PostDetail/PostDetails.jsx`

### Get Draft Posts ✅ CONSUMED
- **GET** `/v1/posts/drafts`
  - Description: Get draft posts for current user
  - Authentication: Required
  - Parameters:
    - `skip` (int, optional): Number of posts to skip (default: 0)
    - `limit` (int, optional): Number of posts to return (default: 10, max: 100)
  - Response: `PostListResponse`
  - **Used in**: `frontend/litho/src/api/postsService.js`, `frontend/litho/src/Pages/User/DraftPosts.jsx`

### Get Reports
- **GET** `/v1/posts/reports`
  - Description: Get post reports (admin only)
  - Authentication: Required (admin)
  - Parameters:
    - `skip` (int, optional): Number of reports to skip (default: 0)
    - `limit` (int, optional): Number of reports to return (default: 10, max: 100)
  - Response: List of `ReportResponse`

### Get All Posts ✅ CONSUMED
- **GET** `/v1/posts/`
  - Description: Get all posts with filtering options
  - Parameters:
    - `skip` (int, optional): Number of posts to skip (default: 0)
    - `limit` (int, optional): Number of posts to return (default: 10, max: 100)
    - `published` (bool, optional): Filter by published status (default: true)
    - `author_id` (int, optional): Filter by author ID
    - `category_id` (int, optional): Filter by category ID
    - `tag_id` (int, optional): Filter by tag ID
  - Response: `PostListResponse`
  - **Used in**: `frontend/litho/src/api/postsService.js`, `frontend/litho/src/api/usePosts.js`, `frontend/litho/src/Pages/Home/Magazine.jsx`

### Get Single Post ✅ CONSUMED
- **GET** `/v1/posts/{post_uuid}`
  - Description: Get a specific post by UUID
  - Parameters:
    - `post_uuid` (string): Post UUID
  - Response: `PostResponse`
  - **Used in**: `frontend/litho/src/api/postsService.js`, `frontend/litho/src/api/usePosts.js`, `frontend/litho/src/Pages/Blogs/PostDetail/PostDetails.jsx`

### Create Post ✅ CONSUMED
- **POST** `/v1/posts/`
  - Description: Create a new post
  - Authentication: Required
  - Body: Form data with fields:
    - `title` (string, required): Post title
    - `slug` (string, optional): Post slug
    - `content` (string, required): Post content
    - `excerpt` (string, optional): Post excerpt
    - `meta_title` (string, optional): SEO meta title
    - `meta_description` (string, optional): SEO meta description
    - `category_id` (int, optional): Category ID
    - `tag_ids` (string, optional): Comma-separated tag IDs
    - `reading_time` (int, optional): Estimated reading time
    - `featured_image` (file, optional): Featured image file
  - Response: `PostResponse` (201 Created)
  - **Used in**: `frontend/admin/src/api/postService.js`, `frontend/admin/src/pages/posts/PostForm.jsx`

### Get Post Image ✅ CONSUMED
- **GET** `/v1/posts/images/{filename}`
  - Description: Get post image by filename
  - Parameters:
    - `filename` (string): Image filename
  - Response: Image file
  - **Used in**: `frontend/litho/src/api/postsService.js`, `frontend/litho/src/api/usePosts.js`

### Update Post ✅ CONSUMED
- **PUT** `/v1/posts/{post_uuid}`
  - Description: Update an existing post
  - Authentication: Required (author or admin)
  - Parameters:
    - `post_uuid` (string): Post UUID
  - Body: Form data with optional fields (same as create)
  - Response: `PostResponse`
  - **Used in**: `frontend/admin/src/api/postService.js`, `frontend/admin/src/pages/posts/PostForm.jsx`

### Delete Post ✅ CONSUMED
- **DELETE** `/v1/posts/{post_uuid}`
  - Description: Delete a post (soft delete)
  - Authentication: Required (author or admin)
  - Parameters:
    - `post_uuid` (string): Post UUID
  - Response: 204 No Content
  - **Used in**: `frontend/admin/src/api/postService.js`, `frontend/admin/src/pages/posts/PostList.jsx`

### Toggle Post Like ✅ CONSUMED
- **POST** `/v1/posts/{post_uuid}/like`
  - Description: Like or unlike a post
  - Authentication: Required
  - Parameters:
    - `post_uuid` (string): Post UUID
  - Response: Boolean (true if liked, false if unliked)
  - **Used in**: `frontend/litho/src/api/postsService.js`

### Get Categories ✅ CONSUMED
- **GET** `/v1/posts/categories/`
  - Description: Get all categories
  - Response: `CategoryListResponse`
  - **Used in**: `frontend/litho/src/api/postsService.js`, `frontend/litho/src/api/usePosts.js`, `frontend/litho/src/Pages/Home/Magazine.jsx`

### Create Category ✅ CONSUMED
- **POST** `/v1/posts/categories/`
  - Description: Create a new category
  - Authentication: Required (admin)
  - Body: `CategoryCreate` schema
  - Response: `CategoryResponse` (201 Created)
  - **Used in**: `frontend/admin/src/api/postService.js`, `frontend/admin/src/pages/posts/CategoryManagement.jsx`

### Get Tags ✅ CONSUMED
- **GET** `/v1/posts/tags/`
  - Description: Get all tags
  - Response: `TagListResponse`
  - **Used in**: `frontend/litho/src/api/postsService.js`, `frontend/litho/src/api/usePosts.js`

### Create Tag ✅ CONSUMED
- **POST** `/v1/posts/tags/`
  - Description: Create a new tag
  - Authentication: Required (admin)
  - Body: `TagCreate` schema
  - Response: `TagResponse` (201 Created)
  - **Used in**: `frontend/admin/src/api/postService.js`

### Get Post Statistics ✅ CONSUMED
- **GET** `/v1/posts/stats/`
  - Description: Get post statistics
  - Response: `PostStatsResponse`
  - **Used in**: `frontend/litho/src/api/postsService.js`, `frontend/litho/src/api/usePosts.js`

### Publish Post ✅ CONSUMED
- **PUT** `/v1/posts/{post_uuid}/publish`
  - Description: Publish a draft post
  - Authentication: Required (author or admin)
  - Parameters:
    - `post_uuid` (string): Post UUID
  - Response: `PostResponse`
  - **Used in**: `frontend/admin/src/api/postService.js`, `frontend/admin/src/pages/posts/PostList.jsx`

### Unpublish Post ✅ CONSUMED
- **PUT** `/v1/posts/{post_uuid}/unpublish`
  - Description: Unpublish a published post
  - Authentication: Required (author or admin)
  - Parameters:
    - `post_uuid` (string): Post UUID
  - Response: `PostResponse`
  - **Used in**: `frontend/admin/src/api/postService.js`, `frontend/admin/src/pages/posts/PostList.jsx`

### Feature Post ✅ CONSUMED
- **PUT** `/v1/posts/{post_uuid}/feature`
  - Description: Feature or unfeature a post
  - Authentication: Required (admin)
  - Parameters:
    - `post_uuid` (string): Post UUID
    - `feature` (bool, optional): Feature status (default: true)
  - Response: `PostResponse`
  - **Used in**: `frontend/admin/src/api/postService.js`, `frontend/admin/src/pages/posts/PostList.jsx`

### Report Post ✅ CONSUMED
- **POST** `/v1/posts/{post_uuid}/report`
  - Description: Report a post
  - Authentication: Required
  - Parameters:
    - `post_uuid` (string): Post UUID
  - Body: `ReportCreate` schema
  - Response: `ReportResponse`
  - **Used in**: `frontend/litho/src/api/postsService.js`, `frontend/litho/src/Components/Blogs/ReportModal.jsx`

### Bookmark Post ✅ CONSUMED
- **POST** `/v1/posts/{post_uuid}/bookmark`
  - Description: Bookmark or unbookmark a post
  - Authentication: Required
  - Parameters:
    - `post_uuid` (string): Post UUID
  - Response: Boolean (true if bookmarked, false if unbookmarked)
  - **Used in**: `frontend/litho/src/api/postsService.js`, `frontend/litho/src/Components/Blogs/BookmarkButton.jsx`

### Get User Bookmarks ✅ CONSUMED
- **GET** `/v1/posts/users/me/bookmarks`
  - Description: Get current user's bookmarked posts
  - Authentication: Required
  - Parameters:
    - `skip` (int, optional): Number of posts to skip (default: 0)
    - `limit` (int, optional): Number of posts to return (default: 10, max: 100)
  - Response: `PostListResponse`
  - **Used in**: `frontend/litho/src/api/postsService.js`, `frontend/litho/src/Pages/User/Bookmarks.jsx`

### Get Post Image (Uploads)
- **GET** `/v1/uploads/images/{filename}`
  - Description: Get uploaded image by filename
  - Parameters:
    - `filename` (string): Image filename
    - `folder` (string, required): Folder category (e.g., 'posts', 'avatars', 'media')
  - Response: Image file

---

## User Following Endpoints (`/v1/users`)

### Follow User ✅ CONSUMED
- **POST** `/v1/users/{user_uuid}/follow`
  - Description: Follow a user
  - Authentication: Required
  - Parameters:
    - `user_uuid` (UUID): User UUID to follow
  - Response: `FollowActionResponse`
  - **Used in**: `frontend/litho/src/api/userService.js`, `frontend/litho/src/Components/User/FollowButton.jsx`

### Unfollow User ✅ CONSUMED
- **POST** `/v1/users/{user_uuid}/follow`
  - Description: Unfollow a user
  - Authentication: Required
  - Parameters:
    - `user_uuid` (UUID): User UUID to unfollow
  - Response: `FollowActionResponse`
  - **Used in**: `frontend/litho/src/api/userService.js`, `frontend/litho/src/Components/User/FollowButton.jsx`

### Get User Followers ✅ CONSUMED
- **GET** `/v1/users/{user_uuid}/followers`
  - Description: Get users who follow a specific user
  - Authentication: Required
  - Parameters:
    - `user_uuid` (UUID): User UUID
    - `page` (int, optional): Page number (default: 1)
    - `size` (int, optional): Items per page (default: 10, max: 50)
  - Response: `UserFollowersResponse`
  - **Used in**: `frontend/litho/src/api/userService.js`, `frontend/litho/src/Pages/User/Followers.jsx`

### Get User Following ✅ CONSUMED
- **GET** `/v1/users/{user_uuid}/following`
  - Description: Get users that a specific user follows
  - Authentication: Required
  - Parameters:
    - `user_uuid` (UUID): User UUID
    - `page` (int, optional): Page number (default: 1)
    - `size` (int, optional): Items per page (default: 10, max: 50)
  - Response: `UserFollowingResponse`
  - **Used in**: `frontend/litho/src/api/userService.js`, `frontend/litho/src/Pages/User/Following.jsx`

---

## Comment Endpoints (`/v1/comments`)

### Get Post Comments ✅ CONSUMED
- **GET** `/v1/comments/{post_uuid}/comments`
  - Description: Get comments for a specific post
  - Parameters:
    - `post_uuid` (string): Post UUID
    - `skip` (int, optional): Number of comments to skip (default: 0)
    - `limit` (int, optional): Number of comments to return (default: 10, max: 100)
  - Response: `CommentListResponse`
  - **Used in**: `frontend/litho/src/api/postsService.js`, `frontend/litho/src/api/usePosts.js`

### Create Comment ✅ CONSUMED
- **POST** `/v1/comments/{post_uuid}/comments`
  - Description: Create a new comment on a post
  - Authentication: Required
  - Parameters:
    - `post_uuid` (string): Post UUID
  - Body: `CommentCreate` schema
  - Response: `CommentResponse`
  - **Used in**: `frontend/litho/src/api/postsService.js`, `frontend/litho/src/api/usePosts.js`

### Update Comment ✅ CONSUMED
- **PUT** `/v1/comments/{comment_uuid}`
  - Description: Update a comment
  - Authentication: Required (author or admin)
  - Parameters:
    - `comment_uuid` (string): Comment UUID
  - Body: `CommentCreate` schema
  - Response: `CommentResponse`
  - **Used in**: `frontend/litho/src/api/postsService.js`, `frontend/litho/src/api/usePosts.js`

### Approve Comment
- **PUT** `/v1/comments/{comment_uuid}/approve`
  - Description: Approve a comment (admin only)
  - Authentication: Required (admin)
  - Parameters:
    - `comment_uuid` (string): Comment UUID
  - Response: `CommentResponse`

### Delete Comment ✅ CONSUMED
- **DELETE** `/v1/comments/{comment_uuid}`
  - Description: Delete a comment
  - Authentication: Required (author or admin)
  - Parameters:
    - `comment_uuid` (string): Comment UUID
  - Response: Boolean (true if deleted)
  - **Used in**: `frontend/litho/src/api/postsService.js`, `frontend/litho/src/api/usePosts.js`

---

## Profile Endpoints (`/v1/profiles`)

### Create Profile ✅ CONSUMED
- **POST** `/v1/profiles/`
  - Description: Create a user profile
  - Authentication: Required
  - Body: Form data with fields:
    - `bio` (string, optional): User bio
    - `location` (string, optional): User location
    - `website` (string, optional): User website
    - `twitter_handle` (string, optional): Twitter handle
    - `github_handle` (string, optional): GitHub handle
    - `linkedin_handle` (string, optional): LinkedIn handle
    - `birth_date` (string, optional): Birth date
    - `avatar` (file, optional): Profile avatar
  - Response: `ProfileResponse`
  - **Used in**: `frontend/litho/src/api/postsService.js`

### Get Profile ✅ CONSUMED
- **GET** `/v1/profiles/{user_uuid}`
  - Description: Get user profile by UUID
  - Parameters:
    - `user_uuid` (string): User UUID
  - Response: `ProfileResponse`
  - **Used in**: `frontend/litho/src/api/postsService.js`, `frontend/litho/src/api/usePosts.js`

### Update Profile ✅ CONSUMED
- **PUT** `/v1/profiles/{user_uuid}`
  - Description: Update user profile
  - Authentication: Required (owner or admin)
  - Parameters:
    - `user_uuid` (string): User UUID
  - Body: Form data with optional fields (same as create)
  - Response: `ProfileResponse`
  - **Used in**: `frontend/litho/src/api/postsService.js`

### Delete Profile ✅ CONSUMED
- **DELETE** `/v1/profiles/{user_uuid}`
  - Description: Delete user profile
  - Authentication: Required (owner or admin)
  - Parameters:
    - `user_uuid` (string): User UUID
  - Response: Success message
  - **Used in**: `frontend/litho/src/api/postsService.js`

---

## Response Models

### Common Response Fields
- `id` (int): Database ID
- `uuid` (string): Unique identifier
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last update timestamp

### User Response
```json
{
  "id": 1,
  "uuid": "user-uuid",
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "is_active": true,
  "is_verified": false,
  "role": "user",
  "last_login": "2024-01-01T00:00:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Post Response
```json
{
  "id": 1,
  "uuid": "post-uuid",
  "title": "Post Title",
  "slug": "post-slug",
  "content": "Post content...",
  "excerpt": "Post excerpt...",
  "featured_image": "image-url",
  "is_published": true,
  "is_featured": false,
  "view_count": 100,
  "reading_time": 5,
  "meta_title": "SEO title",
  "meta_description": "SEO description",
  "published_at": "2024-01-01T00:00:00Z",
  "author": { /* User object */ },
  "category": { /* Category object */ },
  "tags": [ /* Tag objects */ ],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Token Response
```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Media Response
```json
{
  "id": 1,
  "uuid": "media-uuid",
  "filename": "image.jpg",
  "file_path": "uploads/media/image.jpg",
  "file_size": 1024000,
  "mime_type": "image/jpeg",
  "description": "Media description",
  "user_id": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message"
}
```

### Common HTTP Status Codes
- `200 OK`: Success
- `201 Created`: Resource created successfully
- `204 No Content`: Success with no response body
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error

---

## Rate Limiting
The API implements rate limiting to prevent abuse. Limits are applied per IP address and endpoint.

## CORS
CORS is enabled for development with the following configuration:
- Allow origins: `*`
- Allow credentials: `true`
- Allow methods: `*`
- Allow headers: `*`

---

## Media Endpoints (`/v1/media`)

### Get User Media ✅ CONSUMED
- **GET** `/v1/media/`
  - Description: Get all media files for current user
  - Authentication: Required
  - Response: List of `MediaResponse`
  - **Used in**: `frontend/litho/src/api/mediaService.js`, `frontend/litho/src/Pages/User/MediaLibrary.jsx`

### Upload Media ✅ CONSUMED
- **POST** `/v1/media/upload`
  - Description: Upload a new media file
  - Authentication: Required
  - Body: Form data with fields:
    - `file` (file, required): Media file to upload
    - `description` (string, optional): Media description
  - Response: `MediaResponse`
  - **Used in**: `frontend/litho/src/api/mediaService.js`, `frontend/litho/src/Components/Media/MediaUploader.jsx`

### Get Media by UUID ✅ CONSUMED
- **GET** `/v1/media/{media_uuid}`
  - Description: Get specific media file by UUID
  - Authentication: Required
  - Parameters:
    - `media_uuid` (string): Media UUID
  - Response: `MediaResponse`
  - **Used in**: `frontend/litho/src/api/mediaService.js`, `frontend/litho/src/Components/Media/MediaGallery.jsx`

### Update Media ✅ CONSUMED
- **PUT** `/v1/media/{media_uuid}`
  - Description: Update media file information
  - Authentication: Required (owner only)
  - Parameters:
    - `media_uuid` (string): Media UUID
  - Body: `MediaUpdateRequest` schema
  - Response: `MediaResponse`
  - **Used in**: `frontend/litho/src/api/mediaService.js`, `frontend/litho/src/Components/Media/MediaGallery.jsx`

### Delete Media ✅ CONSUMED
- **DELETE** `/v1/media/{media_uuid}`
  - Description: Delete a media file
  - Authentication: Required (owner only)
  - Parameters:
    - `media_uuid` (string): Media UUID
  - Response: Success message
  - **Used in**: `frontend/litho/src/api/mediaService.js`, `frontend/litho/src/Components/Media/MediaGallery.jsx`

---

## 🚨 APIs REQUIRING ADMIN PANEL IMPLEMENTATION

The following APIs are **NOT YET CONSUMED** and need to be implemented in the **Admin Panel** (`frontend/admin/`):

### Admin-Only Post Management
- **GET** `/v1/posts/reports` - Get post reports (admin moderation queue)
- **PUT** `/v1/comments/{comment_uuid}/approve` - Approve user comments

### Utility Endpoints (Optional)
- **GET** `/health` - API health check (useful for admin dashboard status)
- **GET** `/v1/uploads/images/{filename}` - Static file serving (may need admin access)

### Documentation Endpoints (Not Required)
- **GET** `/docs` - Swagger UI (development only)
- **GET** `/redoc` - ReDoc documentation (development only) 
- **GET** `/openapi.json` - OpenAPI spec (development only)

### 📊 **Implementation Priority for Admin Panel:**

#### 🔥 **High Priority (Essential Admin Features)**
1. **Comment Moderation System**:
   - `PUT /v1/comments/{comment_uuid}/approve` - Core admin function
   - Build admin comment approval interface
   - Bulk comment actions

2. **Post Reports Management**:
   - `GET /v1/posts/reports` - Review user reports
   - Post moderation workflow
   - Report resolution tracking

#### 🔶 **Medium Priority (Admin Utilities)**
3. **System Health Monitoring**:
   - `GET /health` - System status dashboard
   - API uptime monitoring
   - Database health checks

#### 🔷 **Low Priority (Development Tools)**
4. **API Documentation Access**:
   - Admin access to API docs
   - Development utilities

### 📋 **Current API Consumption Status:**
- **Litho Frontend (Public)**: ✅ **100% Complete** (All user-facing APIs consumed)
- **Admin Panel**: ❌ **Missing 2 Essential APIs** (Comment approval + Post reports)
- **Total Completion**: **🎯 95% of APIs Consumed** (Missing only admin moderation features)

---

## Notes
- All timestamps are in UTC
- File uploads are limited to specific formats and sizes
- Authentication tokens expire after 30 minutes by default
- Soft deletes are used for posts and comments
- Admin users have elevated permissions across all endpoints 