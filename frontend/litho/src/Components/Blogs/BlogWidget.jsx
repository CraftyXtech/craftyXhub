import React, { useState, useEffect, useRef, memo } from 'react'

import { Link } from 'react-router-dom';
import { PropTypes } from "prop-types";
import { m } from 'framer-motion';
import Pagination from './HelperComponents/Pagination';
import Filter from "./BlogFilter";

import { blogData, authorData } from './BlogData';

import { getImageUrl } from '../../api';

// Filter the blog data category wise
const blogWidgetData = blogData.filter((item) => item.blogType === "widget");

const BlogWidget = (props) => {
  const blogWrapper = useRef();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    import("../../Functions/Utilities").then(module => {
      const grid = module.initializeIsotop(blogWrapper.current)
      grid.on('arrangeComplete', () => setLoading(false));
    })
  }, [])

  const handleFilterChange = () => {
    blogWrapper.current.querySelectorAll("li").forEach(item => item.childNodes[0]?.classList.add("appear"))
  }

  return (
    <div className="grid-wrapper">
      <Filter title={props.title} filterData={props.filterData} onFilterChange={handleFilterChange} />
        {/* Grid Start */}
      <ul ref={blogWrapper} className={`blog-widget grid-container ${props.grid ? ` ${props.grid}` : ""}${loading ? " loading" : ""}${props.filter === false ? "" : " mt-28 md:mt-[4.5rem] sm:mt-8"}`}>
        <li className="grid-sizer"></li>
        {
          props.data.map((item, i) => {
            return (
              <li key={i} className={`grid-item${item.double_col ? " grid-item-double" : ""} ${(() => {
                let categories = Array.isArray(item.category) ? item.category : (item.category && item.category.name ? [item.category.name] : []);
                return categories.map(cat => cat.split(" ").join("")).join(" ").toLowerCase();
              })()}`}>
                <m.div className="blog-widget-content bg-white flex p-[30px] xs:p-[15px] rounded-[4px] shadow-sm hover:shadow-md transition-shadow duration-300"
                  initial={{ opacity: 0 }}
                  whileInView={!loading && { opacity: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, ease: "easeOut" }} >
                  <figure className="shrink-0 h-auto w-[140px] mb-0 xs:w-[100px]">
                    <Link aria-label="link" to={`${props.link}${item.uuid || item.id}`}>
                      <img 
                        height={88} 
                        width={140} 
                        src={getImageUrl(item.featured_image) || item.img} 
                        alt={item.title}
                        className="rounded-[4px] object-cover w-full h-[88px]"
                      />
                    </Link>
                  </figure>
                  <div className="leading-normal pl-[30px] xs:pl-[15px] relative top-[-1px] grow">
                    <span className="mb-[5px] text-xs font-serif block text-spanishgray">
                      {item.date ? new Date(item.date).toLocaleDateString('en-US', { 
                        day: '2-digit', 
                        month: 'short', 
                        year: 'numeric' 
                      }) : new Date(item.created_at).toLocaleDateString('en-US', { 
                        day: '2-digit', 
                        month: 'short', 
                        year: 'numeric' 
                      })}
                    </span>
                    <Link 
                      aria-label="link" 
                      to={`${props.link}${item.uuid || item.id}`} 
                      className="mb-2 leading-[22px] font-medium text-darkgray font-serif block hover:text-fastblue transition-colors duration-300"
                    >
                      {item.title}
                    </Link>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-serif text-spanishgray">
                        By {item.author?.full_name || item.author?.username || 'Author'}
                      </span>
                      <div className="flex items-center space-x-2">
                        {item.is_published === false && (
                          <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full">
                            Draft
                          </span>
                        )}
                        {item.is_featured && (
                          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                            Featured
                          </span>
                        )}
                      </div>
                    </div>
                    
                                                {/* Action Buttons - Only show if showActions is true */}
                            {props.showActions !== false && (
                                <div className="flex items-center space-x-2">
                                    {item.is_published === false ? (
                                        // Draft Actions
                                        <>
                                            <button
                                                onClick={(e) => {
                                                    e.preventDefault();
                                                    props.onPublish && props.onPublish(item.uuid, item);
                                                }}
                                                className="text-xs bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded-md transition-colors duration-200 font-medium"
                                            >
                                                Publish
                                            </button>
                                            <Link
                                                to={`/posts/edit/${item.uuid}`}
                                                className="text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-md transition-colors duration-200 font-medium"
                                            >
                                                Edit
                                            </Link>
                                        </>
                                    ) : (
                                        // Published Actions
                                        <>
                                            <Link
                                                to={`${props.link}${item.uuid}`}
                                                className="text-xs bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded-md transition-colors duration-200 font-medium"
                                            >
                                                View
                                            </Link>
                                            <Link
                                                to={`/posts/edit/${item.uuid}`}
                                                className="text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-md transition-colors duration-200 font-medium"
                                            >
                                                Edit
                                            </Link>
                                        </>
                                    )}
                                    <button
                                        onClick={(e) => {
                                            e.preventDefault();
                                            if (window.confirm(`Are you sure you want to delete "${item.title}"?`)) {
                                                props.onDelete && props.onDelete(item.uuid);
                                            }
                                        }}
                                        className="text-xs bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded-md transition-colors duration-200 font-medium"
                                    >
                                        Delete
                                    </button>
                                </div>
                            )}
                  </div>
                </m.div>
              </li>
            )
          })
        }
      </ul>
      {/* Grid Start */}

      {/* Pagination Start */}
      {
        props.pagination === true && (
          <div className="flex justify-center mt-[7.5rem] md:mt-20">
            <Pagination />
          </div>)
      }
      {/* Pagination Emd */}
    </div>
  )
}

BlogWidget.defaultProps = {
  filter: false,
  data: blogWidgetData,
  link: "/posts/",
  showActions: true,
}

BlogWidget.propTypes = {
  pagination: PropTypes.bool,
  title: PropTypes.string,
  grid: PropTypes.string,
  link: PropTypes.string,
  onPublish: PropTypes.func,
  onDelete: PropTypes.func,
  showActions: PropTypes.bool,
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
}

export default memo(BlogWidget)