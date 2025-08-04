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
  BackTo,
} from "@/components/Component";
import { Card, Badge, Spinner, Alert } from "reactstrap";
import useAxiosPrivate from "@/api/useAxiosPrivate";
import { toast } from "react-toastify";

const HealthCheck = () => {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastCheck, setLastCheck] = useState(null);
  
  const axiosPrivate = useAxiosPrivate();

  // Check system health
  const checkHealth = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Note: Using the base URL without /v1 prefix since health is usually at root
      const baseUrl = import.meta.env.VITE_APP_API_URL?.replace('/v1', '') || 'http://127.0.0.1:8000';
      const response = await fetch(`${baseUrl}/health`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setHealthData(data);
      setLastCheck(new Date());
      toast.success("Health check completed successfully");
    } catch (err) {
      setError(err.message || "Health check failed");
      toast.error("Health check failed");
    } finally {
      setLoading(false);
    }
  };

  // Auto-check on component mount
  useEffect(() => {
    checkHealth();
  }, []);

  // Format date
  const formatDate = (date) => {
    return new Date(date).toLocaleString();
  };

  // Get status badge color
  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'ok':
      case 'online':
        return 'success';
      case 'warning':
      case 'degraded':
        return 'warning';
      case 'error':
      case 'offline':
      case 'unhealthy':
        return 'danger';
      default:
        return 'secondary';
    }
  };

  return (
    <>
      <Head title="System Health Check" />
      <Content>
        <BlockHead size="sm">
          <BlockBetween>
            <BlockHeadContent>
              <BackTo link="/" icon="arrow-left">
                Dashboard
              </BackTo>
              <BlockTitle page>System Health Check</BlockTitle>
              <BlockDes className="text-soft">
                Monitor the health and status of system components
              </BlockDes>
            </BlockHeadContent>
            <BlockHeadContent>
              <Button color="primary" onClick={checkHealth} disabled={loading}>
                {loading ? <Spinner size="sm" /> : <Icon name="reload" />}
                <span>{loading ? "Checking..." : "Check Health"}</span>
              </Button>
            </BlockHeadContent>
          </BlockBetween>
        </BlockHead>

        <Block>
          <Row className="g-gs">
            <Col xxl="6">
              <Card className="card-bordered h-100">
                <div className="card-inner">
                  <div className="card-title-group">
                    <div className="card-title">
                      <h6 className="title">
                        <Icon name="activity" className="me-2" />
                        System Status
                      </h6>
                    </div>
                    {lastCheck && (
                      <div className="card-tools">
                        <small className="text-soft">
                          Last checked: {formatDate(lastCheck)}
                        </small>
                      </div>
                    )}
                  </div>

                  {error && (
                    <Alert color="danger" className="mt-3">
                      <div className="alert-cta flex-wrap flex-md-nowrap">
                        <div className="alert-text">
                          <h6>Health Check Failed</h6>
                          <p>{error}</p>
                        </div>
                      </div>
                    </Alert>
                  )}

                  {loading && (
                    <div className="text-center my-4">
                      <Spinner size="lg" />
                      <p className="mt-2">Checking system health...</p>
                    </div>
                  )}

                  {healthData && !loading && (
                    <div className="nk-tb-list">
                      <div className="nk-tb-item nk-tb-head">
                        <div className="nk-tb-col">
                          <span className="sub-text">Component</span>
                        </div>
                        <div className="nk-tb-col text-end">
                          <span className="sub-text">Status</span>
                        </div>
                      </div>

                      {/* API Status */}
                      <div className="nk-tb-item">
                        <div className="nk-tb-col">
                          <span className="tb-lead">API Server</span>
                        </div>
                        <div className="nk-tb-col text-end">
                          <Badge color={getStatusColor(healthData.status || 'healthy')}>
                            {healthData.status || 'Healthy'}
                          </Badge>
                        </div>
                      </div>

                      {/* Database Status */}
                      {healthData.database && (
                        <div className="nk-tb-item">
                          <div className="nk-tb-col">
                            <span className="tb-lead">Database</span>
                          </div>
                          <div className="nk-tb-col text-end">
                            <Badge color={getStatusColor(healthData.database.status)}>
                              {healthData.database.status || 'Unknown'}
                            </Badge>
                          </div>
                        </div>
                      )}

                      {/* Version Info */}
                      {healthData.version && (
                        <div className="nk-tb-item">
                          <div className="nk-tb-col">
                            <span className="tb-lead">Version</span>
                          </div>
                          <div className="nk-tb-col text-end">
                            <span className="tb-sub">{healthData.version}</span>
                          </div>
                        </div>
                      )}

                      {/* Environment */}
                      {healthData.environment && (
                        <div className="nk-tb-item">
                          <div className="nk-tb-col">
                            <span className="tb-lead">Environment</span>
                          </div>
                          <div className="nk-tb-col text-end">
                            <Badge color={healthData.environment === 'production' ? 'danger' : 'info'}>
                              {healthData.environment}
                            </Badge>
                          </div>
                        </div>
                      )}

                      {/* Uptime */}
                      {healthData.uptime && (
                        <div className="nk-tb-item">
                          <div className="nk-tb-col">
                            <span className="tb-lead">Uptime</span>
                          </div>
                          <div className="nk-tb-col text-end">
                            <span className="tb-sub">{healthData.uptime}</span>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </Card>
            </Col>

            <Col xxl="6">
              <Card className="card-bordered h-100">
                <div className="card-inner">
                  <div className="card-title-group">
                    <div className="card-title">
                      <h6 className="title">
                        <Icon name="info" className="me-2" />
                        System Information
                      </h6>
                    </div>
                  </div>

                  {healthData && !loading && (
                    <div className="nk-tb-list">
                      <div className="nk-tb-item nk-tb-head">
                        <div className="nk-tb-col">
                          <span className="sub-text">Property</span>
                        </div>
                        <div className="nk-tb-col text-end">
                          <span className="sub-text">Value</span>
                        </div>
                      </div>

                      {/* Timestamp */}
                      {healthData.timestamp && (
                        <div className="nk-tb-item">
                          <div className="nk-tb-col">
                            <span className="tb-lead">Server Time</span>
                          </div>
                          <div className="nk-tb-col text-end">
                            <span className="tb-sub">{formatDate(healthData.timestamp)}</span>
                          </div>
                        </div>
                      )}

                      {/* Response Time */}
                      {healthData.response_time && (
                        <div className="nk-tb-item">
                          <div className="nk-tb-col">
                            <span className="tb-lead">Response Time</span>
                          </div>
                          <div className="nk-tb-col text-end">
                            <span className="tb-sub">{healthData.response_time}</span>
                          </div>
                        </div>
                      )}

                      {/* Additional details */}
                      {healthData.details && Object.entries(healthData.details).map(([key, value]) => (
                        <div key={key} className="nk-tb-item">
                          <div className="nk-tb-col">
                            <span className="tb-lead">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                          </div>
                          <div className="nk-tb-col text-end">
                            <span className="tb-sub">{String(value)}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {!healthData && !loading && !error && (
                    <div className="text-center my-4">
                      <Icon name="activity" style={{ fontSize: '3em', opacity: 0.3 }} />
                      <p className="mt-2 text-soft">No health data available</p>
                    </div>
                  )}
                </div>
              </Card>
            </Col>
          </Row>
        </Block>
      </Content>
    </>
  );
};

export default HealthCheck;