import React, { useEffect, useRef, useState, memo } from 'react'

// Libraries
import { Link } from 'react-router-dom';
import { m } from 'framer-motion';
import { PropTypes } from "prop-types";

// Components
import Pagination from './HelperComponents/Pagination';
import Filter from "./BlogFilter";

// Data
import { blogData } from './BlogData';

// Filter the blog data category wise
const blogClassicData = blogData.filter((item) => item.blogType === "classic");

const BlogClassic = (props) => {
  const blogWrapper = useRef();
  const [loading, setLoading] = useState(true);

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
                <m.div className="blog-classic"
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
                        src={item.featured_image || item.img} 
                        alt={item.title} 
                        className="rounded-[4px] md:mb-[40px] sm:mb-[33px] xs:mb-[28px]" 
                      />
                    </Link>
                  </div>
                  <div className="post-details">
                    <Link 
                      aria-label="link" 
                      to={`${props.link}${item.uuid}`}
                    >
                      {item.title}
                    </Link>
                    <p>{item.content}</p>
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