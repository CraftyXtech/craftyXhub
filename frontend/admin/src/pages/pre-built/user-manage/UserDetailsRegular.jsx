import React, { useEffect, useState } from "react";
import Content from "@/layout/content/Content";
import Head from "@/layout/head/Head";
import { Card, Badge } from "reactstrap";
import {
  Button,
  Block,
  BlockBetween,
  BlockDes,
  BlockHead,
  BlockHeadContent,
  BlockTitle,
  Icon,
  Col,
  Row,
  UserAvatar,
} from "@/components/Component";
import { useNavigate, useParams } from "react-router-dom";
import { findUpper } from "@/utils/Utils";
import {
  useDeactivateAdminUser,
  useGetAdminUser,
  useToggleAdminUserStatus,
  useUpdateAdminUser,
} from "@/api/adminUserHooks";
import useAxiosPrivate from "@/api/useAxiosPrivate";
import useAuth from "@/api/useAuth";
import RoleModal from "./RoleModal";

const formatRoleLabel = (role) => {
  const value = (role || "").toLowerCase();
  if (value === "super_admin") return "Super Admin";
  if (value === "admin") return "Admin";
  if (value === "moderator") return "Moderator";
  if (value === "user") return "User";
  return role || "User";
};

const getRoleDescription = (role) => {
  const value = (role || "").toLowerCase();
  switch (value) {
    case "super_admin":
      return "Full system access, including managing admins and global settings.";
    case "admin":
      return "Can manage users, posts, and moderation tools, but cannot change super-admins.";
    case "moderator":
      return "Can moderate content and handle reports, but cannot manage user roles.";
    case "user":
    default:
      return "Can create and manage their own content.";
  }
};

