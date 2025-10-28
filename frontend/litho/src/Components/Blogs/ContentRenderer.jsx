import React from 'react'
import Blockquote from '../BlockQuote/Blockquote'
import Dropcaps from '../Dropcaps/Dropcaps'
import { getImageUrl } from '../../api'

const ContentRenderer = ({ content, contentBlocks }) => {
  if (contentBlocks && Array.isArray(contentBlocks)) {
    return (
      <div className="post-content">
        {contentBlocks.map((block, index) => {
          switch (block.type) {
            case 'paragraph':
              return (
                <p key={index} className="mb-[25px]">
                  {block.content}
                </p>
              )
            
            case 'blockquote':
              return (
                <Blockquote
                  key={index}
                  className={block.className || "my-[5.5rem] ml-24 sm:ml-0"}
                  theme={block.style || "blockquote-style-02"}
                  title={block.content}
                  author={block.author}
                />
              )
            
            case 'dropcap':
              return (
                <Dropcaps
                  key={index}
                  theme={block.style || "dropcaps-style04"}
                  content={block.content}
                  className="mb-[25px]"
                />
              )
            
            case 'image':
              return (
                <img
                  key={index}
                  src={getImageUrl(block.src, "posts")}
                  alt={block.alt || ""}
                  className={block.className || "w-full rounded-[6px] mb-16"}
                />
              )
            
            default:
              return null
          }
        })}
      </div>
    )
  }

  if (content) {
    return (
      <div 
        className="post-content prose prose-lg max-w-none"
        dangerouslySetInnerHTML={{ __html: content.replace(/\n/g, '<br />') }} 
      />
    )
  }

  return <p className="text-gray-500">No content available.</p>
}

export default ContentRenderer
