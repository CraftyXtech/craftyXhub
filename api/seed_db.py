import asyncio
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session, engine
from models.user import User, Profile, UserRole
from models.post import Post, Category, Tag
from models.base import Base
from services.user.auth import AuthService
from utils.slug_generator import generate_slug


async def create_users_and_profiles():
    """Create admin user and regular users with their profiles"""
    users_data = [
        {
            "email": "admin@craftyx.com",
            "username": "admin",
            "full_name": "CraftyX Admin", 
            "password": "admin123",
            "role": UserRole.ADMIN,
            "is_verified": True,
            "profile": {
                "bio": "Platform administrator and content curator for CraftyX Hub. Passionate about creating engaging content and fostering community growth.",
                "location": "San Francisco, CA",
                "website": "https://craftyx.com",
                "twitter_handle": "craftyx_admin",
                "github_handle": "craftyx-official"
            }
        },
        {
            "email": "john.doe@example.com", 
            "username": "johndoe",
            "full_name": "John Doe",
            "password": "password123",
            "role": UserRole.USER,
            "is_verified": True,
            "profile": {
                "bio": "Full-stack developer passionate about React, Node.js, and building scalable web applications. Always learning new technologies.",
                "location": "New York, NY",
                "website": "https://johndoe.dev",
                "twitter_handle": "johndoe_dev",
                "github_handle": "johndoe-dev",
                "linkedin_handle": "johndoe-developer"
            }
        },
        {
            "email": "jane.smith@example.com",
            "username": "janesmith", 
            "full_name": "Jane Smith",
            "password": "password123",
            "role": UserRole.USER,
            "is_verified": True,
            "profile": {
                "bio": "UI/UX designer and frontend developer. Love creating beautiful, user-friendly interfaces and writing about design trends.",
                "location": "Los Angeles, CA",
                "website": "https://janesmith.design",
                "twitter_handle": "janesmith_ux",
                "github_handle": "janesmith-design",
                "linkedin_handle": "jane-smith-designer"
            }
        }
    ]
    
    created_users = []
    
    async for session in get_db_session():
        for user_data in users_data:
            # Check if user already exists
            existing_user = await AuthService.get_user_by_email(session, user_data["email"])
            if existing_user:
                print(f"User {user_data['email']} already exists, skipping...")
                created_users.append(existing_user)
                continue
                
            # Create user
            hashed_password = AuthService.get_password_hash(user_data["password"])
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                full_name=user_data["full_name"],
                password=hashed_password,
                role=user_data["role"],
                is_verified=user_data["is_verified"],
                is_active=True
            )
            
            session.add(user)
            await session.flush()  # Get the user ID
            
            # Create profile
            profile = Profile(
                user_id=user.id,
                bio=user_data["profile"]["bio"],
                location=user_data["profile"]["location"],
                website=user_data["profile"]["website"],
                twitter_handle=user_data["profile"]["twitter_handle"],
                github_handle=user_data["profile"]["github_handle"],
                linkedin_handle=user_data["profile"].get("linkedin_handle")
            )
            
            session.add(profile)
            created_users.append(user)
            print(f"Created user: {user.full_name} ({user.role.value})")
            
        await session.commit()
    
    return created_users


async def create_categories():
    """Create blog categories"""
    categories_data = [
        {
            "name": "Web Development",
            "slug": "web-development", 
            "description": "Articles about frontend, backend, and full-stack web development"
        },
        {
            "name": "Design",
            "slug": "design",
            "description": "UI/UX design, graphic design, and design thinking articles"
        },
        {
            "name": "Technology",
            "slug": "technology",
            "description": "Latest technology trends, tools, and innovations"
        },
        {
            "name": "Tutorials",
            "slug": "tutorials",
            "description": "Step-by-step guides and how-to articles"
        },
        {
            "name": "Career",
            "slug": "career",
            "description": "Career advice, job hunting tips, and professional development"
        }
    ]
    
    created_categories = []
    
    async for session in get_db_session():
        for cat_data in categories_data:
            # Check if category exists
            from sqlalchemy import select
            stmt = select(Category).where(Category.slug == cat_data["slug"])
            result = await session.execute(stmt)
            existing_category = result.scalar_one_or_none()
            
            if existing_category:
                print(f"Category {cat_data['name']} already exists, skipping...")
                created_categories.append(existing_category)
                continue
                
            category = Category(
                name=cat_data["name"],
                slug=cat_data["slug"],
                description=cat_data["description"]
            )
            
            session.add(category)
            created_categories.append(category)
            print(f"Created category: {category.name}")
            
        await session.commit()
    
    return created_categories


