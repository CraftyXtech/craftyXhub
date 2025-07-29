import React, { useState, useEffect } from "react";
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
  DataTableHead,
  DataTableBody,
  DataTableRow,
  DataTableItem,
  PaginationComponent,
} from "@/components/Component";
import { Card, DropdownItem, UncontrolledDropdown, DropdownMenu, DropdownToggle, Badge } from "reactstrap";
import { useGetPosts, useDeletePost, useTogglePostLike, useGetCategories, useGetTags, usePublishPost, useUnpublishPost, useFeaturePost } from "@/api/postService";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

const PostList = () => {
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState(1);
  const [itemPerPage] = useState(10);
  const [searchText, setSearchText] = useState("");
  const [filters, setFilters] = useState({
    published: false, // false = show all posts (drafts + published), true = published only
    category_id: null,
    tag_id: null,
  });
  const [sm, updateSm] = useState(false);
  const [selectedPosts, setSelectedPosts] = useState([]);

  // Auto-refresh when component mounts (useful when navigating back from post creation)
  useEffect(() => {
    console.log('[DEBUG] PostList component mounted, refreshing posts...');
  }, []);

  // API hooks
  const apiParams = {
    skip: (currentPage - 1) * itemPerPage,
    limit: itemPerPage,
    ...filters,
  };
  
  console.log('[DEBUG] PostList API params:', apiParams);
  
  const { posts, total, loading, error, refetch } = useGetPosts(apiParams);
  const { categories } = useGetCategories();
  const { tags } = useGetTags();
  const { deletePost, loading: deleteLoading } = useDeletePost();
  const { toggleLike } = useTogglePostLike();
  const { publishPost } = usePublishPost();
  const { unpublishPost } = useUnpublishPost();
  const { featurePost } = useFeaturePost();

  // Debug posts data
  useEffect(() => {
    console.log('[DEBUG] PostList received:', { 
      posts: posts, 
      total, 
      postsCount: posts?.length,
      loading, 
      error 
    });
  }, [posts, total, loading, error]);

  // Handle search
  const onFilterChange = (e) => {
    setSearchText(e.target.value);
    setCurrentPage(1);
  };

  // Handle filter changes
  const onFilterUpdate = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
    setCurrentPage(1);
  };

  // Handle post selection
  const onSelectChange = (e, uuid) => {
    let newSelection = [...selectedPosts];
    if (e.target.checked) {
      newSelection.push(uuid);
    } else {
      newSelection = newSelection.filter(item => item !== uuid);
    }
    setSelectedPosts(newSelection);
  };

  // Handle select all
  const onSelectAllChange = (e) => {
    if (e.target.checked) {
      setSelectedPosts(posts.map(post => post.uuid)); // Use UUID instead of integer ID
    } else {
      setSelectedPosts([]);
    }
  };

  // Handle delete post
  const handleDeletePost = async (postUuid) => {
    console.log('[DEBUG] Delete post:', { postUuid });
    if (window.confirm("Are you sure you want to delete this post?")) {
      try {
        await deletePost(postUuid); // Use UUID instead of integer ID
        toast.success("Post deleted successfully");
        refetch();
      } catch (error) {
        console.error('[DEBUG] Delete error:', error);
        toast.error("Failed to delete post");
      }
    }
  };

  // Handle bulk delete
  const handleBulkDelete = async () => {
    if (selectedPosts.length === 0) return;
    
    if (window.confirm(`Are you sure you want to delete ${selectedPosts.length} posts?`)) {
      try {
        await Promise.all(selectedPosts.map(uuid => deletePost(uuid))); // Use UUID instead of integer ID
        toast.success(`${selectedPosts.length} posts deleted successfully`);
        setSelectedPosts([]);
        refetch();
      } catch (error) {
        console.error('[DEBUG] Bulk delete error:', error);
        toast.error("Failed to delete posts");
      }
    }
  };

  // Handle like toggle
  const handleLikeToggle = async (postUuid) => {
    try {
      await toggleLike(postUuid); // Use UUID instead of integer ID
      refetch();
    } catch (error) {
      console.error('[DEBUG] Like toggle error:', error);
      toast.error("Failed to toggle like");
    }
  };

  // Handle publish post
  const handlePublishPost = async (postUuid) => {
    try {
      await publishPost(postUuid);
      toast.success("Post published successfully");
      refetch();
    } catch (error) {
      console.error('[DEBUG] Publish error:', error);
      toast.error("Failed to publish post");
    }
  };

  // Handle unpublish post
  const handleUnpublishPost = async (postUuid) => {
    try {
      await unpublishPost(postUuid);
      toast.success("Post unpublished successfully");
      refetch();
    } catch (error) {
      console.error('[DEBUG] Unpublish error:', error);
      toast.error("Failed to unpublish post");
    }
  };

  // Handle feature toggle
  const handleFeatureToggle = async (postUuid, currentlyFeatured) => {
    try {
      await featurePost(postUuid, !currentlyFeatured);
      toast.success(currentlyFeatured ? "Post unfeatured successfully" : "Post featured successfully");
      refetch();
    } catch (error) {
      console.error('[DEBUG] Feature toggle error:', error);
      toast.error("Failed to update featured status");
    }
  };

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  // Get status badge
  const getStatusBadge = (isPublished) => {
    return isPublished ? (
      <Badge color="success">Published</Badge>
    ) : (
      <Badge color="warning">Draft</Badge>
    );
  };

  // Change page
  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  // Calculate pagination
  const totalPages = Math.ceil(total / itemPerPage);

  // Handle create post
  const handleCreatePost = () => {
    navigate('/posts-create');
  };

  // Handle edit post
  const handleEditPost = (post) => {
    console.log('[DEBUG] Edit post:', { id: post.id, uuid: post.uuid });
    navigate(`/posts-edit/${post.uuid}`); // Use UUID instead of integer ID
  };

  // Handle view post
  const handleViewPost = (post) => {
    console.log('[DEBUG] View post:', { id: post.id, uuid: post.uuid });
    navigate(`/posts-detail?id=${post.uuid}`); // Use UUID instead of integer ID
  };

  if (loading) {
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

  if (error) {
    return (
      <Content>
        <div className="alert alert-danger" role="alert">
          Error loading posts: {error}
        </div>
      </Content>
    );
  }

  return (
    <>
      <Head title="Posts Management" />
      <Content>
        <BlockHead size="sm">
          <BlockBetween>
            <BlockHeadContent>
              <BlockTitle>Posts</BlockTitle>
              <BlockDes className="text-soft">
                <p>You have total {total} posts.</p>
              </BlockDes>
            </BlockHeadContent>
            <BlockHeadContent>
              <div className="toggle-wrap nk-block-tools-toggle">
                <Button
                  className="btn-icon btn-trigger toggle-expand me-n1"
                  onClick={() => updateSm(!sm)}
                >
                  <Icon name="more-v" />
                </Button>
                <div className="toggle-expand-content" style={{ display: sm ? "block" : "none" }}>
                  <ul className="nk-block-tools g-3">
                    <li>
                      <div className="form-control-wrap">
                        <div className="form-icon form-icon-right">
                          <Icon name="search" />
                        </div>
                        <input
                          type="text"
                          className="form-control"
                          placeholder="Search posts..."
                          value={searchText}
                          onChange={onFilterChange}
                        />
                      </div>
                    </li>
                    <li>
                      <UncontrolledDropdown>
                        <DropdownToggle
                          color="transparent"
                          className="dropdown-toggle dropdown-indicator btn btn-outline-light btn-white"
                        >
                          Status
                        </DropdownToggle>
                        <DropdownMenu end>
                          <ul className="link-list-opt no-bdr">
                            <li>
                              <DropdownItem
                                onClick={() => onFilterUpdate('published', false)}
                              >
                                <span>Drafts</span>
                              </DropdownItem>
                            </li>
                            <li>
                              <DropdownItem
                                onClick={() => onFilterUpdate('published', true)}
                              >
                                <span>Published Only</span>
                              </DropdownItem>
                            </li>
                          </ul>
                        </DropdownMenu>
                      </UncontrolledDropdown>
                    </li>
                    <li>
                      <UncontrolledDropdown>
                        <DropdownToggle
                          color="transparent"
                          className="dropdown-toggle dropdown-indicator btn btn-outline-light btn-white"
                        >
                          Category
                        </DropdownToggle>
                        <DropdownMenu end>
                          <ul className="link-list-opt no-bdr">
                            <li>
                              <DropdownItem
                                onClick={() => onFilterUpdate('category_id', null)}
                              >
                                <span>All Categories</span>
                              </DropdownItem>
                            </li>
                            {categories.map((category) => (
                              <li key={category.id}>
                                <DropdownItem
                                  onClick={() => onFilterUpdate('category_id', category.id)}
                                >
                                  <span>{category.name}</span>
                                </DropdownItem>
                              </li>
                            ))}
                          </ul>
                        </DropdownMenu>
                      </UncontrolledDropdown>
                    </li>
                    <li className="nk-block-tools-opt">
                      <Button color="primary" onClick={handleCreatePost}>
                        <Icon name="plus" />
                        <span>Add Post</span>
                      </Button>
                    </li>
                  </ul>
                </div>
              </div>
            </BlockHeadContent>
          </BlockBetween>
        </BlockHead>

        <Block>
          <Card>
            <div className="card-inner-group">
              <div className="card-inner position-relative card-tools-toggle">
                <div className="card-title-group">
                  <div className="card-tools">
                    <div className="form-inline flex-nowrap gx-3">
                      <div className="form-wrap w-150px">
                        <select
                          className="form-select"
                          value={itemPerPage}
                          onChange={(e) => setItemPerPage(parseInt(e.target.value))}
                        >
                          <option value={10}>10 per page</option>
                          <option value={25}>25 per page</option>
                          <option value={50}>50 per page</option>
                        </select>
                      </div>
                      {selectedPosts.length > 0 && (
                        <div className="form-wrap">
                          <Button color="danger" size="sm" onClick={handleBulkDelete}>
                            <Icon name="trash" />
                            Delete Selected ({selectedPosts.length})
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
              <div className="card-inner p-0">
                <DataTableBody>
                  <DataTableHead>
                    <DataTableRow className="nk-tb-col-check">
                      <div className="custom-control custom-control-sm custom-checkbox notext">
                        <input
                          type="checkbox"
                          className="custom-control-input"
                          onChange={onSelectAllChange}
                          id="uid_all"
                          checked={selectedPosts.length === posts.length && posts.length > 0}
                        />
                        <label className="custom-control-label" htmlFor="uid_all"></label>
                      </div>
                    </DataTableRow>
                    <DataTableRow>
                      <span className="sub-text">Title</span>
                    </DataTableRow>
                    <DataTableRow size="sm">
                      <span className="sub-text">Author</span>
                    </DataTableRow>
                    <DataTableRow size="sm">
                      <span className="sub-text">Category</span>
                    </DataTableRow>
                    <DataTableRow size="sm">
                      <span className="sub-text">Status</span>
                    </DataTableRow>
                    <DataTableRow size="sm">
                      <span className="sub-text">Views</span>
                    </DataTableRow>
                    <DataTableRow size="sm">
                      <span className="sub-text">Likes</span>
                    </DataTableRow>
                    <DataTableRow size="sm">
                      <span className="sub-text">Created</span>
                    </DataTableRow>
                    <DataTableRow className="nk-tb-col-tools text-end">
                      <span className="sub-text">Action</span>
                    </DataTableRow>
                  </DataTableHead>
                  {posts.length > 0 ? (
                    posts.map((post) => (
                                              <DataTableItem key={post.uuid}>
                        <DataTableRow className="nk-tb-col-check">
                          <div className="custom-control custom-control-sm custom-checkbox notext">
                            <input
                              type="checkbox"
                              className="custom-control-input"
                              checked={selectedPosts.includes(post.uuid)}
                              onChange={(e) => onSelectChange(e, post.uuid)}
                              id={`post_${post.uuid}`}
                            />
                            <label className="custom-control-label" htmlFor={`post_${post.uuid}`}></label>
                          </div>
                        </DataTableRow>
                        <DataTableRow>
                          <div className="tb-product">
                            <div className="tb-product-info">
                              <span className="title">{post.title}</span>
                              {post.excerpt && (
                                <span className="sub-text text-muted">{post.excerpt.substring(0, 100)}...</span>
                              )}
                            </div>
                          </div>
                        </DataTableRow>
                        <DataTableRow size="sm">
                          <span className="tb-sub">{post.author.username}</span>
                        </DataTableRow>
                        <DataTableRow size="sm">
                          <span className="tb-sub">
                            {post.category ? post.category.name : "Uncategorized"}
                          </span>
                        </DataTableRow>
                        <DataTableRow size="sm">
                          {getStatusBadge(post.is_published)}
                        </DataTableRow>
                        <DataTableRow size="sm">
                          <span className="tb-sub">{post.view_count}</span>
                        </DataTableRow>
                        <DataTableRow size="sm">
                          <div className="tb-sub">
                            <Button
                              size="sm"
                              color={post.is_liked ? "danger" : "light"}
                              onClick={() => handleLikeToggle(post.uuid)}
                            >
                              <Icon name="heart" />
                              {post.like_count}
                            </Button>
                          </div>
                        </DataTableRow>
                        <DataTableRow size="sm">
                          <span className="tb-sub">{formatDate(post.created_at)}</span>
                        </DataTableRow>
                        <DataTableRow className="nk-tb-col-tools">
                          <ul className="nk-tb-actions gx-1 my-n1">
                            <li className="me-n1">
                              <UncontrolledDropdown>
                                <DropdownToggle
                                  tag="a"
                                  href="#more"
                                  onClick={(ev) => ev.preventDefault()}
                                  className="dropdown-toggle btn btn-icon btn-trigger"
                                >
                                  <Icon name="more-h" />
                                </DropdownToggle>
                                <DropdownMenu end>
                                  <ul className="link-list-opt no-bdr">
                                    <li>
                                      <DropdownItem
                                        tag="a"
                                        href="#view"
                                        onClick={(ev) => {
                                          ev.preventDefault();
                                          handleViewPost(post);
                                        }}
                                      >
                                        <Icon name="eye" />
                                        <span>View Details</span>
                                      </DropdownItem>
                                    </li>
                                    <li>
                                      <DropdownItem
                                        tag="a"
                                        href="#edit"
                                        onClick={(ev) => {
                                          ev.preventDefault();
                                          handleEditPost(post);
                                        }}
                                      >
                                        <Icon name="edit" />
                                        <span>Edit Post</span>
                                      </DropdownItem>
                                    </li>
                                    <li>
                                      <DropdownItem
                                        tag="a"
                                        href="#publish"
                                        onClick={(ev) => {
                                          ev.preventDefault();
                                          if (post.is_published) {
                                            handleUnpublishPost(post.uuid);
                                          } else {
                                            handlePublishPost(post.uuid);
                                          }
                                        }}
                                      >
                                        <Icon name={post.is_published ? "eye-off" : "eye"} />
                                        <span>{post.is_published ? "Unpublish" : "Publish"}</span>
                                      </DropdownItem>
                                    </li>
                                    <li>
                                      <DropdownItem
                                        tag="a"
                                        href="#feature"
                                        onClick={(ev) => {
                                          ev.preventDefault();
                                          handleFeatureToggle(post.uuid, post.is_featured);
                                        }}
                                      >
                                        <Icon name={post.is_featured ? "star-fill" : "star"} />
                                        <span>{post.is_featured ? "Unfeature" : "Feature"}</span>
                                      </DropdownItem>
                                    </li>
                                    <li>
                                      <DropdownItem
                                        tag="a"
                                        href="#delete"
                                        onClick={(ev) => {
                                          ev.preventDefault();
                                          handleDeletePost(post.uuid);
                                        }}
                                      >
                                        <Icon name="trash" />
                                        <span>Delete Post</span>
                                      </DropdownItem>
                                    </li>
                                  </ul>
                                </DropdownMenu>
                              </UncontrolledDropdown>
                            </li>
                          </ul>
                        </DataTableRow>
                      </DataTableItem>
                    ))
                  ) : (
                    <div className="text-center py-4">
                      <Icon name="inbox" className="mb-2" style={{ fontSize: "2rem" }} />
                      <p>No posts found</p>
                    </div>
                  )}
                </DataTableBody>
              </div>
              <div className="card-inner">
                <div className="nk-block-between-md g-3">
                  <div className="g">
                    <PaginationComponent
                      itemPerPage={itemPerPage}
                      totalItems={total}
                      paginate={paginate}
                      currentPage={currentPage}
                    />
                  </div>
                  <div className="g">
                    <div className="pagination-goto d-flex justify-content-center justify-content-md-start gx-3">
                      <div>Page</div>
                      <div>
                        <select
                          className="form-select"
                          value={currentPage}
                          onChange={(e) => setCurrentPage(parseInt(e.target.value))}
                        >
                          {[...Array(totalPages)].map((_, i) => (
                            <option key={i + 1} value={i + 1}>
                              {i + 1}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div>of {totalPages}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </Block>


      </Content>
    </>
  );
};

export default PostList; 