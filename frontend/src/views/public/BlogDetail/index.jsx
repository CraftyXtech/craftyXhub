import { Box, Container, Typography, Chip, Avatar, Stack, Divider, Paper } from '@mui/material';
import { motion } from 'framer-motion';
import { ThemeFonts } from '@/config';

const MotionBox = motion.create(Box);

// Sample blog post data
const post = {
  title: 'Building a Modern Blog with React and MUI',
  subtitle: 'A deep dive into creating a premium blog experience with the latest web technologies',
  author: {
    name: 'Sarah Chen',
    avatar: '',
    role: 'Senior Frontend Developer'
  },
  date: 'December 28, 2024',
  readTime: '8 min read',
  category: 'Technology',
  featuredImage: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1200&h=600&fit=crop',
  content: `
## Introduction

Welcome to this comprehensive guide on building a modern blog with React and Material-UI. In this tutorial, we'll explore best practices for creating a premium reading experience that your users will love.

## Setting Up the Project

First, let's create a new React project with Vite. Vite provides an incredibly fast development experience with hot module replacement.

\`\`\`bash
npm create vite@latest my-blog -- --template react
cd my-blog
npm install
\`\`\`

## Installing Dependencies

We'll need a few packages to get started:

\`\`\`bash
npm install @mui/material @emotion/react @emotion/styled framer-motion
\`\`\`

## Creating the Theme

One of the most important aspects of a premium blog is typography. Here's how we set up our font system:

\`\`\`javascript
// config.js
export const ThemeFonts = {
  FONT_HEADING: "'Plus Jakarta Sans Variable', sans-serif",
  FONT_BODY: "'Inter Variable', sans-serif",
  FONT_MONO: "'JetBrains Mono Variable', monospace"
};
\`\`\`

Notice how we use different fonts for different purposes:

- **Plus Jakarta Sans** for headings - geometric and modern
- **Inter** for body text - optimal readability
- **JetBrains Mono** for code - with beautiful ligatures

## The Code Block Component

Here's a reusable code block component that uses JetBrains Mono:

\`\`\`jsx
function CodeBlock({ code, language }) {
  return (
    <Paper sx={{ 
      p: 3, 
      bgcolor: '#1a1a1a', 
      fontFamily: ThemeFonts.FONT_MONO,
      overflow: 'auto'
    }}>
      <pre style={{ margin: 0 }}>
        <code>{code}</code>
      </pre>
    </Paper>
  );
}
\`\`\`

## Key Takeaways

1. **Typography matters** - Use a dual-font system for visual hierarchy
2. **Performance is key** - Use variable fonts for smaller bundle sizes
3. **Consistency wins** - Apply your design system throughout

## Conclusion

Building a premium blog experience comes down to attention to detail. With the right fonts, colors, and layout, you can create something that stands out from the crowd.

Happy coding! 🚀
  `
};

// Simple code block component
function CodeBlock({ children }) {
  return (
    <Paper
      component="pre"
      sx={{
        p: 3,
        my: 3,
        bgcolor: '#1a1a1a',
        color: '#e0e0e0',
        borderRadius: 2,
        overflow: 'auto',
        fontFamily: ThemeFonts.FONT_MONO,
        fontSize: '0.875rem',
        lineHeight: 1.7,
        '& code': {
          fontFamily: 'inherit'
        }
      }}
    >
      <code>{children}</code>
    </Paper>
  );
}