const UserDetailsPage = () => {
  const { userId } = useParams();
  const navigate = useNavigate();

  const axiosPrivate = useAxiosPrivate();
  const { auth } = useAuth();

  const { user, loading, error, setUser } = useGetAdminUser(userId);
  const { mutate: updateUser, loading: updating } = useUpdateAdminUser();
  const { mutate: toggleStatus, loading: statusLoading } = useToggleAdminUserStatus();
  const { mutate: deactivateUser, loading: deactivating } = useDeactivateAdminUser();

  const [editForm, setEditForm] = useState({ full_name: "", email: "", is_verified: false });
  const [isRoleModalOpen, setRoleModalOpen] = useState(false);
  const [roleHistory, setRoleHistory] = useState([]);
  const [roleHistoryLoading, setRoleHistoryLoading] = useState(true);
  const [roleHistoryError, setRoleHistoryError] = useState(null);

  useEffect(() => {
    if (user) {
      setEditForm({
        full_name: user.full_name || "",
        email: user.email || "",
        is_verified: Boolean(user.is_verified),
      });
    }
  }, [user]);

  useEffect(() => {
    if (!userId) {
      setRoleHistoryLoading(false);
      return;
    }

    let isMounted = true;

    const fetchRoleHistory = async () => {
      try {
        setRoleHistoryLoading(true);
        setRoleHistoryError(null);
        const response = await axiosPrivate.get(`/admin/users/${userId}/role-history`, {
          params: { page: 1, size: 10 },
        });
        if (!isMounted) return;
        const { changes = [] } = response.data || {};
        setRoleHistory(changes);
      } catch (err) {
        if (!isMounted) return;
        setRoleHistoryError(
          err.response?.data?.detail || err.message || "Failed to load role history"
        );
      } finally {
        if (isMounted) {
          setRoleHistoryLoading(false);
        }
      }
    };

    fetchRoleHistory();

    return () => {
      isMounted = false;
    };
  }, [axiosPrivate, userId]);

  const handleInputChange = (event) => {
    const { name, value, type, checked } = event.target;
    setEditForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!user) return;
    try {
      const response = await updateUser(user.uuid, {
        full_name: editForm.full_name,
        email: editForm.email,
        is_verified: editForm.is_verified,
      });
      setUser(response?.data || user);
    } catch (err) {
      console.error("Failed to update user", err);
    }
  };

  const handleToggleStatus = async () => {
    if (!user) return;
    try {
      const response = await toggleStatus(user.uuid, !user.is_active);
      setUser(response?.data || { ...user, is_active: !user.is_active });
    } catch (err) {
      console.error("Failed to toggle status", err);
    }
  };

  const handleDeactivate = async () => {
    if (!user) return;
    try {
      const response = await deactivateUser(user.uuid);
      const updated = response?.data ? { ...user, ...response.data } : { ...user, is_active: false };
      setUser(updated);
    } catch (err) {
      console.error("Failed to deactivate user", err);
    }
  };

  const formatDate = (value) => {
    if (!value) return "—";
    const date = new Date(value);
    return date.toLocaleString();
  };

  const profile = user?.profile;
  const currentUserRole = auth?.user?.role || "";
  const currentUserUuid = auth?.user?.uuid || "";
  const normalizedCurrentRole = currentUserRole.toLowerCase();
  const normalizedTargetRole = (user?.role || "user").toLowerCase();

  const canManageThisUser = (() => {
    if (!user || !normalizedCurrentRole) return false;
    if (currentUserUuid && user.uuid && currentUserUuid === user.uuid) return false;

    if (normalizedCurrentRole === "super_admin") {
      return true;
    }

    if (normalizedCurrentRole === "admin") {
      if (normalizedTargetRole === "admin" || normalizedTargetRole === "super_admin") {
        return false;
      }
      // Admins can manage moderators and users (status, deactivate, etc.)
      return normalizedTargetRole === "moderator" || normalizedTargetRole === "user";
    }

    return false;
  })();

  const canChangeRole = normalizedCurrentRole === "super_admin";

  return (
    <>
      <Head title="User Details - Regular"></Head>
      <Content>
        <BlockHead size="sm">
          <BlockBetween>
            <BlockHeadContent>
              <BlockTitle tag="h3" page>
                Users / <strong className="text-primary small">{user?.full_name || "Loading"}</strong>
              </BlockTitle>
              <BlockDes className="text-soft">
                <ul className="list-inline">
                  <li>
                    User UUID: <span className="text-base">{user?.uuid || "—"}</span>
                  </li>
                  <li>
                    Last Login: <span className="text-base">{formatDate(user?.last_login)}</span>
                  </li>
                </ul>
              </BlockDes>
            </BlockHeadContent>
            <BlockHeadContent>
              <div className="d-flex gap-2">
                <Button color="light" outline className="bg-white" onClick={() => navigate(-1)}>
                  <Icon name="arrow-left"></Icon>
                  <span>Back</span>
                </Button>
                {canChangeRole && (
                  <Button color="primary" onClick={() => setRoleModalOpen(true)}>
                    <Icon name="user-check"></Icon>
                    <span>Change Role</span>
                  </Button>
                )}
              </div>
            </BlockHeadContent>
          </BlockBetween>
        </BlockHead>

        {error && (
          <div className="alert alert-danger" role="alert">
            {error}
          </div>
        )}

        {loading && (
          <Block>
            <Card className="card-bordered">
              <div className="card-inner">Loading user information...</div>
            </Card>
          </Block>
        )}

        {!loading && !user && !error && (
          <Block>
            <Card className="card-bordered">
              <div className="card-inner">User not found.</div>
            </Card>
          </Block>
        )}

        {user && (
          <>
            <Row className="g-gs">
              <Col xl="4">
                <Card className="card-bordered h-100">
                  <div className="card-inner text-center">
                    <UserAvatar className="xxl" theme="primary" text={findUpper(user.full_name || user.username || "U")} />
                    <div className="mt-3">
                      <h4>{user.full_name}</h4>
                      <p className="text-soft mb-1">{user.email}</p>
                      <Badge color="outline-info" className="text-capitalize" pill>
                        {formatRoleLabel(user.role)}
                      </Badge>
                      <div className="mt-2">
                        <Badge color={user.is_verified ? "success" : "warning"} pill>
                          {user.is_verified ? "Verified" : "Unverified"}
                        </Badge>
                        <Badge color={user.is_active ? "success" : "danger"} pill className="ms-1">
                          {user.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </div>
                    </div>
                    <div className="d-flex flex-column gap-2 mt-4">
                      <Button
                        color="primary"
                        disabled={statusLoading || deactivating || !canManageThisUser}
                        onClick={handleToggleStatus}
                      >
                        <Icon name="shuffle"></Icon>
                        <span>{user.is_active ? "Set Inactive" : "Activate"}</span>
                      </Button>
                      <Button
                        color="danger"
                        outline
                        disabled={!user.is_active || deactivating || !canManageThisUser}
                        onClick={handleDeactivate}
                      >
                        <Icon name="user-cross"></Icon>
                        <span>Deactivate Account</span>
                      </Button>
                    </div>
                  </div>
                </Card>
              </Col>
              <Col xl="8">
                <Card className="card-bordered h-100">
                  <div className="card-inner">
                    <BlockHead size="sm">
                      <BlockHeadContent>
                        <BlockTitle tag="h5">Edit User</BlockTitle>
                        <BlockDes className="text-soft">Update core profile details.</BlockDes>
                      </BlockHeadContent>
                    </BlockHead>
                    <form className="gy-3" onSubmit={handleSubmit}>
                      <Row className="g-3">
                        <Col md="6">
                          <div className="form-group">
                            <label className="form-label">Full Name</label>
                            <div className="form-control-wrap">
                              <input
                                type="text"
                                className="form-control"
                                name="full_name"
                                value={editForm.full_name}
                                onChange={handleInputChange}
                                required
                              />
                            </div>
                          </div>
                        </Col>
                        <Col md="6">
                          <div className="form-group">
                            <label className="form-label">Email Address</label>
                            <div className="form-control-wrap">
                              <input
                                type="email"
                                className="form-control"
                                name="email"
                                value={editForm.email}
                                onChange={handleInputChange}
                                required
                              />
                            </div>
                          </div>
                        </Col>
                        <Col md="6">
                          <div className="form-group">
                            <div className="form-check">
                              <input
                                className="form-check-input"
                                type="checkbox"
                                name="is_verified"
                                id="is_verified"
                                checked={editForm.is_verified}
                                onChange={handleInputChange}
                              />
                              <label className="form-check-label" htmlFor="is_verified">
                                Account Verified
                              </label>
                            </div>
                          </div>
                        </Col>
                      </Row>
                      <div className="pt-3">
                        <Button color="primary" type="submit" disabled={updating}>
                          <Icon name="save"></Icon>
                          <span>Save Changes</span>
                        </Button>
                      </div>
                    </form>
                  </div>
                </Card>
              </Col>
            </Row>

            <Row className="g-gs mt-1">
              <Col md="6">
                <Card className="card-bordered h-100">
                  <div className="card-inner">
                    <BlockHead size="sm">
                      <BlockHeadContent>
                        <BlockTitle tag="h6">Profile Details</BlockTitle>
                      </BlockHeadContent>
                    </BlockHead>
                    <ul className="gx-3 gy-1">
                      <li>
                        <span className="text-soft">Location:</span> {profile?.location || "—"}
                      </li>
                      <li>
                        <span className="text-soft">Website:</span> {profile?.website || "—"}
                      </li>
                      <li>
                        <span className="text-soft">Bio:</span> {profile?.bio || "—"}
                      </li>
                      <li>
                        <span className="text-soft">Twitter:</span> {profile?.twitter_handle || "—"}
                      </li>
                      <li>
                        <span className="text-soft">GitHub:</span> {profile?.github_handle || "—"}
                      </li>
                      <li>
                        <span className="text-soft">LinkedIn:</span> {profile?.linkedin_handle || "—"}
                      </li>
                    </ul>
                  </div>
                </Card>
              </Col>
              <Col md="6">
                <Card className="card-bordered h-100">
                  <div className="card-inner">
                    <BlockHead size="sm">
                      <BlockHeadContent>
                        <BlockTitle tag="h6">Account Metadata</BlockTitle>
                      </BlockHeadContent>
                    </BlockHead>
                    <ul className="gx-3 gy-1">
                      <li>
                        <span className="text-soft">Role:</span> {formatRoleLabel(user.role)}
                      </li>
                      <li>
                        <span className="text-soft">Status:</span> {user.is_active ? "Active" : "Inactive"}
                      </li>
                      <li>
                        <span className="text-soft">Created:</span> {formatDate(user.created_at)}
                      </li>
                      <li>
                        <span className="text-soft">Updated:</span> {formatDate(user.updated_at)}
                      </li>
                      <li>
                        <span className="text-soft">Last Login:</span> {formatDate(user.last_login)}
                      </li>
                    </ul>
                  </div>
                </Card>
              </Col>
            </Row>

            <Row className="g-gs mt-1">
              <Col md="6">
                <Card className="card-bordered h-100">
                  <div className="card-inner">
                    <BlockHead size="sm">
                      <BlockHeadContent>
                        <BlockTitle tag="h6">Role & Permissions</BlockTitle>
                        <BlockDes className="text-soft">
                          High-level summary of what this role can access.
                        </BlockDes>
                      </BlockHeadContent>
                    </BlockHead>
                    <ul className="gx-3 gy-1">
                      <li>
                        <span className="text-soft">Current Role:</span>{" "}
                        {formatRoleLabel(user.role)}
                      </li>
                      <li>
                        <span className="text-soft">Capabilities:</span>{" "}
                        {getRoleDescription(user.role)}
                      </li>
                      <li>
                        <span className="text-soft">Can be edited by you:</span>{" "}
                        {canManageThisUser ? "Yes" : "No (insufficient privileges)"}
                      </li>
                    </ul>
                  </div>
                </Card>
              </Col>
              <Col md="6">
                <Card className="card-bordered h-100">
                  <div className="card-inner">
                    <BlockHead size="sm">
                      <BlockHeadContent>
                        <BlockTitle tag="h6">Role History</BlockTitle>
                        <BlockDes className="text-soft">
                          The most recent changes to this user&apos;s role.
                        </BlockDes>
                      </BlockHeadContent>
                    </BlockHead>
                    {roleHistoryError && (
                      <div className="alert alert-warning" role="alert">
                        {roleHistoryError}
                      </div>
                    )}
                    {roleHistoryLoading ? (
                      <div>Loading role history...</div>
                    ) : roleHistory.length === 0 ? (
                      <div>No role changes have been recorded for this user yet.</div>
                    ) : (
                      <ul className="gx-3 gy-1">
                        {roleHistory.map((change) => {
                          const oldLabel = formatRoleLabel(change.old_role);
                          const newLabel = formatRoleLabel(change.new_role);
                          const changerName =
                            change.changed_by?.full_name ||
                            change.changed_by?.username ||
                            "Unknown";
                          return (
                            <li key={change.uuid}>
                              <span className="text-soft">
                                {formatDate(change.created_at)}:
                              </span>{" "}
                              <span className="text-capitalize">
                                {oldLabel} <Icon name="arrow-right"></Icon> {newLabel}
                              </span>
                              <span className="d-block text-soft small mt-1">
                                By {changerName}
                                {change.reason ? ` — ${change.reason}` : ""}
                              </span>
                            </li>
                          );
                        })}
                      </ul>
                    )}
                  </div>
                </Card>
              </Col>
            </Row>
          </>
        )}
      </Content>

      {user && canChangeRole && (
        <RoleModal
          isOpen={isRoleModalOpen}
          onClose={() => setRoleModalOpen(false)}
          userUuid={user.uuid}
          currentRole={user.role}
          onRoleChange={(updatedUser) => {
            setUser(updatedUser);
          }}
        />
      )}
    </>
  );
};

export default UserDetailsPage;
