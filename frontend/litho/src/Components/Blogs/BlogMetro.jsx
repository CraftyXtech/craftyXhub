import React, { useState, useEffect, useRef, memo } from "react";

// Libraries
import { Link } from "react-router-dom";
import { PropTypes } from "prop-types";
import { m } from "framer-motion";

// Components
import Filter from "./BlogFilter";
import Pagination from "./HelperComponents/Pagination";
import { blogData } from "./BlogData";
import { getImageUrl } from "../../api";

// Filter the blog data category wise
const blogMetroData = blogData.filter((item) => item.blogType === "metro");

const BlogMetro = (props) => {
  const blogWrapper = useRef();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    import("../../Functions/Utilities").then(module => {
      const grid = module.initializeIsotop(blogWrapper.current)
      grid.on('arrangeComplete', () => setLoading(false));
    })
  }, [])

  const style = { "--overlay-color": typeof (props.overlay) === "object" ? `linear-gradient(to right top, ${props.overlay.map((item, i) => item)})` : props.overlay }

  const handleFilterChange = () => {
    blogWrapper.current.querySelectorAll("li").forEach(item => item.childNodes[0]?.classList.add("appear"))
  }

  return (
    <div className="grid-wrapper">


      <Filter title={props.title} filterData={props.filterData} onFilterChange={handleFilterChange} />
  
      {/* Grid Start */}
      <ul ref={blogWrapper} className={`grid-container ${props.grid ? ` ${props.grid}` : ""}${loading ? " loading" : ""}${props.filter === false ? "" : " mt-28 md:mt-[4.5rem] sm:mt-8"}`} >
        <li className="grid-sizer"></li>
        {props.data.map((item, i) => {
          return (
            <li key={i} className={`grid-item${item.double_col ? " grid-item-double" : ""} ${(() => {
              let categories = Array.isArray(item.category) ? item.category : (item.category && item.category.name ? [item.category.name] : []);
              return categories.map(cat => cat.split(" ").join("")).join(" ").toLowerCase();
            })()}`} >
              <m.div className="blog-metro"
                initial={{ opacity: 0 }}
                whileInView={!loading && { opacity: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, ease: "easeOut" }} >
                <div className="blog-post-image relative overflow-hidden" style={style}>
                  <Link aria-label="link" to={`${props.link}${item.uuid || item.id}`}>
                    <img 
                      className="w-full h-[300px] object-cover" 
                      src={getImageUrl(item.featured_image) || item.img} 
                      alt={item.title} 
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent"></div>
                  </Link>
                  <div className="absolute top-4 left-4 z-10">
                    <Link 
                      aria-label="link" 
                      to={`${props.link}${item.uuid || item.id}`} 
                      className="inline-block bg-white bg-opacity-90 text-black px-3 py-1 text-xs uppercase tracking-wider font-medium hover:bg-opacity-100 transition-all duration-300"
                    > 
                      {Array.isArray(item.category) ? item.category[0] : (item.category && item.category.name ? item.category.name : 'General')}
                    </Link>
                  </div>
                  <div className="absolute bottom-4 left-4 right-4 z-10">
                    <span className="block text-white text-xs opacity-90 mb-2">
                      {new Date(item.date || item.created_at).toLocaleDateString('en-US', { 
                        day: '2-digit', 
                        month: 'long', 
                        year: 'numeric' 
                      })}
                    </span>
                    <Link 
                      aria-label="link" 
                      to={`${props.link}${item.uuid || item.id}`} 
                      className="block text-white font-semibold text-lg leading-tight hover:text-yellow-300 transition-all duration-300 cursor-pointer"
                    >
                      {item.title}
                    </Link>
                  </div>
                </div>
              </m.div>
            </li>
          );
        })}
      </ul>
      {/* Grid End */}

      {/* Pagination Start */}
      {
        props.pagination === true && (
          <div className="flex justify-center mt-[7.5rem] md:mt-20">
            <Pagination />
          </div>)
      }
      {/* Pagination End */}
    </div>
  );
};

BlogMetro.defaultProps = {
  filter: false,
  data: blogMetroData,
  link: "/posts/"
}
BlogMetro.propTypes = {
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

export default memo(BlogMetro);