// Parse content and render with proper formatting
function BlogContent({ content }) {
  const lines = content.trim().split('\n');
  const elements = [];
  let currentCode = [];
  let inCodeBlock = false;
  let codeLanguage = '';

  lines.forEach((line, index) => {
    if (line.startsWith('```')) {
      if (inCodeBlock) {
        // End of code block
        elements.push(
          <CodeBlock key={`code-${index}`}>
            {currentCode.join('\n')}
          </CodeBlock>
        );
        currentCode = [];
        inCodeBlock = false;
      } else {
        // Start of code block
        inCodeBlock = true;
        codeLanguage = line.slice(3);
      }
    } else if (inCodeBlock) {
      currentCode.push(line);
    } else if (line.startsWith('## ')) {
      elements.push(
        <Typography key={index} variant="h4" sx={{ mt: 5, mb: 2 }}>
          {line.slice(3)}
        </Typography>
      );
    } else if (line.startsWith('- **')) {
      // Bold list item
      const match = line.match(/- \*\*(.+?)\*\* - (.+)/);
      if (match) {
        elements.push(
          <Typography key={index} component="li" sx={{ mb: 1, ml: 3 }}>
            <strong>{match[1]}</strong> - {match[2]}
          </Typography>
        );
      }
    } else if (line.startsWith('1. ') || line.startsWith('2. ') || line.startsWith('3. ')) {
      elements.push(
        <Typography key={index} component="li" sx={{ mb: 1, ml: 3 }}>
          {line.slice(3)}
        </Typography>
      );
    } else if (line.trim() === '') {
      // Skip empty lines
    } else {
      elements.push(
        <Typography key={index} variant="body1" sx={{ mb: 2, color: 'text.secondary' }}>
          {line}
        </Typography>
      );
    }
  });

  return <>{elements}</>;
}

export default function BlogDetail() {
  return (
    <Box sx={{ py: { xs: 4, md: 8 } }}>
      <Container maxWidth="md">
        {/* Header */}
        <MotionBox
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Category */}
          <Chip
            label={post.category}
            size="small"
            sx={{
              mb: 3,
              bgcolor: 'grey.100',
              color: 'text.primary',
              fontWeight: 600
            }}
          />

          {/* Title */}
          <Typography
            variant="h1"
            sx={{
              fontSize: { xs: '2rem', md: '3rem' },
              mb: 2
            }}
          >
            {post.title}
          </Typography>

          {/* Subtitle */}
          <Typography
            variant="h5"
            sx={{
              color: 'text.secondary',
              fontWeight: 400,
              mb: 4
            }}
          >
            {post.subtitle}
          </Typography>

          {/* Author & Meta */}
          <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 4 }}>
            <Avatar sx={{ width: 48, height: 48, bgcolor: 'primary.main' }}>
              {post.author.name[0]}
            </Avatar>
            <Box>
              <Typography variant="subtitle1" fontWeight={600}>
                {post.author.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {post.date} · {post.readTime}
              </Typography>
            </Box>
          </Stack>

          <Divider sx={{ mb: 4 }} />
        </MotionBox>

        {/* Featured Image */}
        <MotionBox
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          sx={{ mb: 5 }}
        >
          <Box
            component="img"
            src={post.featuredImage}
            alt={post.title}
            sx={{
              width: '100%',
              height: 'auto',
              borderRadius: 3,
              boxShadow: 3
            }}
          />
        </MotionBox>

        {/* Content */}
        <MotionBox
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          sx={{
            '& ul, & ol': {
              pl: 0,
              listStyle: 'none'
            }
          }}
        >
          <BlogContent content={post.content} />
        </MotionBox>

        {/* Font Demo Section */}
        <Box sx={{ mt: 8, p: 4, bgcolor: 'grey.50', borderRadius: 3 }}>
          <Typography variant="h5" sx={{ mb: 3 }}>
            📝 Font Demo
          </Typography>
          
          <Stack spacing={3}>
            <Box>
              <Typography variant="overline" color="text.secondary">
                Headings: Plus Jakarta Sans
              </Typography>
              <Typography variant="h3">
                The quick brown fox jumps over the lazy dog
              </Typography>
            </Box>

            <Divider />

            <Box>
              <Typography variant="overline" color="text.secondary">
                Body: Inter
              </Typography>
              <Typography variant="body1">
                The quick brown fox jumps over the lazy dog. This font is optimized for readability in long-form content, making it perfect for blog posts and articles.
              </Typography>
            </Box>

            <Divider />

            <Box>
              <Typography variant="overline" color="text.secondary">
                Code: JetBrains Mono (with ligatures)
              </Typography>
              <Paper
                sx={{
                  p: 2,
                  bgcolor: '#1a1a1a',
                  color: '#e0e0e0',
                  fontFamily: ThemeFonts.FONT_MONO,
                  fontSize: '0.9rem',
                  borderRadius: 2
                }}
              >
                <code>
                  {`const greeting = (name) => \`Hello, \${name}!\`;
// Ligatures: != !== === => -> >= <=`}
                </code>
              </Paper>
            </Box>
          </Stack>
        </Box>
      </Container>
    </Box>
  );
}
