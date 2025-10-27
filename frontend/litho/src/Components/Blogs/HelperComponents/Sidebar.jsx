import React, { memo } from 'react'

// Libraries
import { Form, Formik } from 'formik';
import * as Yup from 'yup';
import { Link, useNavigate } from 'react-router-dom';
import { m } from 'framer-motion'

// Components
import StaticInstagram from '../../Instagram/StaticInstagram';
import SocialIcons from '../../SocialIcon/SocialIcons';
import { Input } from '../../Form/Form'

// API Hooks
import { useCategories, useTags, useRecentPosts } from '../../../api';

// Data (for fallback only)
import { fadeIn } from "../../../Functions/GlobalAnimations";
import { getImageUrl } from '../../../api';

const SocialIconsData = [
    {
        color: "#3b5998",
        link: "https://www.facebook.com/",
        icon: "fab fa-facebook-f"
    },
    {
        color: "#ea4c89",
        link: "https://dribbble.com/",
        icon: "fab fa-dribbble"
    },
    {
        color: "#00aced",
        link: "https://twitter.com/",
        icon: "fab fa-twitter"
    },
    {
        color: "#fe1f49",
        link: "https://www.instagram.com/",
        icon: "fab fa-instagram"
    },
    {
        color: "#0077b5",
        link: "https://www.linkedin.com/",
        icon: "fab fa-linkedin-in"
    }
]