async def create_tags():
    """Create blog tags"""
    tags_data = [
        {"name": "React", "slug": "react"},
        {"name": "JavaScript", "slug": "javascript"},
        {"name": "Python", "slug": "python"},
        {"name": "FastAPI", "slug": "fastapi"},
        {"name": "CSS", "slug": "css"},
        {"name": "HTML", "slug": "html"},
        {"name": "Node.js", "slug": "nodejs"},
        {"name": "PostgreSQL", "slug": "postgresql"},
        {"name": "API", "slug": "api"},
        {"name": "Frontend", "slug": "frontend"},
        {"name": "Backend", "slug": "backend"},
        {"name": "Tutorial", "slug": "tutorial"},
        {"name": "Beginner", "slug": "beginner"},
        {"name": "Advanced", "slug": "advanced"},
        {"name": "UI/UX", "slug": "ui-ux"}
    ]
    
    created_tags = []
    new_tags_count = 0
    
    async for session in get_db_session():
        for tag_data in tags_data:
            # Check if tag exists
            from sqlalchemy import select
            stmt = select(Tag).where(Tag.slug == tag_data["slug"])
            result = await session.execute(stmt)
            existing_tag = result.scalar_one_or_none()
            
            if existing_tag:
                await session.refresh(existing_tag)  # Ensure it's fully loaded
                created_tags.append(existing_tag)
                continue
                
            tag = Tag(
                name=tag_data["name"],
                slug=tag_data["slug"]
            )
            
            session.add(tag)
            await session.flush()
            await session.refresh(tag)  # Get ID and ensure loaded
            created_tags.append(tag)
            new_tags_count += 1
            
        await session.commit()
        print(f"Created {new_tags_count} tags")
    
    return created_tags


