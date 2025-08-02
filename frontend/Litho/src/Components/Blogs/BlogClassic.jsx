import React, { useEffect, useRef, useState, memo } from 'react'

// Libraries
import { Link } from 'react-router-dom';
import { m } from 'framer-motion';
import { PropTypes } from "prop-types";

// Components
import Pagination from './HelperComponents/Pagination';
import Filter from "./BlogFilter";
import Buttons from '../Button/Buttons';

// Data
import { blogData } from './BlogData';

// API
import { getImageUrl } from '../../api';

// Filter the blog data category wise
const blogClassicData = blogData.filter((item) => item.blogType === "classic");

const BlogClassic = (props) => {
  const blogWrapper = useRef();
  const [loading, setLoading] = useState(true);

  // Utility function to truncate content and strip HTML
  const truncateWords = (text, limit = 50) => {
    if (!text) return '';
    // Strip HTML tags, decode HTML entities, and get plain text
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = text;
    const plainText = tempDiv.textContent || tempDiv.innerText || '';
    const cleanText = plainText.replace(/\s+/g, ' ').trim();
    
    const words = cleanText.split(' ');
    if (words.length > limit) {
      return words.slice(0, limit).join(' ') + '...';
    }
    return cleanText;
  };

  useEffect(() => {
    import("../../Functions/Utilities").then(module => {
      const grid = module.initializeIsotop(blogWrapper.current)
      grid.on('arrangeComplete', () => setLoading(false));
    })
  })

  const handleFilterChange = () => {
    blogWrapper.current.querySelectorAll("li").forEach(item => item.childNodes[0]?.classList.add("appear"))
  }

  return (
    <div className="grid-wrapper">
      {/* Filter Start */}
      <Filter title={props.title} filterData={props.filterData} onFilterChange={handleFilterChange} />
      {/* Filter End */}

      {/* Grid Start */}
      <ul ref={blogWrapper} className={`grid-container${props.grid ? ` ${props.grid}` : ""}${loading ? " loading" : ""}${props.filter === false ? "" : " mt-28 md:mt-[4.5rem] sm:mt-8"}`}>
        <li className="grid-sizer"></li>
        {
          props.data.map((item, i) => {
            return (
              <li key={i} className={`grid-item${item.double_col ? " grid-item-double" : ""} ${(() => {
                let categories = Array.isArray(item.category) ? item.category : (item.category && item.category.name ? [item.category.name] : []);
                return categories.map(cat => cat.split(" ").join("")).join(" ").toLowerCase();
              })()}`}>
                <m.div className="blog-classic mb-12 md:mb-10 sm:mb-8"
                  initial={{ opacity: 0 }}
                  whileInView={!loading && { opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, ease: "easeOut" }}>
                  <div className="blog-post-image">
                    <Link 
                      aria-label="link" 
                      to={`${props.link}${item.uuid}`}
                    >
                      <img 
                        loading="lazy" 
                        src={getImageUrl(item.featured_image) || item.img} 
                        alt={item.title} 
                        className="rounded-[4px] w-full h-55 object-cover md:mb-[25px] sm:mb-[20px] xs:mb-[15px]" 
                      />
                    </Link>
                  </div>
                  <div className="post-details">
                    <Link 
                      aria-label="link" 
                      to={`${props.link}${item.uuid}`}
                      className="font-bold text-darkgray hover:text-fastblue transition-colors duration-300"
                    >
                      {item.title}
                    </Link>
                    <p className="mt-3 text-spanishgray leading-relaxed">
                      {truncateWords(item.content, 50)}
                    </p>
                    <div className="mt-4">
                      <Buttons
                        to={`${props.link}${item.uuid}`}
                        title="Continue Reading"
                        size="sm"
                        themeColor={["#0038e3", "#ff7a56"]}
                        className="btn-transparent"
                        ariaLabel={`Continue reading ${item.title}`}
                      />
                    </div>
                  </div>
                </m.div>
              </li>
            )
          })
        }
      </ul>
      {/* Grid End */}

      {/* Pagination Start */}
      {props.pagination === true && (
        <div className="flex justify-center mt-[7.5rem] md:mt-20">
          <Pagination />
        </div>)}
    </div>
  )
}

BlogClassic.defaultProps = {
  filter: false,
  data: blogClassicData,
  readMoreButton: "Continue reading",
  link: "/posts/"
}

BlogClassic.propTypes = {
  pagination: PropTypes.bool,
  title: PropTypes.string,
  grid: PropTypes.string,
  link: PropTypes.string,
  data: PropTypes.arrayOf(
    PropTypes.exact({
      id: PropTypes.number,
      category: PropTypes.array,
      tags: PropTypes.array,
      blogType: PropTypes.string,
      img: PropTypes.string,
      title: PropTypes.string,
      content: PropTypes.string,
      author: PropTypes.number,
      likes: PropTypes.number,
      comments: PropTypes.number,
      date: PropTypes.string,
      double_col: PropTypes.bool
    })
  ),
};

export default memo(BlogClassic)