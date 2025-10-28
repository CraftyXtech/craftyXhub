import React from 'react'
import { Link } from 'react-router-dom'
import { PropTypes } from "prop-types";
import { m } from "framer-motion";
import { fadeIn } from '../../../Functions/GlobalAnimations';
import Buttons from '../../Button/Buttons'

const AuthorBox = ({ authorData, className }) => {
    if (!authorData) return null;

    const authorImage = authorData.img || authorData.profile_picture || "https://via.placeholder.com/110x110";
    const authorName = authorData.full_name || authorData.name || authorData.username || "Unknown Author";
    const authorRole = authorData.role || authorData.designation || "Author";
    const authorBio = authorData.bio || authorData.description || "No bio available.";
    const authorLink = authorData.uuid || authorData.id;

    return (
        <m.div {...fadeIn} className={`flex justify-center items-center w-full shadow-[0_0_15px_rgba(0,0,0,0.1)] rounded-[5px] p-16 sm:block${className ? ` ${className}` : ""}`}>
            <div className="w-[130px] mr-[60px] sm:mx-auto text-center">
                <img width="" height="" src={authorImage} className="rounded-full w-[110px] mx-auto" alt={authorName} />
                <Link aria-label="link" to={`/blogs/author/${authorLink}`} className="text-darkgray font-serif font-medium mt-[20px] block text-md hover:text-fastblue">{authorName}</Link>
                <span className="text-medium block leading-[18px] sm:mb-[25px]">{authorRole}</span>
            </div>
            <div className="w-[75%] md:text-start sm:w-full sm:text-center">
                <p className="mb-[25px]">{authorBio}</p>
                <Buttons ariaLabel="authorbox" to={`/blogs/author/${authorLink}`} className="font-medium font-serif after:h-[2px] after:bg-black hover:text-black uppercase btn-link md:mb-[15px]" size="md" color="#232323" title="All author posts" />
            </div>
        </m.div>
    )
}

AuthorBox.propTypes = {
    authorData: PropTypes.object,
    className: PropTypes.string,
};

export default AuthorBox