import React, { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import Head from "@/layout/head/Head";
import Content from "@/layout/content/Content";
import {
  Block,
  BlockHead,
  BlockTitle,
  BlockBetween,
  BlockHeadContent,
  BlockDes,
  Icon,
  Row,
  Col,
  Button,
  PreviewCard,
} from "@/components/Component";
import { useGetPost, useDeletePost, useTogglePostLike, useImageUrl } from "@/api/postService";
import { toast } from "react-toastify";
import { Badge } from "reactstrap";

const PostDetail = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const postUuid = searchParams.get('id'); // This should be UUID from URL
  const commentId = searchParams.get('comment'); // Comment ID for scrolling
  
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  console.log('[DEBUG] PostDetail UUID from URL:', postUuid);

  // API hooks
  const { post: fetchedPost, loading: postLoading } = useGetPost(postUuid);
  const { deletePost, loading: deleteLoading } = useDeletePost();
  const { toggleLike } = useTogglePostLike();
  const { getImageUrl } = useImageUrl();



  useEffect(() => {
    if (!postUuid) {
      setError("No post UUID provided");
      setLoading(false);
      return;
    }

    if (fetchedPost) {
      console.log('[DEBUG] PostDetail received post data:', fetchedPost);
      console.log('[DEBUG] Featured image path:', fetchedPost.featured_image);
      if (fetchedPost.featured_image) {
        console.log('[DEBUG] Constructed image URL:', getImageUrl(fetchedPost.featured_image, "posts"));
      }
      setPost(fetchedPost);
      setLoading(false);
    }
  }, [postUuid, fetchedPost]);

  // Scroll to comment if comment ID is in URL
  useEffect(() => {
    if (commentId && post && !loading) {
      // Wait for DOM to render
      const timer = setTimeout(() => {
        const element = document.getElementById(`comment-${commentId}`);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' });
          element.classList.add('highlight-comment');
          // Remove highlight after 3 seconds
          setTimeout(() => {
            element.classList.remove('highlight-comment');
          }, 3000);
        }
      }, 500);
      
      return () => clearTimeout(timer);
    }
  }, [commentId, post, loading]);

  // Handle delete post
  const handleDeletePost = async () => {
    if (window.confirm("Are you sure you want to delete this post?")) {
      try {
        console.log('[DEBUG] Deleting post with UUID:', postUuid);
        await deletePost(postUuid); // Use UUID instead of postId
        toast.success("Post deleted successfully");
        navigate('/posts-list');
      } catch (error) {
        console.error('[DEBUG] Delete post error:', error);
        toast.error("Failed to delete post");
      }
    }
  };

  const handleEditPost = () => {
    console.log('[DEBUG] Edit post with UUID:', postUuid);
    navigate(`/posts-edit/${postUuid}`); // Use UUID instead of postId
  };

  const handleLikeToggle = async () => {
    try {
      console.log('[DEBUG] Toggle like for post UUID:', postUuid);
      await toggleLike(postUuid); // Use UUID instead of postId
      window.location.reload();
    } catch (error) {
      console.error('[DEBUG] Toggle like error:', error);
      toast.error("Failed to toggle like");
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Get status badge
  const getStatusBadge = (isPublished) => {
    return isPublished ? (
      <Badge color="success">Published</Badge>
    ) : (
      <Badge color="warning">Draft</Badge>
    );
  };

  if (loading || postLoading) {
    return (
      <Content>
        <div className="d-flex justify-content-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </Content>
    );
  }

  if (error || !post) {
    return (
      <Content>
        <div className="alert alert-danger" role="alert">
          {error || "Post not found"}
        </div>
      </Content>
    );
  }

  return (
    <>
      <Head title={`Post: ${post.title}`} />
      <Content>
        <BlockHead size="sm">
          <BlockBetween>
            <BlockHeadContent>
              <BlockTitle page>Post Details</BlockTitle>
              <BlockDes className="text-soft">
                <p>Viewing post: {post.title}</p>
              </BlockDes>
            </BlockHeadContent>
            <BlockHeadContent>
              <div className="d-flex gap-2">
                <Button color="light" onClick={() => navigate('/posts-list')}>
                  <Icon name="arrow-left" className="me-1" />
                  Back to Posts
                </Button>
                <Button color="primary" onClick={handleEditPost}>
                  <Icon name="edit" className="me-1" />
                  Edit Post
                </Button>
                <Button color="danger" onClick={handleDeletePost} disabled={deleteLoading}>
                  <Icon name="trash" className="me-1" />
                  Delete
                </Button>
              </div>
            </BlockHeadContent>
          </BlockBetween>
        </BlockHead>

        <Block>
          <Row className="g-gs">
            {/* Main Content */}
            <Col xxl="8">
              <div className="gap gy-gs">
                {/* Post Header */}
                <PreviewCard className="card-bordered">
                  <div className="card-head">
                    <h3 className="card-title">{post.title}</h3>
                    <div className="d-flex align-items-center gap-3 mt-3">
                      {getStatusBadge(post.is_published)}
                      {post.is_featured && <Badge color="info">Featured</Badge>}
                    </div>
                  </div>
                  <div className="card-inner">
                    <Row className="g-4">
                      <Col sm="6">
                        <div className="d-flex align-items-center">
                          <Icon name="user" className="me-2" />
                          <span className="text-muted">Author:</span>
                          <span className="ms-2 fw-medium">{post.author?.username || 'Unknown'}</span>
                        </div>
                      </Col>
                      <Col sm="6">
                        <div className="d-flex align-items-center">
                          <Icon name="calendar" className="me-2" />
                          <span className="text-muted">Created:</span>
                          <span className="ms-2 fw-medium">{formatDate(post.created_at)}</span>
                        </div>
                      </Col>
                      <Col sm="6">
                        <div className="d-flex align-items-center">
                          <Icon name="folder" className="me-2" />
                          <span className="text-muted">Category:</span>
                          <span className="ms-2 fw-medium">{post.category?.name || 'Uncategorized'}</span>
                        </div>
                      </Col>
                      <Col sm="6">
                        <div className="d-flex align-items-center">
                          <Icon name="clock" className="me-2" />
                          <span className="text-muted">Reading Time:</span>
                          <span className="ms-2 fw-medium">{post.reading_time || 0} min</span>
                        </div>
                      </Col>
                    </Row>
                  </div>
                </PreviewCard>

                {/* Post Content */}
                <PreviewCard className="card-bordered">
                  <div className="card-head">
                    <h5 className="card-title">Content</h5>
                  </div>
                  <div className="card-inner">
                    {post.excerpt && (
                      <div className="mb-4">
                        <h6 className="text-muted mb-2">Excerpt</h6>
                        <p className="lead">{post.excerpt}</p>
                      </div>
                    )}
                    <div className="post-content">
                      <div dangerouslySetInnerHTML={{ __html: post.content }} />
                    </div>
                  </div>
                </PreviewCard>

                {/* Tags */}
                {post.tags && post.tags.length > 0 && (
                  <PreviewCard className="card-bordered">
                    <div className="card-head">
                      <h5 className="card-title">Tags</h5>
                    </div>
                    <div className="card-inner">
                      <div className="d-flex flex-wrap gap-2">
                        {post.tags.map(tag => (
                          <Badge key={tag.id} color="light" className="text-dark">
                            {tag.name}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </PreviewCard>
                )}
              </div>
            </Col>

            {/* Sidebar */}
            <Col xxl="4">
              <div className="gap gy-gs">
                {/* Featured Image */}
                {post.featured_image && (
                  <PreviewCard className="card-bordered">
                    <div className="card-head">
                      <h5 className="card-title">Featured Image</h5>
                    </div>
                    <div className="card-inner">
                      <img 
                        src={getImageUrl(post.featured_image, "posts")} 
                        alt={post.title}
                        className="img-fluid rounded"
                        style={{ maxWidth: '100%', height: 'auto' }}
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                    </div>
                  </PreviewCard>
                )}

                {/* Post Statistics */}
                <PreviewCard className="card-bordered">
                  <div className="card-head">
                    <h5 className="card-title">Statistics</h5>
                  </div>
                  <div className="card-inner">
                    <div className="d-flex justify-content-between align-items-center mb-3">
                      <span className="text-muted">Views</span>
                      <span className="fw-medium">{post.view_count || 0}</span>
                    </div>
                    <div className="d-flex justify-content-between align-items-center mb-3">
                      <span className="text-muted">Likes</span>
                      <div className="d-flex align-items-center">
                        <Button
                          size="sm"
                          color={post.is_liked ? "danger" : "light"}
                          onClick={handleLikeToggle}
                          className="me-2"
                        >
                          <Icon name="heart" />
                        </Button>
                        <span className="fw-medium">{post.like_count || 0}</span>
                      </div>
                    </div>
                    <div className="d-flex justify-content-between align-items-center mb-3">
                      <span className="text-muted">Comments</span>
                      <span className="fw-medium">{post.comment_count || 0}</span>
                    </div>
                    <div className="d-flex justify-content-between align-items-center">
                      <span className="text-muted">Word Count</span>
                      <span className="fw-medium">
                        {post.content.replace(/<[^>]*>/g, '').split(/\s+/).filter(word => word.length > 0).length}
                      </span>
                    </div>
                  </div>
                </PreviewCard>

                {/* SEO Information */}
                <PreviewCard className="card-bordered">
                  <div className="card-head">
                    <h5 className="card-title">SEO Information</h5>
                  </div>
                  <div className="card-inner">
                    {post.meta_title && (
                      <div className="mb-3">
                        <h6 className="text-muted mb-1">Meta Title</h6>
                        <p className="small">{post.meta_title}</p>
                      </div>
                    )}
                    {post.meta_description && (
                      <div className="mb-3">
                        <h6 className="text-muted mb-1">Meta Description</h6>
                        <p className="small">{post.meta_description}</p>
                      </div>
                    )}
                    <div>
                      <h6 className="text-muted mb-1">URL Slug</h6>
                      <p className="small text-muted">/posts/{post.slug}</p>
                    </div>
                  </div>
                </PreviewCard>

                {/* Last Updated */}
                <PreviewCard className="card-bordered">
                  <div className="card-head">
                    <h5 className="card-title">Timestamps</h5>
                  </div>
                  <div className="card-inner">
                    <div className="d-flex justify-content-between align-items-center mb-2">
                      <span className="text-muted">Created</span>
                      <span className="small">{formatDate(post.created_at)}</span>
                    </div>
                    {post.updated_at && post.updated_at !== post.created_at && (
                      <div className="d-flex justify-content-between align-items-center">
                        <span className="text-muted">Updated</span>
                        <span className="small">{formatDate(post.updated_at)}</span>
                      </div>
                    )}
                  </div>
                </PreviewCard>
              </div>
            </Col>
          </Row>
        </Block>
      </Content>
    </>
  );
};

export default PostDetail; 