import React from 'react'

// Libraries
import { Form, Formik } from 'formik';
import * as Yup from 'yup';
import { m } from 'framer-motion'

// Components
import StaticInstagram from '../../Instagram/StaticInstagram';
import SocialIcons from '../../SocialIcon/SocialIcons';
import { Input } from '../../Form/Form'

// Data
import { authorData } from '../BlogData';
import { fadeIn } from "../../../Functions/GlobalAnimations";

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
    const handleSearch = (values) => {
        // Simulate search redirect behavior without react-router
        alert(`Search submitted: ${values.search}`);
    };

    const author = props.data?.[0]?.author
        ? authorData.find(author => author.id === props.data[0].author)
        : null;

    return (
        <aside className="col-12 col-xl-3 offset-xl-1 col-lg-4 col-md-7 md:pl-[15px]">
            <div className='inline-block w-full mb-20'>
                <span className='mb-[25px] font-medium text-darkgray text-lg font-serif block'>Search posts</span>
                <div className="relative">
                    <Formik
                        initialValues={{ search: '' }}
                        validationSchema={Yup.object().shape({
                            search: Yup.string().required("Field is required."),
                        })}
                        onSubmit={async (values, actions) => {
                            await new Promise((r) => setTimeout(r, 500));
                            actions.resetForm();
                            handleSearch(values);
                        }}
                    >
                        {({ isSubmitting }) => (
                            <div className="relative">
                                <Form className="relative">
                                    <Input showErrorMsg={false} type="text" name="search" className="border-[1px] py-[15px] px-[20px] w-full rounded-[5px] border-solidborder-transparent" placeholder="Enter your keyword..." />
                                    <button type="submit" className={`text-xs tracking-[1px] text-fastblue py-[15px] !absolute top-[8%] right-0 px-[20px] uppercase${isSubmitting ? " loading" : ""}`}>
                                        <i className="feather-search"></i>
                                    </button>
                                </Form>
                            </div>
                        )}
                    </Formik>
                </div>
            </div>

            {author && (
                <div className='p-[38px] mb-20 rounded-[4px] border-mediumgray border text-center'>
                    <a href="#">
                        <img src={author.img} alt={author.name} className='mb-[5px] rounded-[50%] block mx-auto w-[100px]' />
                    </a>
                    <a href="#" className='mt-[20px] font-medium text-darkgray text-md font-serif inline-block'>{author.name}</a>
                    <span className='mb-[20px] leading-[18px] text-[14px] block'>Co-founder</span>
                    <p className='mb-[25px]'>Lorem ipsum is simply dummy text of the printing and industry lorem ipsum has been standard.</p>
                    <SocialIcons theme="social-icon-style-01" size="xs" iconColor="dark" data={SocialIconsData.slice(0, 4)} />
                </div>
            )}

            <div className='mb-20 xs:mb-[35px]'>
                <m.span className="mb-[35px] font-medium font-serif text-darkgray text-lg block" {...fadeIn}>Categories</m.span>
                <m.ul className="pl-0" {...fadeIn}>
                    {["Entertainment", "Business", "Creative", "Lifestyle", "Fashion", "Design"].map((category, idx) => (
                        <li key={category} className='relative inline-block w-full mb-[15px] leading-[18px]'>
                            <a href="#" className='inline-block text-left'>{category}</a>
                            <span className='text-[14px] absolute top-[1px] right-0 text-right'>{["10", "05", "03", "02", "19", "21"][idx]}</span>
                        </li>
                    ))}
                </m.ul>
            </div>

            <div className='mb-20 xs:mb-[35px]'>
                <span className='mb-[35px] font-medium font-serif text-darkgray text-lg block'>Recent posts</span>
                <ul>
                    {[1, 2, 3].map((_, index) => (
                        <m.li key={index} className='flex mb-[45px]' {...{ ...fadeIn, transition: { delay: 0.2 * (index + 1) } }}>
                            <figure className="h-[65px] w-[80px] m-0 shrink-0">
                                <a href="#"><img src={`https://via.placeholder.com/800x800`} alt="" className='rounded-[3px]' /></a>
                            </figure>
                            <div className='leading-normal pl-[30px] relative top-[-3px] grow'>
                                <a href="#" className='mb-[5px] sm:mb-0 font-medium text-darkgray inline-block'>Post title {index + 1}</a>
                                <span className="leading-[22px] text-[14px] block">Lorem ipsum is simply as dummy text of the...</span>
                            </div>
                        </m.li>
                    ))}
                </ul>
            </div>

            <m.div className='visible mb-20 md:w-[90%] sm:w-full' {...fadeIn}>
                <span className='mb-[35px] font-medium font-serif text-darkgray text-lg block'>Tags cloud</span>
                {["Development", "Mountains", "Lifestyle", "Hotel", "Event", "Multimedia", "Fashion"].map(tag => (
                    <a key={tag} href="#" className='inline-block text-center text-sm mt-0 ml-[6px] mb-[10px] mr-0 pt-[5px] px-[18px] pb-[6px] rounded-[4px] border-mediumgray border hover:text-[#828282] hover:shadow-[0_0_15px_rgba(0,0,0,0.1)]'>{tag}</a>
                ))}
            </m.div>

            <m.div {...fadeIn}>
                <span className='mb-[35px] font-medium font-serif text-darkgray text-lg block'>Instagram</span>
                <StaticInstagram />
            </m.div>
        </aside>
    )
}

export default Sidebar;