async def create_posts(users, categories, tags):
    """Create sample blog posts"""
    posts_data = [
        {
            "title": "Getting Started with FastAPI and React",
            "content": """# Getting Started with FastAPI and React

FastAPI is a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints. Combined with React for the frontend, it creates a powerful full-stack development experience.

## Why FastAPI?

FastAPI offers several advantages:
- **Fast performance**: One of the fastest Python frameworks available
- **Easy to use**: Intuitive design based on Python type hints
- **Automatic docs**: Interactive API documentation with Swagger UI
- **Modern Python**: Full support for async/await

## Setting Up FastAPI

First, install FastAPI and Uvicorn:

```bash
pip install fastapi uvicorn
```

Create a simple API:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}
```

## Building the React Frontend

Create a new React app:

```bash
npx create-react-app my-frontend
cd my-frontend
npm start
```

## Connecting Frontend and Backend

Use axios to make API calls from React to your FastAPI backend:

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

export default api;
```

This combination provides a robust foundation for modern web applications with excellent developer experience and performance.
""",
            "excerpt": "Learn how to build a modern web application using FastAPI for the backend and React for the frontend. This comprehensive guide covers setup, development, and deployment.",
            "author_index": 0,  # admin
            "category_index": 0,  # Web Development
            "tag_indices": [0, 1, 3, 9, 10],  # React, JavaScript, FastAPI, Frontend, Backend
            "is_published": True,
            "is_featured": True,
            "reading_time": 8
        },
        {
            "title": "Modern UI Design Principles for Web Applications",
            "content": """# Modern UI Design Principles for Web Applications

Creating intuitive and beautiful user interfaces is crucial for successful web applications. Here are the key principles every developer and designer should know.

## 1. Simplicity and Clarity

Keep your interface clean and focused. Every element should have a purpose:
- Remove unnecessary elements
- Use whitespace effectively
- Prioritize content hierarchy

## 2. Consistency

Maintain consistency throughout your application:
- Use a consistent color palette
- Apply typography rules uniformly
- Keep interaction patterns predictable

## 3. Responsive Design

Your application should work seamlessly across all devices:
- Mobile-first approach
- Flexible grid systems
- Scalable images and media

## 4. Accessibility

Design for everyone:
- Use semantic HTML
- Ensure proper color contrast
- Implement keyboard navigation
- Add alt text for images

## 5. Performance

Fast loading times are essential:
- Optimize images
- Minimize HTTP requests
- Use efficient CSS and JavaScript

## Color Theory in UI Design

Understanding color psychology helps create better user experiences:
- **Blue**: Trust, reliability (used by Facebook, Twitter)
- **Green**: Growth, success (used by Spotify, WhatsApp)
- **Red**: Urgency, attention (used for error states)

## Typography Best Practices

Choose fonts that enhance readability:
- Use a maximum of 2-3 font families
- Ensure proper line spacing
- Consider font weight hierarchy

Remember, great design is invisible - users should be able to accomplish their goals without thinking about the interface.
""",
            "excerpt": "Discover the fundamental principles of modern UI design that will help you create more intuitive and visually appealing web applications.",
            "author_index": 2,  # Jane Smith
            "category_index": 1,  # Design
            "tag_indices": [4, 5, 9, 14],  # CSS, HTML, Frontend, UI/UX
            "is_published": True,
            "is_featured": True,
            "reading_time": 6
        },
        {
            "title": "Building RESTful APIs with Python and FastAPI",
            "content": """# Building RESTful APIs with Python and FastAPI

REST (Representational State Transfer) is an architectural style for designing networked applications. FastAPI makes building RESTful APIs in Python incredibly straightforward and enjoyable.

## What is REST?

REST is based on several key principles:
- **Stateless**: Each request contains all necessary information
- **Resource-based**: URLs represent resources, not actions
- **HTTP methods**: Use GET, POST, PUT, DELETE appropriately
- **JSON responses**: Structured data format

## Setting Up Your FastAPI Project

Start with a proper project structure:

```
my_api/
├── main.py
├── models/
├── routers/
├── schemas/
└── services/
```

## Creating Your First Endpoint

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    email: str

users = []

@app.get("/users", response_model=List[User])
async def get_users():
    return users

@app.post("/users", response_model=User)
async def create_user(user: User):
    users.append(user)
    return user

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    for user in users:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")
```

## Database Integration

Use SQLAlchemy with FastAPI for database operations:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

## API Documentation

FastAPI automatically generates interactive API documentation at `/docs` and `/redoc`. This makes testing and sharing your API effortless.

## Best Practices

1. **Use Pydantic models** for request/response validation
2. **Implement proper error handling** with meaningful HTTP status codes
3. **Add authentication and authorization** for secured endpoints
4. **Version your API** for backward compatibility
5. **Write tests** for all endpoints

Building APIs with FastAPI is not just about speed - it's about creating maintainable, well-documented, and reliable services that power modern applications.
""",
            "excerpt": "A comprehensive guide to building RESTful APIs using FastAPI. Learn best practices, database integration, and how to create maintainable API services.",
            "author_index": 1,  # John Doe
            "category_index": 0,  # Web Development
            "tag_indices": [2, 3, 8, 10, 11],  # Python, FastAPI, API, Backend, Tutorial
            "is_published": True,
            "is_featured": False,
            "reading_time": 10
        },
        {
            "title": "Career Tips for Junior Developers",
            "content": """# Career Tips for Junior Developers

Starting your career as a developer can be both exciting and overwhelming. Here are practical tips to help you navigate your early career successfully.

## 1. Focus on Fundamentals

Before diving into the latest frameworks, master the basics:
- **Programming fundamentals**: Variables, functions, loops, conditionals
- **Data structures**: Arrays, objects, lists, dictionaries
- **Problem-solving**: Break complex problems into smaller parts
- **Version control**: Learn Git thoroughly

## 2. Build a Strong Portfolio

Your portfolio is your calling card:
- Create 3-5 quality projects rather than 20 mediocre ones
- Include a variety of technologies
- Write clear README files
- Deploy your projects live
- Show the problem your project solves

## 3. Learn to Learn

Technology evolves rapidly. Develop these learning habits:
- Read documentation thoroughly
- Practice coding daily (even 30 minutes helps)
- Join developer communities
- Follow industry blogs and newsletters
- Attend meetups and conferences

## 4. Communication is Key

Technical skills alone aren't enough:
- Learn to explain complex concepts simply
- Ask questions when you're stuck
- Document your code clearly
- Practice presenting your work
- Collaborate effectively with teams

## 5. Don't Compare Yourself to Others

Everyone's journey is different:
- Focus on your own progress
- Celebrate small wins
- Learn from mistakes without harsh self-judgment
- Find mentors who inspire you
- Remember that senior developers were once beginners too

## 6. Networking and Community

Build meaningful professional relationships:
- Contribute to open source projects
- Answer questions on Stack Overflow
- Share your learning journey on social media
- Attend local tech meetups
- Find a mentor

## 7. Practical Job Search Tips

When you're ready to apply:
- Tailor your resume to each job
- Practice coding interviews regularly
- Prepare stories about your projects
- Research the company thoroughly
- Follow up professionally after interviews

## 8. Once You Land the Job

Make the most of your first role:
- Ask lots of questions (you're expected to)
- Volunteer for diverse projects
- Seek feedback regularly
- Document what you learn
- Be patient with yourself

Remember, becoming a great developer is a marathon, not a sprint. Focus on consistent growth, and you'll be amazed at how far you can go.
""",
            "excerpt": "Essential career advice for junior developers looking to build successful careers in tech. From fundamentals to job searching and beyond.",
            "author_index": 0,  # Admin
            "category_index": 4,  # Career
            "tag_indices": [11, 12],  # Tutorial, Beginner
            "is_published": True,
            "is_featured": False,
            "reading_time": 7
        },
        {
            "title": "Advanced JavaScript Patterns and Best Practices",
            "content": """# Advanced JavaScript Patterns and Best Practices

As you grow as a JavaScript developer, understanding advanced patterns and best practices becomes crucial for writing maintainable, performant code.

## 1. Module Patterns

### ES6 Modules
```javascript
// utils.js
export const formatDate = (date) => {
  return new Intl.DateTimeFormat('en-US').format(date);
};

export const debounce = (func, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(null, args), delay);
  };
};

// main.js
import { formatDate, debounce } from './utils.js';
```

### Revealing Module Pattern
```javascript
const UserModule = (() => {
  let users = [];
  
  const addUser = (user) => {
    users.push(user);
  };
  
  const getUsers = () => {
    return [...users]; // Return a copy
  };
  
  // Public API
  return {
    addUser,
    getUsers
  };
})();
```

## 2. Observer Pattern

Great for event-driven architectures:

```javascript
class EventEmitter {
  constructor() {
    this.events = {};
  }
  
  on(event, callback) {
    if (!this.events[event]) {
      this.events[event] = [];
    }
    this.events[event].push(callback);
  }
  
  emit(event, data) {
    if (this.events[event]) {
      this.events[event].forEach(callback => callback(data));
    }
  }
  
  off(event, callback) {
    if (this.events[event]) {
      this.events[event] = this.events[event].filter(cb => cb !== callback);
    }
  }
}
```

## 3. Async/Await Best Practices

### Error Handling
```javascript
const fetchUserData = async (userId) => {
  try {
    const response = await fetch(`/api/users/${userId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to fetch user data:', error);
    throw error; // Re-throw to let caller handle
  }
};
```

### Parallel Execution
```javascript
const fetchAllData = async () => {
  try {
    // Run requests in parallel
    const [users, posts, comments] = await Promise.all([
      fetchUsers(),
      fetchPosts(),
      fetchComments()
    ]);
    
    return { users, posts, comments };
  } catch (error) {
    console.error('Failed to fetch data:', error);
  }
};
```

## 4. Functional Programming Concepts

### Pure Functions
```javascript
// Pure function - no side effects
const calculateTotal = (items) => {
  return items.reduce((total, item) => total + item.price, 0);
};

// Impure function - modifies external state
let total = 0;
const addToTotal = (amount) => {
  total += amount; // Side effect!
  return total;
};
```

### Higher-Order Functions
```javascript
const withLogging = (fn) => {
  return (...args) => {
    console.log(`Calling ${fn.name} with args:`, args);
    const result = fn(...args);
    console.log(`Result:`, result);
    return result;
  };
};

const add = (a, b) => a + b;
const loggedAdd = withLogging(add);
```

## 5. Memory Management

### Avoiding Memory Leaks
```javascript
// Bad - creates memory leak
const createHandler = () => {
  const largeData = new Array(1000000).fill('data');
  
  return (event) => {
    // Handler keeps reference to largeData
    console.log(largeData.length);
  };
};

// Good - clean up references
const createHandler = () => {
  return (event) => {
    // Only reference what you need
    console.log('Handler called');
  };
};
```

## 6. Performance Optimization

### Debouncing and Throttling
```javascript
const debounce = (func, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

const throttle = (func, limit) => {
  let inThrottle;
  return (...args) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};
```

These patterns will help you write more maintainable, efficient JavaScript code. Remember to choose the right pattern for your specific use case.
""",
            "excerpt": "Explore advanced JavaScript patterns including modules, observers, async patterns, and functional programming concepts for better code organization.",
            "author_index": 1,  # John Doe
            "category_index": 3,  # Tutorials
            "tag_indices": [1, 9, 11, 13],  # JavaScript, Frontend, Tutorial, Advanced
            "is_published": True,
            "is_featured": False,
            "reading_time": 12
        }
    ]
    
    created_posts = []
    
    async for session in get_db_session():
        for post_data in posts_data:
            # Check if post exists
            from sqlalchemy import select
            title_slug = generate_slug(post_data["title"])
            stmt = select(Post).where(Post.slug == title_slug)
            result = await session.execute(stmt)
            existing_post = result.scalar_one_or_none()
            
            if existing_post:
                print(f"Post '{post_data['title']}' already exists, skipping...")
                created_posts.append(existing_post)
                continue
            
            # Create post
            post = Post(
                title=post_data["title"],
                slug=title_slug,
                content=post_data["content"],
                excerpt=post_data["excerpt"],
                author_id=users[post_data["author_index"]].id,
                category_id=categories[post_data["category_index"]].id,
                is_published=post_data["is_published"],
                is_featured=post_data["is_featured"],
                reading_time=post_data["reading_time"],
                published_at=datetime.utcnow() if post_data["is_published"] else None,
                view_count=0
            )
            
            session.add(post)
            await session.flush()  # Get post ID
            await session.refresh(post)  # Ensure post is fully loaded

