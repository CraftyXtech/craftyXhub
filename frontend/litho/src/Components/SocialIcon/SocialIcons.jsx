import React, { memo } from 'react'

// Libraries
import { m } from "framer-motion"
import { PropTypes } from "prop-types";

// Data
import { SocialIconsData01 } from './SocialIconsData'

// css
import "../../Assets/scss/components/_socialicons.scss"

const SocialIcons = ({ data, theme, size, iconColor, className, animation, animationDelay, ...props }) => {
    // Set defaults
    const actualData = data ?? SocialIconsData01
    const actualTheme = theme ?? "social-icon-style-01"
    const actualSize = size ?? "lg"
    const actualIconColor = iconColor ?? "light"
    const actualClassName = className ?? "justify-center"
    const actualAnimationDelay = animationDelay ?? 0.2
    return (
        <ul className={`social-icon flex-wrap gap-y-5 p-0 ${actualTheme} ${actualSize} ${actualIconColor} ${actualClassName}`}>
            {
                actualData.map((item, i) => {
                    return (
                        actualTheme !== "social-icon-style-11" ? (
                            <m.li key={i} style={{ "--social-icon-color": item.color ? item.color : "#000" }} {...{ ...animation, transition: { delay: i * actualAnimationDelay } }} >
                                <a href={item.link} aria-label="social icon" target="_blank" rel="noreferrer">
                                    {item.name && <span className='flex brand-label'>{item.name ? item.name : "icon"}</span>}
                                    {item.icon && <i className={`${item.icon} brand-icon`}></i>}
                                    <span></span>
                                </a>
                            </m.li>
                        ) : (
                            <m.li key={i} style={{ "--social-icon-color": item.color ? item.color : "#000" }} {...{ ...animation, transition: { delay: i * actualAnimationDelay } }} >
                                <a href={item.link} aria-label="social icon" target="_blank" rel="noreferrer">
                                    {item.socialback && <div className='social-back'><span>{item.socialback}</span></div>}
                                    <div className={`${item.position} social-front grid`}>
                                        {item.icon && <i className={item.icon}></i>}
                                        {item.name && <span>{item.name ? item.name : "icon"}</span>}
                                    </div>
                                </a>
                            </m.li>
                        )
                    )
                })
            }
        </ul>
    )
}

SocialIcons.propTypes = {
    theme: PropTypes.string,
    animationDelay: PropTypes.number,
    animation: PropTypes.object,
    size: PropTypes.string,
    iconColor: PropTypes.string,
    className: PropTypes.string,
    data: PropTypes.arrayOf(
        PropTypes.exact({
            name: PropTypes.string,
            link: PropTypes.string,
            icon: PropTypes.string,
            color: PropTypes.string,
            position: PropTypes.string,
            socialback: PropTypes.string,
        })
    ),
}

// Defaults are now handled in destructuring
SocialIcons.defaultProps = undefined;

export default memo(SocialIcons)