import React, { useState, memo } from 'react'
import PropTypes from 'prop-types'

// Libraries
import { Form, Formik } from "formik"
import { Col, Container, Row } from "react-bootstrap"
import { Link } from "react-router-dom"
import { m, AnimatePresence } from 'framer-motion'
import { Link as ScrollTo } from "react-scroll"

// Components
import { CommentFormSchema } from "../../Form/FormSchema"
import { Input } from '../../Form/Form'
import Buttons from '../../Button/Buttons'
import MessageBox from "../../MessageBox/MessageBox"
import { fadeIn } from '../../../Functions/GlobalAnimations'

// API Hooks
import { useComments, useCreateComment, useCommentLike, useAuth } from '../../../api'

// Utils
import { formatDate } from '../../../utils/dateUtils'

const CommentBox = ({ postUuid, postData }) => {
    const [replyingTo, setReplyingTo] = useState(null)
    const { user, isAuthenticated } = useAuth()
    
    // Fetch comments for this post
    const { comments, loading: commentsLoading, error: commentsError, totalComments, refreshComments } = useComments(postUuid)
    
    // Comment creation hook
    const { createNewComment, loading: creatingComment, error: createError } = useCreateComment()
    
    // Comment like hook
    const { toggleLike, loading: likingComment } = useCommentLike()

    // Handle comment submission
    const handleCommentSubmit = async (values, actions) => {
        if (!isAuthenticated) {
            actions.setStatus({ type: 'error', message: 'Please log in to comment.' })
            return
        }

        try {
            const commentData = {
                post_uuid: postUuid,
                content: values.comment,
                parent_id: replyingTo
            }

            await createNewComment(commentData)
            
            // Reset form and state
            actions.resetForm()
            setReplyingTo(null)
            refreshComments()
            
            actions.setStatus({ type: 'success', message: 'Comment posted successfully! It will be visible after admin approval.' })
        } catch (error) {
            actions.setStatus({ type: 'error', message: createError || 'Failed to post comment' })
        }
    }

    // Handle comment like
    const handleCommentLike = async (commentUuid) => {
        if (!isAuthenticated) {
            return
        }

        try {
            await toggleLike(commentUuid)
            refreshComments() // Refresh to get updated like counts
        } catch (error) {
            console.error('Failed to toggle like:', error)
        }
    }

    // Handle reply
    const handleReply = (commentUuid, authorName) => {
        setReplyingTo(commentUuid)
        // Scroll to comment form
        document.getElementById('comments')?.scrollIntoView({ behavior: 'smooth' })
    }

    // Render individual comment
    const renderComment = (comment, isChild = false) => {
        const hasReplies = comment.replies && comment.replies.length > 0
        const isLikedByUser = comment.liked_by?.some(user_like => user_like.uuid === user?.uuid)

        return (
            <li key={comment.uuid} className={isChild ? "mt-[60px]" : ""}>
                <div className={`flex w-full md:items-start sm:block ${isChild && comment.is_highlighted ? 'bg-lightgray rounded-[5px] p-[40px] md:p-[30px] sm:p-[20px]' : ''}`}>
                    <div className="inline-block w-[75px] sm:w-[50px] sm:mb-[10px]">
                        <img 
                            height="75" 
                            width="75" 
                            src={comment.author?.profile_picture || "https://via.placeholder.com/125x125"} 
                            className="rounded-full w-[95%] sm:w-full" 
                            alt={comment.author?.full_name || 'User'} 
                        />
                    </div>
                    <div className="w-full pl-[25px] sm:pl-0">
                        <div className="flex items-center justify-between flex-wrap mb-[10px]">
                            <div className="flex items-center gap-[10px] flex-wrap">
                                <Link 
                                    aria-label="author" 
                                    to={`/blogs/author/${comment.author?.uuid}`} 
                                    className="text-darkgray font-serif font-medium text-md hover:text-fastblue"
                                >
                                    {comment.author?.full_name || comment.author?.username || 'Anonymous'}
                                </Link>
                                
                                {/* Comment Status Badge */}
                                {!comment.is_approved && (
                                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                                        <i className="fas fa-clock mr-1 text-xs"></i>
                                        Pending Review
                                    </span>
                                )}
                                
                                {isAuthenticated && comment.is_approved && (
                                    <button
                                        onClick={() => handleReply(comment.uuid, comment.author?.full_name)}
                                        className="btn-reply py-[7px] px-[16px] text-spanishgray uppercase hover:text-fastblue transition-colors"
                                    >
                                        Reply
                                    </button>
                                )}
                            </div>
                            
                            {/* Like button */}
                            {isAuthenticated && (
                                <button
                                    onClick={() => handleCommentLike(comment.uuid)}
                                    disabled={likingComment}
                                    className={`flex items-center gap-1 px-2 py-1 rounded hover:bg-gray-100 transition-colors ${isLikedByUser ? 'text-red-500' : 'text-gray-500'}`}
                                >
                                    <svg className="w-4 h-4" fill={isLikedByUser ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                                    </svg>
                                    <span className="text-sm">{comment.like_count || 0}</span>
                                </button>
                            )}
                        </div>
                        
                        <div className="text-md text-spanishgray mb-[15px]">
                            {formatDate(comment.created_at)}
                        </div>
                        
                        <div className="w-[85%] prose prose-sm max-w-none">
                            <p>{comment.content}</p>
                        </div>
                    </div>
                </div>
                
                {/* Render replies */}
                {hasReplies && (
                    <ul className="child-comment ml-[70px]">
                        {comment.replies.map(reply => renderComment(reply, true))}
                    </ul>
                )}
            </li>
        )
    }

    return (
        <>
            {/* Comments List Section */}
            <m.section {...fadeIn} className="py-[130px] overflow-hidden lg:py-[90px] md:py-[75px] sm:py-[50px]">
                <Container>
                    <Row className="justify-center">
                        <Col md={6} className="text-center mb-20">
                            <h6 className="font-serif text-darkgray font-medium">
                                {commentsLoading ? 'Loading comments...' : `${totalComments || 0} Comment${totalComments !== 1 ? 's' : ''}`}
                            </h6>
                        </Col>
                    </Row>
                    <Row>
                        <Col lg={9} className="mx-auto">
                            {commentsError && (
                                <div className="text-center mb-8">
                                    <MessageBox 
                                        theme="message-box01" 
                                        variant="error" 
                                        message={`Error loading comments: ${commentsError}`} 
                                    />
                                </div>
                            )}
                            
                            {commentsLoading ? (
                                <div className="text-center py-12">
                                    <div className="inline-block w-6 h-6 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin"></div>
                                    <p className="mt-4 text-gray-500">Loading comments...</p>
                                </div>
                            ) : comments.length > 0 ? (
                                <ul className="blog-comment">
                                    {comments.map(comment => renderComment(comment))}
                                </ul>
                            ) : (
                                <div className="text-center py-12">
                                    <p className="text-gray-500 text-lg">No comments yet. Be the first to comment!</p>
                                </div>
                            )}
                        </Col>
                    </Row>
                </Container>
            </m.section>

            {/* Comment Form Section */}
            <m.section {...fadeIn} id="comments" className="pt-0 py-[130px] lg:py-[90px] md:py-[75px] sm:py-[50px] overflow-hidden">
                <Container>
                    <Row className="justify-center">
                        <Col lg={9} className="mb-16 sm:mb-8">
                            <h6 className="font-serif text-darkgray font-medium mb-[5px]">
                                {replyingTo ? 'Write a reply' : 'Write a comment'}
                            </h6>
                            {replyingTo && (
                                <div className="mb-4 p-3 bg-blue-50 rounded border-l-4 border-blue-400">
                                    <p className="text-sm text-blue-700">
                                        Replying to comment. 
                                        <button 
                                            onClick={() => setReplyingTo(null)}
                                            className="ml-2 text-blue-600 hover:text-blue-800 underline"
                                        >
                                            Cancel reply
                                        </button>
                                    </p>
                                </div>
                            )}
                            {!isAuthenticated ? (
                                <div className="mb-[5px] p-4 bg-yellow-50 border border-yellow-200 rounded">
                                    <p className="text-yellow-800">
                                        You must be <Link to="/login" className="text-blue-600 hover:underline">logged in</Link> to post a comment.
                                    </p>
                                </div>
                            ) : (
                                <div className="mb-[5px]">
                                    Your email address will not be published. Required fields are marked <span className="text-[#fb4f58]">*</span>
                                </div>
                            )}
                        </Col>
                    </Row>
                    
                    {isAuthenticated && (
                        <Row className="justify-center">
                            <Col lg={9}>
                                <Formik
                                    initialValues={{ comment: '' }}
                                    validationSchema={CommentFormSchema}
                                    onSubmit={handleCommentSubmit}
                                >
                                    {({ isSubmitting, status, values, setFieldValue }) => (
                                        <Form className="row mb-[30px]">
                                            <Col md={12} sm={12} xs={12}>
                                                <label className="mb-[15px]">Your comment <span className="text-red-500">*</span></label>
                                                <textarea 
                                                    className="mb-[2.5rem] rounded-[4px] py-[15px] px-[20px] h-[120px] w-full bg-transparent border border-[#dfdfdf] text-md resize-none" 
                                                    rows="6" 
                                                    name="comment" 
                                                    value={values.comment}
                                                    onChange={(e) => setFieldValue('comment', e.target.value)}
                                                    placeholder="Enter your comment"
                                                    required
                                                />
                                            </Col>
                                            <Col>
                                                <Buttons 
                                                    type="submit" 
                                                    className={`tracking-[0.5px] btn-fill rounded-[2px] font-medium uppercase${isSubmitting || creatingComment ? " loading" : ""}`} 
                                                    themeColor="#232323" 
                                                    size="md" 
                                                    color="#fff" 
                                                    title={replyingTo ? "Post reply" : "Post comment"}
                                                    disabled={isSubmitting || creatingComment || !values.comment.trim()}
                                                />
                                            </Col>
                                            <AnimatePresence>
                                                {status && (
                                                    <m.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                                                        <MessageBox 
                                                            className="mt-[20px] py-[10px]" 
                                                            theme="message-box01" 
                                                            variant={status.type === 'success' ? 'success' : 'error'} 
                                                            message={status.message} 
                                                        />
                                                    </m.div>
                                                )}
                                            </AnimatePresence>
                                        </Form>
                                    )}
                                </Formik>
                            </Col>
                        </Row>
                    )}
                </Container>
            </m.section>
        </>
    )
}

CommentBox.defaultProps = {
    postUuid: null,
    postData: null,
}

CommentBox.propTypes = {
    postUuid: PropTypes.string.isRequired,
    postData: PropTypes.object,
}

export default memo(CommentBox)