import asyncio
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session, engine
from models.user import User, Profile, UserRole
from models.post import Post, Category, Tag
from models.base import Base
from services.user.auth import AuthService
from utils.slug_generator import generate_slug


async def create_users_and_profiles():
    """Create admin user and regular users with their profiles"""
    users_data = [
        {
            "email": "admin@craftyx.com",
            "username": "admin",
            "full_name": "CraftyX Admin", 
            "password": "admin123",
            "role": UserRole.ADMIN,
            "is_verified": True,
            "profile": {
                "bio": "Platform administrator and content curator for CraftyX Hub. Passionate about creating engaging content and fostering community growth.",
                "location": "San Francisco, CA",
                "website": "https://craftyx.com",
                "twitter_handle": "craftyx_admin",
                "github_handle": "craftyx-official"
            }
        },
        {
            "email": "john.doe@example.com", 
            "username": "johndoe",
            "full_name": "John Doe",
            "password": "password123",
            "role": UserRole.USER,
            "is_verified": True,
            "profile": {
                "bio": "Full-stack developer passionate about React, Node.js, and building scalable web applications. Always learning new technologies.",
                "location": "New York, NY",
                "website": "https://johndoe.dev",
                "twitter_handle": "johndoe_dev",
                "github_handle": "johndoe-dev",
                "linkedin_handle": "johndoe-developer"
            }
        },
        {
            "email": "jane.smith@example.com",
            "username": "janesmith", 
            "full_name": "Jane Smith",
            "password": "password123",
            "role": UserRole.USER,
            "is_verified": True,
            "profile": {
                "bio": "UI/UX designer and frontend developer. Love creating beautiful, user-friendly interfaces and writing about design trends.",
                "location": "Los Angeles, CA",
                "website": "https://janesmith.design",
                "twitter_handle": "janesmith_ux",
                "github_handle": "janesmith-design",
                "linkedin_handle": "jane-smith-designer"
            }
        }
    ]
    
    created_users = []
    
    async for session in get_db_session():
        for user_data in users_data:
            # Check if user already exists
            existing_user = await AuthService.get_user_by_email(session, user_data["email"])
            if existing_user:
                print(f"User {user_data['email']} already exists, skipping...")
                created_users.append(existing_user)
                continue
                
            # Create user
            hashed_password = AuthService.get_password_hash(user_data["password"])
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                full_name=user_data["full_name"],
                password=hashed_password,
                role=user_data["role"],
                is_verified=user_data["is_verified"],
                is_active=True
            )
            
            session.add(user)
            await session.flush()  # Get the user ID
            
            # Create profile
            profile = Profile(
                user_id=user.id,
                bio=user_data["profile"]["bio"],
                location=user_data["profile"]["location"],
                website=user_data["profile"]["website"],
                twitter_handle=user_data["profile"]["twitter_handle"],
                github_handle=user_data["profile"]["github_handle"],
                linkedin_handle=user_data["profile"].get("linkedin_handle")
            )
            
            session.add(profile)
            created_users.append(user)
            print(f"Created user: {user.full_name} ({user.role.value})")
            
        await session.commit()
    
    return created_users


