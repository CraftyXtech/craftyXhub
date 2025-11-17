import React, { useEffect, useMemo, useState } from "react";
import Content from "@/layout/content/Content";
import Head from "@/layout/head/Head";
import PostsOverview from "@/components/partials/blog-analytics/PostsOverview";
import EngagementMetrics from "@/components/partials/blog-analytics/EngagementMetrics";
import PopularPosts from "@/components/partials/blog-analytics/PopularPosts";
import RecentActivity from "@/components/partials/blog-analytics/RecentActivity";
import RecentDocuments from "@/components/partials/dashboard/RecentDocuments";
import useAxiosPrivate from "@/api/useAxiosPrivate";
import useAuth from "@/api/useAuth";
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

  const axiosPrivate = useAxiosPrivate();
  const { auth } = useAuth();

  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const role = auth?.user?.role?.toLowerCase();
  const isAdminRole = role === "super_admin" || role === "admin" || role === "moderator";

  useEffect(() => {
    let isMounted = true;

    const fetchDashboard = async () => {
      if (!auth?.user) {
        setDashboard(null);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const endpoint = isAdminRole ? "/dashboard/admin" : "/dashboard/user";
        const response = await axiosPrivate.get(endpoint);

        if (isMounted) {
          setDashboard(response.data);
        }
      } catch (err) {
        console.error("Failed to load dashboard:", err);
        if (isMounted) {
          const message =
            err?.response?.data?.detail || err.message || "Failed to load dashboard";
          setError(message);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchDashboard();

    return () => {
      isMounted = false;
    };
  }, [auth?.user, isAdminRole, axiosPrivate]);

  const overviewCards = useMemo(() => {
    const overview = dashboard?.overview;
    const engagement = dashboard?.engagement_metrics;

    if (!overview) {
      return [];
    }

    if (isAdminRole) {
      return [
        {
          key: "totalUsers",
          label: "Total Users",
          icon: "users",
          color: "primary",
          value: overview.total_users ?? 0,
          showChange: true,
          changeDirection: "up",
          changeText: "12.5%",
          subtitle: null,
        },
        {
          key: "activeUsers",
          label: "Active Users",
          icon: "user-check",
          color: "success",
          value: overview.active_users ?? 0,
          showChange: true,
          changeDirection: "up",
          changeText: "8.3%",
          subtitle: null,
        },
        {
          key: "totalPosts",
          label: "Total Posts",
          icon: "file-text",
          color: "info",
          value: overview.total_posts ?? 0,
          showChange: true,
          changeDirection: "up",
          changeText: "15.2%",
          subtitle: null,
        },
        {
          key: "pendingReviews",
          label: "Pending Reviews",
          icon: "alert-circle",
          color: "warning",
          value: overview.pending_reviews ?? 0,
          showChange: false,
          changeDirection: null,
          changeText: "",
          subtitle: "Needs attention",
        },
      ];
    }

    return [
      {
        key: "myPosts",
        label: "My Posts",
        icon: "file-text",
        color: "primary",
        value: overview.total_posts ?? 0,
        showChange: false,
        changeDirection: null,
        changeText: "",
        subtitle: null,
      },
      {
        key: "publishedPosts",
        label: "Published",
        icon: "check-circle",
        color: "success",
        value: overview.published_posts ?? 0,
        showChange: false,
        changeDirection: null,
        changeText: "",
        subtitle: null,
      },
      {
        key: "draftPosts",
        label: "Drafts",
        icon: "edit",
        color: "warning",
        value: overview.draft_posts ?? 0,
        showChange: false,
        changeDirection: null,
        changeText: "",
        subtitle: null,
      },
      {
        key: "totalViews",
        label: "Total Views",
        icon: "eye",
        color: "info",
        value: engagement?.total_views ?? 0,
        showChange: false,
        changeDirection: null,
        changeText: "",
        subtitle: null,
      },
    ];
  }, [dashboard, isAdminRole]);

  const postsOverviewData = useMemo(() => {
    const stats = dashboard?.posts_overview;
    if (!stats) {
      return null;
    }
    return {
      totalPosts: stats.total_posts ?? 0,
      published: stats.published_posts ?? 0,
      drafts: stats.draft_posts ?? 0,
      trending: stats.trending_count ?? 0,
    };
  }, [dashboard]);

  const engagementMetricsData = useMemo(() => {
    const metrics = dashboard?.engagement_metrics;
    if (!metrics) {
      return null;
    }
    return {
      totalViews: metrics.total_views ?? 0,
      likes: metrics.total_likes ?? 0,
      comments: metrics.total_comments ?? 0,
      bookmarks: metrics.total_bookmarks ?? 0,
    };
  }, [dashboard]);

  const popularPostsData = useMemo(() => {
    if (!dashboard?.top_posts) {
      return null;
    }
    return {
      posts: dashboard.top_posts.map((post) => ({
        id: post.uuid,
        title: post.title,
        views: post.view_count ?? 0,
        likes: post.like_count ?? 0,
        trend: "up",
      })),
    };
  }, [dashboard]);

  const recentActivityData = useMemo(() => {
    if (!dashboard?.recent_activity) {
      return null;
    }
    return {
      activities: dashboard.recent_activity.map((activity) => ({
        id: activity.id,
        type: activity.type,
        icon: activity.icon || "activity",
        color: activity.color || "primary",
        title: activity.title,
        description: activity.description,
        time: activity.created_at
          ? new Date(activity.created_at).toLocaleString()
          : "",
      })),
    };
  }, [dashboard]);

  const recentDocuments = useMemo(() => {
    if (!dashboard?.recent_documents) {
      return [];
    }
    return dashboard.recent_documents.map((doc) => ({
      id: doc.uuid,
      name: doc.title,
      type: doc.status === "draft" ? "Draft" : "Document",
      category: doc.category || "Blog Content",
      updated_at: doc.updated_at || doc.created_at,
    }));
  }, [dashboard]);

  const pageSubtitle = isAdminRole
    ? "Welcome to your admin dashboard."
    : "Monitor your content performance and engagement.";

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
                {error ? (
                  <p className="text-danger">{error}</p>
                ) : (
                  <p>{pageSubtitle}</p>
                )}
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
            {overviewCards.map((card) => (
              <Col key={card.key} sm="6" lg="3">
                <Card className="card-bordered h-100">
                  <CardBody className="card-inner">
                    <div className="card-title-group align-start mb-2">
                      <div className="card-title">
                        <h6 className="subtitle">{card.label}</h6>
                      </div>
                      <div className="card-tools">
                        <div
                          className={`icon-circle icon-circle-lg bg-${card.color}-dim text-${card.color}`}
                        >
                          <Icon name={card.icon}></Icon>
                        </div>
                      </div>
                    </div>
                    <div className="align-end flex-sm-wrap g-4 flex-md-nowrap">
                      <div className="nk-sale-data">
                        <span className="amount">
                          {loading ? "..." : card.value}
                        </span>
                        {card.subtitle && (
                          <span className="sub-title text-soft mt-1">
                            {card.subtitle}
                          </span>
                        )}
                        {card.showChange && card.changeDirection && (
                          <span className="sub-title text-soft mt-1">
                            <span
                              className={`change ${
                                card.changeDirection === "up" ? "up" : "down"
                              } text-${
                                card.changeDirection === "up"
                                  ? "success"
                                  : "danger"
                              }`}
                            >
                              <Icon
                                name={
                                  card.changeDirection === "up"
                                    ? "arrow-long-up"
                                    : "arrow-long-down"
                                }
                              ></Icon>
                              {card.changeText}
                            </span>
                          </span>
                        )}
                      </div>
                    </div>
                  </CardBody>
                </Card>
              </Col>
            ))}
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
              <PostsOverview data={postsOverviewData} />
            </Col>
            <Col lg="6" xxl="6">
              <EngagementMetrics data={engagementMetricsData} />
            </Col>
          </Row>
        </Block>

        <Block>
          <Row className="g-gs">
            <Col lg="8" xxl="8">
              <PopularPosts data={popularPostsData} />
            </Col>
            <Col lg="4" xxl="4">
              <RecentActivity data={recentActivityData} />
            </Col>
          </Row>
        </Block>

        <Block>
          <RecentDocuments documents={recentDocuments} />
        </Block>
      </Content>
    </>
  );
};

export default AnalyticsHomePage;
