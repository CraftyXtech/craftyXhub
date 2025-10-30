import { textUtils } from '../utils/textUtils';

const sampleContent = {
  'blog-ideas': [
    {
      title: 'Top 10 Emerging Trends in Digital Marketing for 2024',
      content: 'Explore the latest trends reshaping the digital marketing landscape, from AI-powered personalization to voice search optimization.'
    },
    {
      title: 'How to Build a Successful Content Marketing Strategy from Scratch',
      content: 'A comprehensive guide to creating, implementing, and measuring a content marketing strategy that drives real business results.'
    },
    {
      title: 'The Ultimate Guide to Social Media Engagement: Best Practices and Tools',
      content: 'Learn proven strategies and leverage the right tools to boost your social media engagement and grow your online community.'
    }
  ],
  'blog-outline': [
    {
      title: 'Complete Blog Post Outline',
      content: `<h2>Introduction</h2>
<p>Hook readers with a compelling question or statement that addresses their pain point.</p>

<h2>Understanding the Problem</h2>
<p>Deep dive into the core issue your readers are facing and why it matters.</p>

<h2>Solution Overview</h2>
<p>Present your main solution or approach to solving the problem.</p>

<h2>Step-by-Step Guide</h2>
<ul>
  <li>Step 1: Initial setup and preparation</li>
  <li>Step 2: Implementation details</li>
  <li>Step 3: Testing and optimization</li>
  <li>Step 4: Monitoring and maintenance</li>
</ul>

<h2>Common Challenges and How to Overcome Them</h2>
<p>Address potential roadblocks and provide practical solutions.</p>

<h2>Best Practices and Pro Tips</h2>
<p>Share expert insights and advanced techniques.</p>

<h2>Conclusion</h2>
<p>Summarize key takeaways and provide a clear call-to-action.</p>`
    }
  ],
  'social-media-post': [
    {
      title: 'Engaging Social Media Post',
      content: `Did you know that 80% of businesses struggle with consistent content creation? 

Here's how we solved it:

✅ Create a content calendar
✅ Batch-produce content
✅ Use AI tools for ideation
✅ Repurpose top-performing posts

Which tip will you implement first? Let me know in the comments! 👇

#ContentMarketing #SocialMediaTips #MarketingStrategy`
    }
  ],
  'meta-description': [
    {
      title: 'SEO-Optimized Meta Tags',
      content: `<strong>Meta Title:</strong> Digital Marketing Trends 2024 | Complete Guide & Best Practices

<strong>Meta Description:</strong> Discover the top digital marketing trends shaping 2024. Learn proven strategies, tools, and techniques to stay ahead of the competition and grow your business.`
    }
  ],
  'default': [
    {
      title: 'Generated Content',
      content: `<h2>Introduction</h2>
<p>In today's fast-paced digital landscape, creating engaging content has become more crucial than ever. Whether you're a blogger, marketer, or business owner, understanding how to craft compelling narratives can significantly impact your success.</p>

<h2>Key Points to Consider</h2>
<p>When developing your content strategy, focus on these essential elements:</p>
<ul>
  <li>Understanding your target audience's needs and pain points</li>
  <li>Creating value-driven content that solves real problems</li>
  <li>Maintaining consistency in your messaging and publishing schedule</li>
  <li>Optimizing for search engines while keeping human readers first</li>
</ul>

<h2>Implementing Best Practices</h2>
<p>To maximize your content's effectiveness, consider incorporating data-driven insights, storytelling techniques, and interactive elements that encourage engagement. Remember, quality always trumps quantity.</p>

<h2>Conclusion</h2>
<p>By following these guidelines and continuously refining your approach based on performance metrics, you'll be well-positioned to achieve your content marketing goals and build a loyal audience.</p>`
    }
  ]
};

const generateVariant = (baseContent, variantNumber) => {
  const variants = [
    baseContent,
    {
      ...baseContent,
      content: baseContent.content.replace(/\b(crucial|important|essential)\b/gi, 'vital')
        .replace(/\b(significantly|greatly)\b/gi, 'substantially')
    },
    {
      ...baseContent,
      content: baseContent.content.replace(/\b(understand|comprehend)\b/gi, 'grasp')
        .replace(/\b(impact|effect)\b/gi, 'influence')
    }
  ];
  
  return variants[variantNumber % variants.length];
};

export const mockGenerator = {
  generate: async ({ template, prompt, keywords = [], tone = 'professional', language = 'en-US', variants = 1 }) => {
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const templateContent = sampleContent[template] || sampleContent['default'];
    const baseContent = templateContent[Math.floor(Math.random() * templateContent.length)];
    
    const results = [];
    for (let i = 0; i < variants; i++) {
      const variant = generateVariant(baseContent, i);
      const content = variant.content;
      
      results.push({
        title: variant.title,
        content: content,
        metadata: {
          words: textUtils.countWords(content),
          characters: textUtils.countCharacters(content),
          readingTime: textUtils.estimateReadingTime(content),
          tone: tone,
          language: language,
          keywords: keywords,
          prompt: prompt,
          template: template
        },
        generated_at: new Date().toISOString()
      });
    }
    
    return results;
  }
};