async def create_categories():
    """Create blog categories"""
    categories_data = [
        {
            "name": "Web Development",
            "slug": "web-development", 
            "description": "Articles about frontend, backend, and full-stack web development"
        },
        {
            "name": "Design",
            "slug": "design",
            "description": "UI/UX design, graphic design, and design thinking articles"
        },
        {
            "name": "Technology",
            "slug": "technology",
            "description": "Latest technology trends, tools, and innovations"
        },
        {
            "name": "Tutorials",
            "slug": "tutorials",
            "description": "Step-by-step guides and how-to articles"
        },
        {
            "name": "Career",
            "slug": "career",
            "description": "Career advice, job hunting tips, and professional development"
        }
    ]
    
    created_categories = []
    
    async for session in get_db_session():
        for cat_data in categories_data:
            # Check if category exists
            from sqlalchemy import select
            stmt = select(Category).where(Category.slug == cat_data["slug"])
            result = await session.execute(stmt)
            existing_category = result.scalar_one_or_none()
            
            if existing_category:
                print(f"Category {cat_data['name']} already exists, skipping...")
                created_categories.append(existing_category)
                continue
                
            category = Category(
                name=cat_data["name"],
                slug=cat_data["slug"],
                description=cat_data["description"]
            )
            
            session.add(category)
            created_categories.append(category)
            print(f"Created category: {category.name}")
            
        await session.commit()
    
    return created_categories


async def create_tags():
    """Create blog tags"""
    tags_data = [
        {"name": "React", "slug": "react"},
        {"name": "JavaScript", "slug": "javascript"},
        {"name": "Python", "slug": "python"},
        {"name": "FastAPI", "slug": "fastapi"},
        {"name": "CSS", "slug": "css"},
        {"name": "HTML", "slug": "html"},
        {"name": "Node.js", "slug": "nodejs"},
        {"name": "PostgreSQL", "slug": "postgresql"},
        {"name": "API", "slug": "api"},
        {"name": "Frontend", "slug": "frontend"},
        {"name": "Backend", "slug": "backend"},
        {"name": "Tutorial", "slug": "tutorial"},
        {"name": "Beginner", "slug": "beginner"},
        {"name": "Advanced", "slug": "advanced"},
        {"name": "UI/UX", "slug": "ui-ux"}
    ]
    
    created_tags = []
    new_tags_count = 0
    
    async for session in get_db_session():
        for tag_data in tags_data:
            # Check if tag exists
            from sqlalchemy import select
            stmt = select(Tag).where(Tag.slug == tag_data["slug"])
            result = await session.execute(stmt)
            existing_tag = result.scalar_one_or_none()
            
            if existing_tag:
                await session.refresh(existing_tag)  # Ensure it's fully loaded
                created_tags.append(existing_tag)
                continue
                
            tag = Tag(
                name=tag_data["name"],
                slug=tag_data["slug"]
            )
            
            session.add(tag)
            await session.flush()
            await session.refresh(tag)  # Get ID and ensure loaded
            created_tags.append(tag)
            new_tags_count += 1
            
        await session.commit()
        print(f"Created {new_tags_count} tags")
    
    return created_tags