const Sidebar = (props) => {
    const navigate = useNavigate();
    
    // API hooks for dynamic data
    const { categories, loading: categoriesLoading } = useCategories();
    const { tags, loading: tagsLoading } = useTags();
    const { posts: recentPosts, loading: recentPostsLoading } = useRecentPosts({ limit: 3 });

    // Guard against undefined data
    const postData = props.data || {};

    return (
        <aside className="col-12 col-xl-3 offset-xl-1 col-lg-4 col-md-7 md:pl-[15px]">
            <div className='inline-block w-full mb-20'>
                <span className='mb-[25px] font-medium text-darkgray text-lg font-serif block'>Search posts</span>
                <div className="relative">
                    <Formik
                        initialValues={{ search: '' }}
                        validationSchema={Yup.object().shape({ search: Yup.string().required("Field is required."), })}
                        onSubmit={async (values, actions) => {
                            await new Promise((r) => setTimeout(r, 500));
                            actions.resetForm();
                            navigate("/page/search-result", { state: { search: values } });
                        }}
                    >
                        {({ isSubmitting, status }) => (
                            <div className="relative">
                                <Form className="relative">
                                    <Input showErrorMsg={false} type="text" name="search" className="border-[1px] py-[15px] px-[20px] w-full rounded-[5px] border-solidborder-transparent" placeholder="Enter your keyword..." />
                                    <button type="submit" className={`text-xs tracking-[1px] text-fastblue py-[15px] !absolute top-[8%] right-0 px-[20px] uppercase${isSubmitting ? " loading" : ""}`}><i className="feather-search"></i></button>
                                </Form>
                            </div>
                        )}
                    </Formik>
                </div>
            </div>
            
            {/* Author Section */}
            <div className='p-[38px] mb-20 rounded-[4px] border-mediumgray border text-center'>
                {postData?.author ? (
                    // API data - author is an object
                    <>
                        <Link aria-label="link" to={`/blogs/author/${postData.author.uuid || postData.author.username}`}>
                            <img 
                                height="" 
                                width="" 
                                src={postData.author.img || "https://via.placeholder.com/100x100"} 
                                alt={postData.author.full_name || postData.author.username} 
                                className='mb-[5px] rounded-[50%] block mx-auto w-[100px]' 
                            />
                        </Link>
                        <Link 
                            aria-label="link" 
                            to={`/blogs/author/${postData.author.uuid || postData.author.username}`} 
                            className='mt-[20px] font-medium text-darkgray text-md font-serif inline-block'
                        >
                            {postData.author.full_name || postData.author.username}
                        </Link>
                        <span className='mb-[20px] leading-[18px] text-[14px] block'>
                            {postData.author.role || 'Author'}
                        </span>
                        <p className='mb-[25px]'>
                            {postData.author.bio || 'Lorem ipsum is simply dummy text of the printing and industry lorem ipsum has been standard.'}
                        </p>
                    </>
                ) : null }
                <SocialIcons theme="social-icon-style-01" size="xs" iconColor="dark" data={SocialIconsData.slice(0, 4)} />
            </div>
            
            {/* Categories Section */}
            <div className='mb-20 xs:mb-[35px]'>
                <m.span className="mb-[35px] font-medium font-serif text-darkgray text-lg block" {...fadeIn}>
                    Categories
                    {categoriesLoading && <span className="ml-2 text-sm text-gray-500">(Loading...)</span>}
                </m.span>
                <m.ul className="pl-0" {...fadeIn}>
                    {categories.length > 0 ? (
                        categories.map((category, index) => (
                            <li key={category.id || index} className='relative inline-block w-full mb-[15px] leading-[18px]'>
                                <Link 
                                    aria-label="category link" 
                                    to={`/blogs/category/${category.slug || category.name?.toLowerCase().replace(/\s+/g, '-')}`} 
                                    className='inline-block text-left'
                                >
                                    {category.name}
                                </Link>
                                <span className='text-[14px] absolute top-[1px] right-0 text-right'>
                                    {category.post_count || 0}
                                </span>
                            </li>
                        ))
                    ) : null }
                </m.ul>
            </div>
            
            {/* Recent Posts Section */}
            <div className='mb-20 xs:mb-[35px]'>
                <span className='mb-[35px] font-medium font-serif text-darkgray text-lg block'>
                    Recent posts
                    {recentPostsLoading && <span className="ml-2 text-sm text-gray-500">(Loading...)</span>}
                </span>
                <ul>
                    {recentPosts.length > 0 ? (
                        recentPosts.map((post, index) => (
                            <m.li key={post.uuid || index} className='flex mb-[45px]' {...{...fadeIn,transition:{delay:0.2 * (index + 1)}}}>
                                <figure className="h-[65px] w-[80px] m-0 shrink-0">
                                    <Link aria-label="link" to={`/posts/${post.uuid}`}>
                                        <img 
                                            height="" 
                                            width="" 
                                            src={getImageUrl(post.featured_image, "posts") || "https://via.placeholder.com/800x800"} 
                                            alt={post.title} 
                                            className='rounded-[3px]' 
                                        />
                                    </Link>
                                </figure>
                                <div className='leading-normal pl-[30px] relative top-[-3px] grow'>
                                    <Link 
                                        aria-label="link" 
                                        to={`/posts/${post.uuid}`} 
                                        className='mb-[5px] sm:mb-0 font-medium text-darkgray inline-block'
                                    >
                                        {post.title}
                                    </Link>
                                    <span className="leading-[22px] text-[14px] block">
                                        {post.excerpt || 'Lorem ipsum is simply as dummy text of the...'}
                                    </span>
                                </div>
                            </m.li>
                        ))
                    ) : null }
                </ul>
            </div>
            
            {/* Tags Cloud Section */}
            <m.div className='visible mb-20 md:w-[90%] sm:w-full' {...fadeIn}>
                <span className='mb-[35px] font-medium font-serif text-darkgray text-lg block'>
                    Tags cloud
                    {tagsLoading && <span className="ml-2 text-sm text-gray-500">(Loading...)</span>}
                </span>
                {tags.length > 0 && (
                    tags.map((tag, index) => (
                        <Link 
                            key={tag.id || index}
                            aria-label="tag" 
                            to={`/blogs/tag/${tag.slug || tag.name?.toLowerCase().replace(/\s+/g, '-')}`} 
                            className='inline-block text-center text-sm mt-0 ml-[6px] mb-[10px] mr-0 pt-[5px] px-[18px] pb-[6px] rounded-[4px] border-mediumgray border hover:text-[#828282] hover:shadow-[0_0_15px_rgba(0,0,0,0.1)]'
                        >
                            {tag.name}
                        </Link>
                    ))
                ) }
            </m.div>
            
            {/* Instagram Section */}
            <m.div {...fadeIn}>
                <span className='mb-[35px] font-medium font-serif text-darkgray text-lg block'>Instagram</span>
                <StaticInstagram />
            </m.div>
        </aside>
    )
}

export default Sidebar