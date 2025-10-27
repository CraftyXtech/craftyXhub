import React, { useEffect, useState, useRef } from "react";

// Libraries
import { Link } from "react-router-dom";
import { PropTypes } from "prop-types";
import { m } from "framer-motion";

// Data
import { blogData } from "./BlogData";

// Filter the blog data category wise
const blogCategoryData = blogData.filter((item) => item.blogType === "category");

const BlogCategory = (props) => {
    const style = { "--overlay-color": typeof (props.overlay) === "object" ? `linear-gradient(to right top, ${props.overlay.map((item) => item)})` : props.overlay }
    const blogWrapper = useRef();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        import("../../Functions/Utilities").then(module => {
            const grid = module.initializeIsotop(blogWrapper.current)
            grid.on('arrangeComplete', () => setLoading(false));
        })
    })


    return (
        <div className="grid-wrapper">
            <ul ref={blogWrapper} className={`grid-container ${props.grid ? ` ${props.grid}` : ""}${loading ? " loading" : ""}`} >
                <li className="grid-sizer"></li>
                {props.data.map((item, i) => {
                    return (
                        <li key={i} className={`grid-item ${item.name || item.category || ''}`} >
                            <m.div className="blog-category xs:block" style={style}
                                initial={{ opacity: 0 }}
                                whileInView={!loading && { opacity: 1 }}
                                viewport={{ once: true }}
                                transition={{ duration: 0.6, ease: "easeOut" }} >
                                <Link aria-label="link" to={`/blogs/category/${item.slug || (item.name || item.category || '').toLowerCase().split(" ").join("-")}`}>
                                    <div className="blog-post relative overflow-hidden">
                                        <div className="blog-image bg-darkgray">
                                            <img height={341} width={444} src={item.img || 'https://via.placeholder.com/444x341'} alt="blog-category" />
                                        </div>
                                        <div className="bg-darkgray font-serif text-sm font-medium py-2 px-[22px] uppercase text-[#fff] absolute bottom-[45px] left-1/2 -translate-x-1/2 inline-flex justify-center">{item.name || item.category}</div>
                                    </div>
                                </Link>
                            </m.div>
                        </li>
                    );
                })}
            </ul>
        </div>
    );
};

BlogCategory.defaultProps = {
    data: blogCategoryData,
    link: "/blog-types/blog-standard-post/"
};

BlogCategory.propTypes = {
    grid: PropTypes.string,
    link: PropTypes.string,
    data: PropTypes.arrayOf(
        PropTypes.shape({
            id: PropTypes.number,
            name: PropTypes.string,
            slug: PropTypes.string,
            description: PropTypes.string,
            img: PropTypes.string,
            created_at: PropTypes.string,
            post_count: PropTypes.number,
            // Legacy fields for backward compatibility
            category: PropTypes.string,
            tags: PropTypes.array,
            blogType: PropTypes.string,
            title: PropTypes.string,
            content: PropTypes.string,
            author: PropTypes.number,
            likes: PropTypes.number,
            comments: PropTypes.number,
            date: PropTypes.string
        })
    ),
};

export default BlogCategory;
