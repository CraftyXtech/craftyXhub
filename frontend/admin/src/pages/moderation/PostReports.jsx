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
import { Card, Badge, Spinner, Alert, Modal, ModalBody, ModalHeader } from "reactstrap";
import { useGetReports, useResolveReport } from "@/api/reportsService";
import { toast } from "react-toastify";
import Swal from "sweetalert2";

const PostReports = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [itemPerPage] = useState(10);
  const [searchText, setSearchText] = useState("");
  const [sm, updateSm] = useState(false);
  const [selectedReports, setSelectedReports] = useState([]);
  const [viewModal, setViewModal] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);
  const [resolvedReports, setResolvedReports] = useState(new Set());

  // API hooks
  const { reports, total, loading, error, refetch } = useGetReports();
  const { resolveReport, loading: resolveLoading } = useResolveReport();

  // Filter reports based on search and resolved status
  const filteredReports = reports.filter(report => {
    const matchesSearch = 
      report.reason?.toLowerCase().includes(searchText.toLowerCase()) ||
      report.description?.toLowerCase().includes(searchText.toLowerCase()) ||
      report.post?.title?.toLowerCase().includes(searchText.toLowerCase()) ||
      report.user?.full_name?.toLowerCase().includes(searchText.toLowerCase());
    
    const isNotResolved = !resolvedReports.has(report.id);
    
    return matchesSearch && isNotResolved;
  });

  // Pagination
  const indexOfLastItem = currentPage * itemPerPage;
  const indexOfFirstItem = indexOfLastItem - itemPerPage;
  const currentItems = filteredReports.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(filteredReports.length / itemPerPage);

  // Handle search
  const onFilterChange = (e) => {
    setSearchText(e.target.value);
    setCurrentPage(1);
  };

  // Handle report selection
  const onSelectChange = (e, reportId) => {
    let newSelection = [...selectedReports];
    if (e.target.checked) {
      newSelection.push(reportId);
    } else {
      newSelection = newSelection.filter(item => item !== reportId);
    }
    setSelectedReports(newSelection);
  };

  // Handle select all
  const onSelectAllChange = (e) => {
    if (e.target.checked) {
      setSelectedReports(currentItems.map(item => item.id));
    } else {
      setSelectedReports([]);
    }
  };

  // Handle view report details
  const handleViewReport = (report) => {
    setSelectedReport(report);
    setViewModal(true);
  };

  // Handle resolve report
  const handleResolveReport = async (reportId, action = 'resolved') => {
    try {
      await resolveReport(reportId, action);
      setResolvedReports(prev => new Set([...prev, reportId]));
      toast.success(`Report ${action} successfully`);
      refetch();
    } catch (error) {
      toast.error(`Failed to ${action} report`);
    }
  };

  // Handle bulk resolve
  const handleBulkResolve = async (action = 'resolved') => {
    if (selectedReports.length === 0) {
      toast.warning("Please select reports to resolve");
      return;
    }

    const actionText = action === 'dismissed' ? 'dismiss' : 'resolve';
    const result = await Swal.fire({
      title: `${actionText.charAt(0).toUpperCase() + actionText.slice(1)} Reports?`,
      text: `Are you sure you want to ${actionText} ${selectedReports.length} report(s)?`,
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: action === 'dismissed' ? '#d33' : '#3085d6',
      cancelButtonColor: '#6c757d',
      confirmButtonText: `Yes, ${actionText} them!`
    });

    if (result.isConfirmed) {
      try {
        const resolvePromises = selectedReports.map(id => resolveReport(id, action));
        await Promise.all(resolvePromises);
        
        // Mark as resolved locally
        setResolvedReports(prev => {
          const newSet = new Set(prev);
          selectedReports.forEach(id => newSet.add(id));
          return newSet;
        });
        
        toast.success(`${selectedReports.length} report(s) ${action} successfully`);
        setSelectedReports([]);
        refetch();
      } catch (error) {
        toast.error(`Failed to ${actionText} some reports`);
      }
    }
  };

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  // Truncate text
  const truncateText = (text, maxLength = 100) => {
    if (!text) return 'N/A';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  };

  // Get reason badge color
  const getReasonBadgeColor = (reason) => {
    switch (reason?.toLowerCase()) {
      case 'spam':
        return 'warning';
      case 'harassment':
      case 'hate_speech':
        return 'danger';
      case 'inappropriate_content':
        return 'info';
      case 'copyright':
        return 'secondary';
      default:
        return 'light';
    }
  };

  return (
    <>
      <Head title="Post Reports Management" />
      <Content>
        <BlockHead size="sm">
          <BlockBetween>
            <BlockHeadContent>
              <BackTo link="/" icon="arrow-left">
                Dashboard
              </BackTo>
              <BlockTitle page>Post Reports Management</BlockTitle>
              <BlockDes className="text-soft">
                Review and manage user reports about posts
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
                          placeholder="Search reports..."
                          value={searchText}
                          onChange={onFilterChange}
                        />
                      </div>
                    </li>
                    {selectedReports.length > 0 && (
                      <>
                        <li>
                          <Button 
                            color="success" 
                            onClick={() => handleBulkResolve('resolved')} 
                            disabled={resolveLoading}
                          >
                            {resolveLoading ? <Spinner size="sm" /> : <Icon name="check" />}
                            <span>Resolve Selected ({selectedReports.length})</span>
                          </Button>
                        </li>
                        <li>
                          <Button 
                            color="warning" 
                            onClick={() => handleBulkResolve('dismissed')} 
                            disabled={resolveLoading}
                          >
                            {resolveLoading ? <Spinner size="sm" /> : <Icon name="cross" />}
                            <span>Dismiss Selected ({selectedReports.length})</span>
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
                            {filteredReports.length} active reports
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
                        <p>Failed to load reports: {error}</p>
                      </div>
                    </div>
                  </Alert>
                </div>
              )}

              {loading ? (
                <div className="card-inner text-center">
                  <Spinner size="lg" />
                  <p className="mt-2">Loading reports...</p>
                </div>
              ) : filteredReports.length === 0 ? (
                <div className="card-inner text-center">
                  <div className="nk-empty-state">
                    <div className="nk-empty-state-icon">
                      <Icon name="report" style={{ fontSize: '3em', opacity: 0.3 }} />
                    </div>
                    <div className="nk-empty-state-content">
                      <h4 className="nk-empty-state-title">No active reports</h4>
                      <p className="nk-empty-state-text">
                        Great! All reports have been reviewed and resolved.
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
                        <span className="sub-text">Reporter</span>
                      </div>
                      <div className="nk-tb-col tb-col-lg">
                        <span className="sub-text">Post</span>
                      </div>
                      <div className="nk-tb-col tb-col-md">
                        <span className="sub-text">Reason</span>
                      </div>
                      <div className="nk-tb-col tb-col-md">
                        <span className="sub-text">Date</span>
                      </div>
                      <div className="nk-tb-col nk-tb-col-tools text-end">
                        <span className="sub-text">Actions</span>
                      </div>
                    </div>

                    {currentItems.map((report) => (
                      <div key={report.id} className="nk-tb-item">
                        <div className="nk-tb-col nk-tb-col-check">
                          <div className="custom-control custom-control-sm custom-checkbox notext">
                            <input
                              type="checkbox"
                              className="custom-control-input"
                              defaultChecked={selectedReports.includes(report.id)}
                              id={`report-${report.id}`}
                              onChange={(e) => onSelectChange(e, report.id)}
                            />
                            <label className="custom-control-label" htmlFor={`report-${report.id}`}></label>
                          </div>
                        </div>
                        <div className="nk-tb-col">
                          <div className="user-card">
                            <div className="user-info">
                              <span className="tb-lead">
                                {report.user?.full_name || 'Anonymous'}
                                <span className="dot d-md-none ms-1"></span>
                              </span>
                              <span className="tb-sub d-md-none">
                                {report.user?.email}
                              </span>
                            </div>
                          </div>
                        </div>
                        <div className="nk-tb-col tb-col-lg">
                          <span className="tb-amount">
                            {truncateText(report.post?.title, 50)}
                          </span>
                          <span className="tb-sub d-block">
                            {truncateText(report.description, 80)}
                          </span>
                        </div>
                        <div className="nk-tb-col tb-col-md">
                          <Badge color={getReasonBadgeColor(report.reason)} className="badge-dim">
                            {report.reason?.replace('_', ' ') || 'Other'}
                          </Badge>
                        </div>
                        <div className="nk-tb-col tb-col-md">
                          <span className="tb-sub">{formatDate(report.created_at)}</span>
                        </div>
                        <div className="nk-tb-col nk-tb-col-tools">
                          <ul className="nk-tb-actions gx-1">
                            <li>
                              <Button
                                size="sm"
                                color="info"
                                className="btn-icon btn-trigger"
                                onClick={() => handleViewReport(report)}
                                title="View Details"
                              >
                                <Icon name="eye" />
                              </Button>
                            </li>
                            <li>
                              <Button
                                size="sm"
                                color="success"
                                className="btn-icon btn-trigger"
                                onClick={() => handleResolveReport(report.id, 'resolved')}
                                disabled={resolveLoading}
                                title="Resolve Report"
                              >
                                <Icon name="check" />
                              </Button>
                            </li>
                            <li>
                              <Button
                                size="sm"
                                color="warning"
                                className="btn-icon btn-trigger"
                                onClick={() => handleResolveReport(report.id, 'dismissed')}
                                disabled={resolveLoading}
                                title="Dismiss Report"
                              >
                                <Icon name="cross" />
                              </Button>
                            </li>
                          </ul>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {filteredReports.length > 0 && (
                <div className="card-inner">
                  <div className="nk-block-between-md g-3">
                    <div className="g">
                      <PaginationComponent
                        itemPerPage={itemPerPage}
                        totalItems={filteredReports.length}
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

        {/* Report Details Modal */}
        <Modal isOpen={viewModal} toggle={() => setViewModal(false)} size="lg">
          <ModalHeader toggle={() => setViewModal(false)}>
            Report Details
          </ModalHeader>
          <ModalBody>
            {selectedReport && (
              <div className="nk-modal-content">
                <Row className="g-gs">
                  <Col md="6">
                    <div className="form-group">
                      <label className="form-label">Reporter</label>
                      <div className="form-control-plaintext">
                        {selectedReport.user?.full_name || 'Anonymous'} 
                        {selectedReport.user?.email && (
                          <span className="text-soft"> ({selectedReport.user.email})</span>
                        )}
                      </div>
                    </div>
                  </Col>
                  <Col md="6">
                    <div className="form-group">
                      <label className="form-label">Reason</label>
                      <div className="form-control-plaintext">
                        <Badge color={getReasonBadgeColor(selectedReport.reason)}>
                          {selectedReport.reason?.replace('_', ' ') || 'Other'}
                        </Badge>
                      </div>
                    </div>
                  </Col>
                  <Col md="12">
                    <div className="form-group">
                      <label className="form-label">Reported Post</label>
                      <div className="form-control-plaintext">
                        <strong>{selectedReport.post?.title || 'Unknown Post'}</strong>
                      </div>
                    </div>
                  </Col>
                  <Col md="12">
                    <div className="form-group">
                      <label className="form-label">Description</label>
                      <div className="form-control-plaintext">
                        {selectedReport.description || 'No description provided'}
                      </div>
                    </div>
                  </Col>
                  <Col md="6">
                    <div className="form-group">
                      <label className="form-label">Report Date</label>
                      <div className="form-control-plaintext">
                        {formatDate(selectedReport.created_at)}
                      </div>
                    </div>
                  </Col>
                </Row>
                <div className="form-group mt-4">
                  <div className="d-flex gap-2">
                    <Button 
                      color="success" 
                      onClick={() => {
                        handleResolveReport(selectedReport.id, 'resolved');
                        setViewModal(false);
                      }}
                      disabled={resolveLoading}
                    >
                      <Icon name="check" /> Resolve Report
                    </Button>
                    <Button 
                      color="warning" 
                      onClick={() => {
                        handleResolveReport(selectedReport.id, 'dismissed');
                        setViewModal(false);
                      }}
                      disabled={resolveLoading}
                    >
                      <Icon name="cross" /> Dismiss Report
                    </Button>
                    <Button color="secondary" onClick={() => setViewModal(false)}>
                      Close
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </ModalBody>
        </Modal>
      </Content>
    </>
  );
};

export default PostReports;