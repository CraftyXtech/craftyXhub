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
  BackTo,
} from "@/components/Component";
import { Card, Badge, Spinner, Alert } from "reactstrap";
import { useGetPendingComments, useApproveComment, useDeleteComment } from "@/api/commentService";
import { toast } from "react-toastify";
import Swal from "sweetalert2";

const CommentModeration = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [itemPerPage] = useState(10);
  const [searchText, setSearchText] = useState("");
  const [sm, updateSm] = useState(false);
  const [selectedComments, setSelectedComments] = useState([]);

  // API hooks
  const { comments, total, loading, error, refetch } = useGetPendingComments();
  const { approveComment, loading: approveLoading } = useApproveComment();
  const { deleteComment, loading: deleteLoading } = useDeleteComment();

  // Filter comments based on search
  const filteredComments = comments.filter(comment =>
    comment.content.toLowerCase().includes(searchText.toLowerCase()) ||
    comment.author?.full_name?.toLowerCase().includes(searchText.toLowerCase()) ||
    comment.post_title?.toLowerCase().includes(searchText.toLowerCase())
  );

  // Pagination
  const indexOfLastItem = currentPage * itemPerPage;
  const indexOfFirstItem = indexOfLastItem - itemPerPage;
  const currentItems = filteredComments.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(filteredComments.length / itemPerPage);

  // Handle search
  const onFilterChange = (e) => {
    setSearchText(e.target.value);
    setCurrentPage(1);
  };

  // Handle comment selection
  const onSelectChange = (e, uuid) => {
    let newSelection = [...selectedComments];
    if (e.target.checked) {
      newSelection.push(uuid);
    } else {
      newSelection = newSelection.filter(item => item !== uuid);
    }
    setSelectedComments(newSelection);
  };

  // Handle select all
  const onSelectAllChange = (e) => {
    if (e.target.checked) {
      setSelectedComments(currentItems.map(item => item.uuid));
    } else {
      setSelectedComments([]);
    }
  };

  // Handle approve comment
  const handleApproveComment = async (commentUuid) => {
    try {
      await approveComment(commentUuid);
      toast.success("Comment approved successfully");
      refetch();
    } catch (error) {
      toast.error("Failed to approve comment");
    }
  };

  // Handle bulk approve
  const handleBulkApprove = async () => {
    if (selectedComments.length === 0) {
      toast.warning("Please select comments to approve");
      return;
    }

    const result = await Swal.fire({
      title: 'Approve Comments?',
      text: `Are you sure you want to approve ${selectedComments.length} comment(s)?`,
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Yes, approve them!'
    });

    if (result.isConfirmed) {
      try {
        const approvePromises = selectedComments.map(uuid => approveComment(uuid));
        await Promise.all(approvePromises);
        toast.success(`${selectedComments.length} comment(s) approved successfully`);
        setSelectedComments([]);
        refetch();
      } catch (error) {
        toast.error("Failed to approve some comments");
      }
    }
  };

  // Handle delete comment
  const handleDeleteComment = async (commentUuid) => {
    const result = await Swal.fire({
      title: 'Delete Comment?',
      text: "This action cannot be undone!",
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Yes, delete it!'
    });

    if (result.isConfirmed) {
      try {
        await deleteComment(commentUuid);
        toast.success("Comment deleted successfully");
        refetch();
      } catch (error) {
        toast.error("Failed to delete comment");
      }
    }
  };

  // Handle bulk delete
  const handleBulkDelete = async () => {
    if (selectedComments.length === 0) {
      toast.warning("Please select comments to delete");
      return;
    }

    const result = await Swal.fire({
      title: 'Delete Comments?',
      text: `Are you sure you want to delete ${selectedComments.length} comment(s)? This action cannot be undone!`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Yes, delete them!'
    });

    if (result.isConfirmed) {
      try {
        const deletePromises = selectedComments.map(uuid => deleteComment(uuid));
        await Promise.all(deletePromises);
        toast.success(`${selectedComments.length} comment(s) deleted successfully`);
        setSelectedComments([]);
        refetch();
      } catch (error) {
        toast.error("Failed to delete some comments");
      }
    }
  };

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  // Truncate text
  const truncateText = (text, maxLength = 100) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  };

  return (
    <>
      <Head title="Comment Moderation" />
      <Content>
        <BlockHead size="sm">
          <BlockBetween>
            <BlockHeadContent>
              <BackTo link="/" icon="arrow-left">
                Dashboard
              </BackTo>
              <BlockTitle page>Comment Moderation</BlockTitle>
              <BlockDes className="text-soft">
                Review and approve pending comments from users
              </BlockDes>
            </BlockHeadContent>
            <BlockHeadContent>
              <div className="toggle-wrap nk-block-tools-toggle">
                <Button
                  className={`btn-icon btn-trigger toggle-expand me-n1 ${sm ? "active" : ""}`}
                  onClick={() => updateSm(!sm)}
                >
                  <Icon name="menu-alt-r"></Icon>
                </Button>
                <div className="toggle-expand-content" style={{ display: sm ? "block" : "none" }}>
                  <ul className="nk-block-tools g-3">
                    <li>
                      <div className="form-control-wrap">
                        <div className="form-icon form-icon-right">
                          <Icon name="search"></Icon>
                        </div>
                        <input
                          type="text"
                          className="form-control"
                          id="default-04"
                          placeholder="Search comments..."
                          value={searchText}
                          onChange={onFilterChange}
                        />
                      </div>
                    </li>
                    {selectedComments.length > 0 && (
                      <>
                        <li>
                          <Button color="success" onClick={handleBulkApprove} disabled={approveLoading}>
                            {approveLoading ? <Spinner size="sm" /> : <Icon name="check" />}
                            <span>Approve Selected ({selectedComments.length})</span>
                          </Button>
                        </li>
                        <li>
                          <Button color="danger" onClick={handleBulkDelete} disabled={deleteLoading}>
                            {deleteLoading ? <Spinner size="sm" /> : <Icon name="trash" />}
                            <span>Delete Selected ({selectedComments.length})</span>
                          </Button>
                        </li>
                      </>
                    )}
                    <li>
                      <Button color="primary" onClick={refetch} disabled={loading}>
                        {loading ? <Spinner size="sm" /> : <Icon name="reload" />}
                        <span>Refresh</span>
                      </Button>
                    </li>
                  </ul>
                </div>
              </div>
            </BlockHeadContent>
          </BlockBetween>
        </BlockHead>

        <Block>
          <Card className="card-bordered card-stretch">
            <div className="card-inner-group">
              <div className="card-inner position-relative card-tools-toggle">
                <div className="card-title-group">
                  <div className="card-tools">
                    <div className="form-inline flex-nowrap gx-3">
                      <div className="form-wrap w-150px">
                        <span className="d-none d-md-block">
                          <Badge color="light" className="badge-dim">
                            {filteredComments.length} pending comments
                          </Badge>
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {error && (
                <div className="card-inner">
                  <Alert color="danger">
                    <div className="alert-cta flex-wrap flex-md-nowrap">
                      <div className="alert-text">
                        <p>Failed to load comments: {error}</p>
                      </div>
                    </div>
                  </Alert>
                </div>
              )}

              {loading ? (
                <div className="card-inner text-center">
                  <Spinner size="lg" />
                  <p className="mt-2">Loading pending comments...</p>
                </div>
              ) : filteredComments.length === 0 ? (
                <div className="card-inner text-center">
                  <div className="nk-empty-state">
                    <div className="nk-empty-state-icon">
                      <Icon name="comments" style={{ fontSize: '3em', opacity: 0.3 }} />
                    </div>
                    <div className="nk-empty-state-content">
                      <h4 className="nk-empty-state-title">No pending comments</h4>
                      <p className="nk-empty-state-text">
                        Great! All comments have been reviewed and approved.
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="card-inner p-0">
                  <div className="nk-tb-list nk-tb-ulist">
                    <div className="nk-tb-item nk-tb-head">
                      <div className="nk-tb-col nk-tb-col-check">
                        <div className="custom-control custom-control-sm custom-checkbox notext">
                          <input
                            type="checkbox"
                            className="custom-control-input"
                            onChange={onSelectAllChange}
                            id="uid"
                          />
                          <label className="custom-control-label" htmlFor="uid"></label>
                        </div>
                      </div>
                      <div className="nk-tb-col">
                        <span className="sub-text">Author</span>
                      </div>
                      <div className="nk-tb-col tb-col-lg">
                        <span className="sub-text">Comment</span>
                      </div>
                      <div className="nk-tb-col tb-col-md">
                        <span className="sub-text">Post</span>
                      </div>
                      <div className="nk-tb-col tb-col-md">
                        <span className="sub-text">Date</span>
                      </div>
                      <div className="nk-tb-col nk-tb-col-tools text-end">
                        <span className="sub-text">Actions</span>
                      </div>
                    </div>

                    {currentItems.map((comment) => (
                      <div key={comment.uuid} className="nk-tb-item">
                        <div className="nk-tb-col nk-tb-col-check">
                          <div className="custom-control custom-control-sm custom-checkbox notext">
                            <input
                              type="checkbox"
                              className="custom-control-input"
                              defaultChecked={selectedComments.includes(comment.uuid)}
                              id={comment.uuid}
                              onChange={(e) => onSelectChange(e, comment.uuid)}
                            />
                            <label className="custom-control-label" htmlFor={comment.uuid}></label>
                          </div>
                        </div>
                        <div className="nk-tb-col">
                          <div className="user-card">
                            <div className="user-info">
                              <span className="tb-lead">
                                {comment.author?.full_name || 'Anonymous'}
                                <span className="dot d-md-none ms-1"></span>
                              </span>
                              <span className="tb-sub d-md-none">
                                {comment.author?.email}
                              </span>
                            </div>
                          </div>
                        </div>
                        <div className="nk-tb-col tb-col-lg">
                          <span className="tb-amount">
                            {truncateText(comment.content)}
                          </span>
                        </div>
                        <div className="nk-tb-col tb-col-md">
                          <span className="tb-sub text-primary">
                            {truncateText(comment.post_title || 'Unknown Post', 30)}
                          </span>
                        </div>
                        <div className="nk-tb-col tb-col-md">
                          <span className="tb-sub">{formatDate(comment.created_at)}</span>
                        </div>
                        <div className="nk-tb-col nk-tb-col-tools">
                          <ul className="nk-tb-actions gx-1">
                            <li>
                              <Button
                                size="sm"
                                color="success"
                                className="btn-icon btn-trigger"
                                onClick={() => handleApproveComment(comment.uuid)}
                                disabled={approveLoading}
                                title="Approve Comment"
                              >
                                <Icon name="check" />
                              </Button>
                            </li>
                            <li>
                              <Button
                                size="sm"
                                color="danger"
                                className="btn-icon btn-trigger"
                                onClick={() => handleDeleteComment(comment.uuid)}
                                disabled={deleteLoading}
                                title="Delete Comment"
                              >
                                <Icon name="trash" />
                              </Button>
                            </li>
                          </ul>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {filteredComments.length > 0 && (
                <div className="card-inner">
                  <div className="nk-block-between-md g-3">
                    <div className="g">
                      <PaginationComponent
                        itemPerPage={itemPerPage}
                        totalItems={filteredComments.length}
                        currentPage={currentPage}
                        setCurrentPage={setCurrentPage}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </Card>
        </Block>
      </Content>
    </>
  );
};

export default CommentModeration;