async def create_posts(users, categories, tags):
    """Create sample blog posts"""
    posts_data = [
        {
            "title": "Getting Started with FastAPI and React",
            "content": """# Getting Started with FastAPI and React

FastAPI is a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints. Combined with React for the frontend, it creates a powerful full-stack development experience.

## Why FastAPI?

FastAPI offers several advantages:
- **Fast performance**: One of the fastest Python frameworks available
- **Easy to use**: Intuitive design based on Python type hints
- **Automatic docs**: Interactive API documentation with Swagger UI
- **Modern Python**: Full support for async/await

## Setting Up FastAPI

First, install FastAPI and Uvicorn:

```bash
pip install fastapi uvicorn
```

Create a simple API:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}
```

## Building the React Frontend

Create a new React app:

```bash
npx create-react-app my-frontend
cd my-frontend
npm start
```

## Connecting Frontend and Backend

Use axios to make API calls from React to your FastAPI backend:

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

export default api;
```

This combination provides a robust foundation for modern web applications with excellent developer experience and performance.
""",
            "excerpt": "Learn how to build a modern web application using FastAPI for the backend and React for the frontend. This comprehensive guide covers setup, development, and deployment.",
            "author_index": 0,  # admin
            "category_index": 0,  # Web Development
            "tag_indices": [0, 1, 3, 9, 10],  # React, JavaScript, FastAPI, Frontend, Backend
            "is_published": True,
            "is_featured": True,
            "reading_time": 8
        },
        {
            "title": "Modern UI Design Principles for Web Applications",
            "content": """# Modern UI Design Principles for Web Applications

Creating intuitive and beautiful user interfaces is crucial for successful web applications. Here are the key principles every developer and designer should know.

## 1. Simplicity and Clarity

Keep your interface clean and focused. Every element should have a purpose:
- Remove unnecessary elements
- Use whitespace effectively
- Prioritize content hierarchy

## 2. Consistency

Maintain consistency throughout your application:
- Use a consistent color palette
- Apply typography rules uniformly
- Keep interaction patterns predictable

## 3. Responsive Design

Your application should work seamlessly across all devices:
- Mobile-first approach
- Flexible grid systems
- Scalable images and media

## 4. Accessibility

Design for everyone:
- Use semantic HTML
- Ensure proper color contrast
- Implement keyboard navigation
- Add alt text for images

## 5. Performance

Fast loading times are essential:
- Optimize images
- Minimize HTTP requests
- Use efficient CSS and JavaScript

## Color Theory in UI Design

Understanding color psychology helps create better user experiences:
- **Blue**: Trust, reliability (used by Facebook, Twitter)
- **Green**: Growth, success (used by Spotify, WhatsApp)
- **Red**: Urgency, attention (used for error states)

## Typography Best Practices

Choose fonts that enhance readability:
- Use a maximum of 2-3 font families
- Ensure proper line spacing
- Consider font weight hierarchy

Remember, great design is invisible - users should be able to accomplish their goals without thinking about the interface.
""",
            "excerpt": "Discover the fundamental principles of modern UI design that will help you create more intuitive and visually appealing web applications.",
            "author_index": 2,  # Jane Smith
            "category_index": 1,  # Design
            "tag_indices": [4, 5, 9, 14],  # CSS, HTML, Frontend, UI/UX
            "is_published": True,
            "is_featured": True,
            "reading_time": 6
        },
        {
            "title": "Building RESTful APIs with Python and FastAPI",
            "content": """# Building RESTful APIs with Python and FastAPI

REST (Representational State Transfer) is an architectural style for designing networked applications. FastAPI makes building RESTful APIs in Python incredibly straightforward and enjoyable.

## What is REST?

REST is based on several key principles:
- **Stateless**: Each request contains all necessary information
- **Resource-based**: URLs represent resources, not actions
- **HTTP methods**: Use GET, POST, PUT, DELETE appropriately
- **JSON responses**: Structured data format

## Setting Up Your FastAPI Project

Start with a proper project structure:

```
my_api/
├── main.py
├── models/
├── routers/
├── schemas/
└── services/
```

## Creating Your First Endpoint

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    email: str

users = []

@app.get("/users", response_model=List[User])
async def get_users():
    return users

@app.post("/users", response_model=User)
async def create_user(user: User):
    users.append(user)
    return user

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    for user in users:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")
```

## Database Integration

Use SQLAlchemy with FastAPI for database operations:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

## API Documentation

FastAPI automatically generates interactive API documentation at `/docs` and `/redoc`. This makes testing and sharing your API effortless.

## Best Practices

1. **Use Pydantic models** for request/response validation
2. **Implement proper error handling** with meaningful HTTP status codes
3. **Add authentication and authorization** for secured endpoints
4. **Version your API** for backward compatibility
5. **Write tests** for all endpoints

Building APIs with FastAPI is not just about speed - it's about creating maintainable, well-documented, and reliable services that power modern applications.
""",
            "excerpt": "A comprehensive guide to building RESTful APIs using FastAPI. Learn best practices, database integration, and how to create maintainable API services.",
            "author_index": 1,  # John Doe
            "category_index": 0,  # Web Development
            "tag_indices": [2, 3, 8, 10, 11],  # Python, FastAPI, API, Backend, Tutorial
            "is_published": True,
            "is_featured": False,
            "reading_time": 10
        },
        {
            "title": "Career Tips for Junior Developers",
            "content": """# Career Tips for Junior Developers

Starting your career as a developer can be both exciting and overwhelming. Here are practical tips to help you navigate your early career successfully.

## 1. Focus on Fundamentals

Before diving into the latest frameworks, master the basics:
- **Programming fundamentals**: Variables, functions, loops, conditionals
- **Data structures**: Arrays, objects, lists, dictionaries
- **Problem-solving**: Break complex problems into smaller parts
- **Version control**: Learn Git thoroughly

## 2. Build a Strong Portfolio

Your portfolio is your calling card:
- Create 3-5 quality projects rather than 20 mediocre ones
- Include a variety of technologies
- Write clear README files
- Deploy your projects live
- Show the problem your project solves

## 3. Learn to Learn

Technology evolves rapidly. Develop these learning habits:
- Read documentation thoroughly
- Practice coding daily (even 30 minutes helps)
- Join developer communities
- Follow industry blogs and newsletters
- Attend meetups and conferences

## 4. Communication is Key

Technical skills alone aren't enough:
- Learn to explain complex concepts simply
- Ask questions when you're stuck
- Document your code clearly
- Practice presenting your work
- Collaborate effectively with teams

## 5. Don't Compare Yourself to Others

Everyone's journey is different:
- Focus on your own progress
- Celebrate small wins
- Learn from mistakes without harsh self-judgment
- Find mentors who inspire you
- Remember that senior developers were once beginners too

## 6. Networking and Community

Build meaningful professional relationships:
- Contribute to open source projects
- Answer questions on Stack Overflow
- Share your learning journey on social media
- Attend local tech meetups
- Find a mentor

## 7. Practical Job Search Tips

When you're ready to apply:
- Tailor your resume to each job
- Practice coding interviews regularly
- Prepare stories about your projects
- Research the company thoroughly
- Follow up professionally after interviews

## 8. Once You Land the Job

Make the most of your first role:
- Ask lots of questions (you're expected to)
- Volunteer for diverse projects
- Seek feedback regularly
- Document what you learn
- Be patient with yourself

Remember, becoming a great developer is a marathon, not a sprint. Focus on consistent growth, and you'll be amazed at how far you can go.
""",
            "excerpt": "Essential career advice for junior developers looking to build successful careers in tech. From fundamentals to job searching and beyond.",
            "author_index": 0,  # Admin
            "category_index": 4,  # Career
            "tag_indices": [11, 12],  # Tutorial, Beginner
            "is_published": True,
            "is_featured": False,
            "reading_time": 7
        },
        {
            "title": "Advanced JavaScript Patterns and Best Practices",
            "content": """# Advanced JavaScript Patterns and Best Practices

As you grow as a JavaScript developer, understanding advanced patterns and best practices becomes crucial for writing maintainable, performant code.

## 1. Module Patterns

### ES6 Modules
```javascript
// utils.js
export const formatDate = (date) => {
  return new Intl.DateTimeFormat('en-US').format(date);
};

export const debounce = (func, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(null, args), delay);
  };
};

// main.js
import { formatDate, debounce } from './utils.js';
```

### Revealing Module Pattern
```javascript
const UserModule = (() => {
  let users = [];
  
  const addUser = (user) => {
    users.push(user);
  };
  
  const getUsers = () => {
    return [...users]; // Return a copy
  };
  
  // Public API
  return {
    addUser,
    getUsers
  };
})();
```

## 2. Observer Pattern

Great for event-driven architectures:

```javascript
class EventEmitter {
  constructor() {
    this.events = {};
  }
  
  on(event, callback) {
    if (!this.events[event]) {
      this.events[event] = [];
    }
    this.events[event].push(callback);
  }
  
  emit(event, data) {
    if (this.events[event]) {
      this.events[event].forEach(callback => callback(data));
    }
  }
  
  off(event, callback) {
    if (this.events[event]) {
      this.events[event] = this.events[event].filter(cb => cb !== callback);
    }
  }
}
```

## 3. Async/Await Best Practices

### Error Handling
```javascript
const fetchUserData = async (userId) => {
  try {
    const response = await fetch(`/api/users/${userId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to fetch user data:', error);
    throw error; // Re-throw to let caller handle
  }
};
```

### Parallel Execution
```javascript
const fetchAllData = async () => {
  try {
    // Run requests in parallel
    const [users, posts, comments] = await Promise.all([
      fetchUsers(),
      fetchPosts(),
      fetchComments()
    ]);
    
    return { users, posts, comments };
  } catch (error) {
    console.error('Failed to fetch data:', error);
  }
};
```

## 4. Functional Programming Concepts

### Pure Functions
```javascript
// Pure function - no side effects
const calculateTotal = (items) => {
  return items.reduce((total, item) => total + item.price, 0);
};

// Impure function - modifies external state
let total = 0;
const addToTotal = (amount) => {
  total += amount; // Side effect!
  return total;
};
```

### Higher-Order Functions
```javascript
const withLogging = (fn) => {
  return (...args) => {
    console.log(`Calling ${fn.name} with args:`, args);
    const result = fn(...args);
    console.log(`Result:`, result);
    return result;
  };
};

const add = (a, b) => a + b;
const loggedAdd = withLogging(add);
```

## 5. Memory Management

### Avoiding Memory Leaks
```javascript
// Bad - creates memory leak
const createHandler = () => {
  const largeData = new Array(1000000).fill('data');
  
  return (event) => {
    // Handler keeps reference to largeData
    console.log(largeData.length);
  };
};

// Good - clean up references
const createHandler = () => {
  return (event) => {
    // Only reference what you need
    console.log('Handler called');
  };
};
```

## 6. Performance Optimization

### Debouncing and Throttling
```javascript
const debounce = (func, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

const throttle = (func, limit) => {
  let inThrottle;
  return (...args) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};
```

These patterns will help you write more maintainable, efficient JavaScript code. Remember to choose the right pattern for your specific use case.
""",
            "excerpt": "Explore advanced JavaScript patterns including modules, observers, async patterns, and functional programming concepts for better code organization.",
            "author_index": 1,  # John Doe
            "category_index": 3,  # Tutorials
            "tag_indices": [1, 9, 11, 13],  # JavaScript, Frontend, Tutorial, Advanced
            "is_published": True,
            "is_featured": False,
            "reading_time": 12
        }
    ]
    
    created_posts = []
    
    async for session in get_db_session():
        for post_data in posts_data:
            # Check if post exists
            from sqlalchemy import select
            title_slug = generate_slug(post_data["title"])
            stmt = select(Post).where(Post.slug == title_slug)
            result = await session.execute(stmt)
            existing_post = result.scalar_one_or_none()
            
            if existing_post:
                print(f"Post '{post_data['title']}' already exists, skipping...")
                created_posts.append(existing_post)
                continue
            
            # Create post
            post = Post(
                title=post_data["title"],
                slug=title_slug,
                content=post_data["content"],
                excerpt=post_data["excerpt"],
                author_id=users[post_data["author_index"]].id,
                category_id=categories[post_data["category_index"]].id,
                is_published=post_data["is_published"],
                is_featured=post_data["is_featured"],
                reading_time=post_data["reading_time"],
                published_at=datetime.utcnow() if post_data["is_published"] else None,
                view_count=0
            )
            
            session.add(post)
            await session.flush()  # Get post ID
            await session.refresh(post)  # Ensure post is fully loaded
            
            # Add tags to post using association table within current session
            from sqlalchemy import select
            for tag_index in post_data["tag_indices"]:
                slug_value = tags[tag_index].slug
                tag_stmt = select(Tag).where(Tag.slug == slug_value)
                tag_result = await session.execute(tag_stmt)
                tag_in_session = tag_result.scalar_one()
                post.tags.append(tag_in_session)
            await session.flush()  # Flush after assigning tags
            
            created_posts.append(post)
            print(f"Created post: {post.title}")
            
        await session.commit()
    
    return created_posts


async def main():
    """Main seeding function"""
    print("Starting database seeding...")
    
    try:
        # Create tables if they don't exist
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables ready")
        
        # Create users and profiles
        print("\nCreating users and profiles...")
        users = await create_users_and_profiles()
        
        # Create categories
        print("\nCreating categories...")
        categories = await create_categories()
        
        # Create tags
        print("\nCreating tags...")
        tags = await create_tags()
        
        # Create posts
        print("\nCreating posts...")
        posts = await create_posts(users, categories, tags)
        
        print(f"""
Database seeding completed successfully!

Created:
- {len(users)} users (1 admin, 2 regular users)
- {len(categories)} categories
- {len(tags)} tags  
- {len(posts)} blog posts

Admin credentials:
- Email: admin@craftyx.com
- Password: admin123

Regular user credentials:
- john.doe@example.com / password123
- jane.smith@example.com / password123
        """)
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 