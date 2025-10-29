import React, { useState } from "react";
import Content from "@/layout/content/Content";
import Head from "@/layout/head/Head";
import PostsOverview from "@/components/partials/blog-analytics/PostsOverview";
import EngagementMetrics from "@/components/partials/blog-analytics/EngagementMetrics";
import PopularPosts from "@/components/partials/blog-analytics/PopularPosts";
import RecentActivity from "@/components/partials/blog-analytics/RecentActivity";
import RecentDocuments from "@/components/partials/dashboard/RecentDocuments";
import { Card, CardBody } from "reactstrap";
import { DropdownToggle, DropdownMenu, UncontrolledDropdown, DropdownItem } from "reactstrap";
import {
  Block,
  BlockDes,
  BlockHead,
  BlockHeadContent,
  BlockTitle,
  Icon,
  Button,
  Row,
  Col,
} from "@/components/Component";

const AnalyticsHomePage = () => {
  const [sm, updateSm] = useState(false);
  
  const systemData = {
    overview: {
      totalUsers: 1248,
      activeUsers: 892,
      totalPosts: 156,
      pendingReviews: 23
    },
    postsOverview: {
      totalPosts: 156,
      published: 132,
      drafts: 18,
      trending: 6
    },
    engagementMetrics: {
      totalViews: '45.2k',
      likes: '8.5k',
      comments: '1.2k',
      bookmarks: '3.4k'
    }
  };

  return (
    <>
      <Head title="Dashboard" />
      <Content>
        <BlockHead size="sm">
          <div className="nk-block-between">
            <BlockHeadContent>
              <BlockTitle page tag="h3">
                Dashboard Overview
              </BlockTitle>
              <BlockDes className="text-soft">
                <p>Welcome to your admin dashboard.</p>
              </BlockDes>
            </BlockHeadContent>
            <BlockHeadContent>
              <div className="toggle-wrap nk-block-tools-toggle">
                <Button
                  className={`btn-icon btn-trigger toggle-expand me-n1 ${sm ? "active" : ""}`}
                  onClick={() => updateSm(!sm)}
                >
                  <Icon name="more-v"></Icon>
                </Button>
                <div className="toggle-expand-content" style={{ display: sm ? "block" : "none" }}>
                  <ul className="nk-block-tools g-3">
                    <li>
                      <UncontrolledDropdown >
                        <DropdownToggle tag="a" className="dropdown-toggle btn btn-white btn-dim btn-outline-light">
                          <Icon className="d-none d-sm-inline" name="calender-date"></Icon>
                          <span>
                            <span className="d-none d-md-inline">Last</span> 30 Days
                          </span>
                          <Icon className="dd-indc" name="chevron-right"></Icon>
                        </DropdownToggle>
                        <DropdownMenu>
                          <ul className="link-list-opt no-bdr">
                            <li>
                              <DropdownItem
                                href="#dropdownitem"
                                onClick={(ev) => {
                                  ev.preventDefault();
                                }}
                              >
                                Last 30 days
                              </DropdownItem>
                            </li>
                            <li>
                              <DropdownItem
                                href="#dropdownitem"
                                onClick={(ev) => {
                                  ev.preventDefault();
                                }}
                              >
                                Last 6 months
                              </DropdownItem>
                            </li>
                            <li>
                              <DropdownItem
                                href="#dropdownitem"
                                onClick={(ev) => {
                                  ev.preventDefault();
                                }}
                              >
                                Last 3 weeks
                              </DropdownItem>
                            </li>
                          </ul>
                        </DropdownMenu>
                      </UncontrolledDropdown>
                    </li>
                    <li className="nk-block-tools-opt">
                      <Button color="primary">
                        <Icon name="reports"></Icon>
                        <span>Reports</span>
                      </Button>
                    </li>
                  </ul>
                </div>
              </div>
            </BlockHeadContent>
          </div>
        </BlockHead>

        <Block>
          <Row className="g-gs">
            <Col sm="6" lg="3">
              <Card className="card-bordered h-100">
                <CardBody className="card-inner">
                  <div className="card-title-group align-start mb-2">
                    <div className="card-title">
                      <h6 className="subtitle">Total Users</h6>
                    </div>
                    <div className="card-tools">
                      <div className="icon-circle icon-circle-lg bg-primary-dim text-primary">
                        <Icon name="users"></Icon>
                      </div>
                    </div>
                  </div>
                  <div className="align-end flex-sm-wrap g-4 flex-md-nowrap">
                    <div className="nk-sale-data">
                      <span className="amount">{systemData.overview.totalUsers}</span>
                      <span className="sub-title text-soft mt-1">
                        <span className="change up text-success">
                          <Icon name="arrow-long-up"></Icon>12.5%
                        </span>
                      </span>
                    </div>
                  </div>
                </CardBody>
              </Card>
            </Col>

            <Col sm="6" lg="3">
              <Card className="card-bordered h-100">
                <CardBody className="card-inner">
                  <div className="card-title-group align-start mb-2">
                    <div className="card-title">
                      <h6 className="subtitle">Active Users</h6>
                    </div>
                    <div className="card-tools">
                      <div className="icon-circle icon-circle-lg bg-success-dim text-success">
                        <Icon name="user-check"></Icon>
                      </div>
                    </div>
                  </div>
                  <div className="align-end flex-sm-wrap g-4 flex-md-nowrap">
                    <div className="nk-sale-data">
                      <span className="amount">{systemData.overview.activeUsers}</span>
                      <span className="sub-title text-soft mt-1">
                        <span className="change up text-success">
                          <Icon name="arrow-long-up"></Icon>8.3%
                        </span>
                      </span>
                    </div>
                  </div>
                </CardBody>
              </Card>
            </Col>

            <Col sm="6" lg="3">
              <Card className="card-bordered h-100">
                <CardBody className="card-inner">
                  <div className="card-title-group align-start mb-2">
                    <div className="card-title">
                      <h6 className="subtitle">Total Posts</h6>
                    </div>
                    <div className="card-tools">
                      <div className="icon-circle icon-circle-lg bg-info-dim text-info">
                        <Icon name="file-text"></Icon>
                      </div>
                    </div>
                  </div>
                  <div className="align-end flex-sm-wrap g-4 flex-md-nowrap">
                    <div className="nk-sale-data">
                      <span className="amount">{systemData.overview.totalPosts}</span>
                      <span className="sub-title text-soft mt-1">
                        <span className="change up text-success">
                          <Icon name="arrow-long-up"></Icon>15.2%
                        </span>
                      </span>
                    </div>
                  </div>
                </CardBody>
              </Card>
            </Col>

            <Col sm="6" lg="3">
              <Card className="card-bordered h-100">
                <CardBody className="card-inner">
                  <div className="card-title-group align-start mb-2">
                    <div className="card-title">
                      <h6 className="subtitle">Pending Reviews</h6>
                    </div>
                    <div className="card-tools">
                      <div className="icon-circle icon-circle-lg bg-warning-dim text-warning">
                        <Icon name="alert-circle"></Icon>
                      </div>
                    </div>
                  </div>
                  <div className="align-end flex-sm-wrap g-4 flex-md-nowrap">
                    <div className="nk-sale-data">
                      <span className="amount">{systemData.overview.pendingReviews}</span>
                      <span className="sub-title text-soft mt-1">Needs attention</span>
                    </div>
                  </div>
                </CardBody>
              </Card>
            </Col>
          </Row>
        </Block>

        <Block>
          <BlockHead>
            <BlockHeadContent>
              <BlockTitle>Blog Analytics</BlockTitle>
              <BlockDes className="text-soft">
                <p>Monitor your blog performance and engagement</p>
              </BlockDes>
            </BlockHeadContent>
          </BlockHead>
          <Row className="g-gs">
            <Col lg="6" xxl="6">
              <PostsOverview data={systemData.postsOverview} />
            </Col>
            <Col lg="6" xxl="6">
              <EngagementMetrics data={systemData.engagementMetrics} />
            </Col>
          </Row>
        </Block>

        <Block>
          <Row className="g-gs">
            <Col lg="8" xxl="8">
              <PopularPosts />
            </Col>
            <Col lg="4" xxl="4">
              <RecentActivity />
            </Col>
          </Row>
        </Block>

        <Block>
          <RecentDocuments />
        </Block>
      </Content>
    </>
  );
};

export default AnalyticsHomePage;
