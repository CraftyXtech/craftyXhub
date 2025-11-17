import React, { useContext, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { DropdownMenu, DropdownToggle, DropdownItem, UncontrolledDropdown } from "reactstrap";
import {
  Block,
  BlockBetween,
  BlockDes,
  BlockHead,
  BlockHeadContent,
  BlockTitle,
  Icon,
  Row,
  Col,
  UserAvatar,
  PaginationComponent,
  Button,
  DataTable,
  DataTableBody,
  DataTableHead,
  DataTableRow,
  DataTableItem,
  TooltipComponent,
  RSelect,
} from "@/components/Component";
import Content from "@/layout/content/Content";
import Head from "@/layout/head/Head";
import { bulkActionOptions, findUpper } from "@/utils/Utils";
import { UserContext } from "./UserContext";
import {
  useAdminUserStats,
  useDeactivateAdminUser,
  useToggleAdminUserStatus,
} from "@/api/adminUserHooks";
import useAuth from "@/api/useAuth";
import RoleModal from "./RoleModal";

const roleFilterOptions = [
  { value: "", label: "Any Role" },
  { value: "super_admin", label: "Super Admin" },
  { value: "admin", label: "Admin" },
  { value: "moderator", label: "Moderator" },
  { value: "user", label: "User" },
];

const statusFilterOptions = [
  { value: "", label: "Any Status" },
  { value: "active", label: "Active" },
  { value: "inactive", label: "Inactive" },
];

const pageSizeOptions = [10, 15, 25];

const UserListRegularPage = () => {
  const { contextData, meta, loading, error, params, setParams, refetch } = useContext(UserContext);
  const [contextUsers] = contextData;

  const { auth } = useAuth();
  const currentUserRole = auth?.user?.role || "";
  const currentUserUuid = auth?.user?.uuid || "";

  const [sm, updateSm] = useState(false);
  const [tablesm, updateTableSm] = useState(false);
  const [onSearch, setOnSearch] = useState(true);
  const [searchText, setSearchText] = useState(params.search || "");
  const [tableData, setTableData] = useState([]);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [actionText, setActionText] = useState("");
  const [roleFilter, setRoleFilter] = useState(params.role || "");
  const [statusFilter, setStatusFilter] = useState(params.status || "");
  const [sortDirection, setSortDirection] = useState(params.sort === "full_name" ? "asc" : "dsc");
  const [roleModalOpen, setRoleModalOpen] = useState(false);
  const [selectedUserForRole, setSelectedUserForRole] = useState(null);

  const { mutate: toggleStatus, loading: statusMutating } = useToggleAdminUserStatus();
  const { mutate: deactivateUser, loading: deactivateMutating } = useDeactivateAdminUser();
  const {
    stats,
    loading: statsLoading,
    error: statsError,
  } = useAdminUserStats();
  const isMutating = statusMutating || deactivateMutating;

  const normalizedCurrentRole = currentUserRole.toLowerCase();

  const canManageUser = (user) => {
    if (!normalizedCurrentRole) return false;

    const targetRole = (user.raw?.role || "user").toLowerCase();
    const targetUuid = user.raw?.uuid || user.uuid || user.id || "";

    // Never allow changing own account from here
    if (currentUserUuid && targetUuid && currentUserUuid === targetUuid) {
      return false;
    }

    if (normalizedCurrentRole === "super_admin") {
      return true;
    }

    if (normalizedCurrentRole === "admin") {
      // Admins cannot touch admins or super-admins
      if (targetRole === "admin" || targetRole === "super_admin") {
        return false;
      }
      // Admins can manage moderators and users (status, deactivate, etc.)
      return targetRole === "moderator" || targetRole === "user";
    }

    // Moderators and users cannot manage accounts here (route is admin only, but keep safe)
    return false;
  };

  useEffect(() => {
    setSearchText(params.search || "");
  }, [params.search]);

  useEffect(() => {
    setRoleFilter(params.role || "");
  }, [params.role]);

  useEffect(() => {
    setStatusFilter(params.status || "");
  }, [params.status]);

  useEffect(() => {
    const reset = (contextUsers || []).map((user) => ({ ...user, checked: false }));
    setTableData(reset);
    setSelectedIds(new Set());
  }, [contextUsers]);

  useEffect(() => {
    const handler = setTimeout(() => {
      const normalized = searchText.trim();
      const sanitized = normalized === "" ? undefined : normalized;
      if ((params.search || undefined) === sanitized) {
        return;
      }
      setParams((prev) => {
        const next = { ...prev, page: 1 };
        if (sanitized) {
          next.search = sanitized;
        } else {
          delete next.search;
        }
        return next;
      });
    }, 400);

    return () => clearTimeout(handler);
  }, [searchText, params.search, setParams]);

  const handleRoleFilterChange = (option) => {
    const value = option?.value || "";
    setRoleFilter(value);
    setParams((prev) => {
      const next = { ...prev, page: 1 };
      if (value) {
        next.role = value;
      } else {
        delete next.role;
      }
      return next;
    });
  };

  const handleStatusFilterChange = (option) => {
    const value = option?.value || "";
    setStatusFilter(value);
    setParams((prev) => {
      const next = { ...prev, page: 1 };
      if (value) {
        next.status = value;
      } else {
        delete next.status;
      }
      return next;
    });
  };

  const resetFilters = () => {
    setRoleFilter("");
    setStatusFilter("");
    setParams((prev) => {
      const next = { ...prev, page: 1 };
      delete next.role;
      delete next.status;
      return next;
    });
  };

  const toggleSearch = () => setOnSearch((prev) => !prev);

  const handleSortChange = (direction) => {
    setSortDirection(direction);
    const sortValue = direction === "asc" ? "full_name" : "-full_name";
    setParams((prev) => ({ ...prev, sort: sortValue, page: 1 }));
  };

  const handlePageChange = (pageNumber) => {
    const totalPages = meta?.pages || 0;
    if (pageNumber < 1 || pageNumber === meta.page || (totalPages && pageNumber > totalPages)) {
      return;
    }
    setParams((prev) => ({ ...prev, page: pageNumber }));
  };

  const handlePageSizeChange = (size) => {
    if (size === params.size) return;
    setParams((prev) => ({ ...prev, size, page: 1 }));
  };

  const selectorCheck = (e) => {
    const checked = e.target.checked;
    if (checked) {
      const ids = new Set(tableData.filter((user) => canManageUser(user)).map((user) => user.id));
      setSelectedIds(ids);
      setTableData((prev) =>
        prev.map((user) => ({ ...user, checked: canManageUser(user) ? true : false }))
      );
    } else {
      setSelectedIds(new Set());
      setTableData((prev) => prev.map((user) => ({ ...user, checked: false })));
    }
  };

  const onSelectChange = (e, id) => {
    const checked = e.target.checked;
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (checked) {
        next.add(id);
      } else {
        next.delete(id);
      }
      return next;
    });
    setTableData((prev) => prev.map((user) => (user.id === id ? { ...user, checked } : user)));
  };

  const onActionText = (option) => setActionText(option?.value || "");

  const handleBulkAction = async () => {
    if (!actionText || selectedIds.size === 0) return;
    try {
      if (actionText === "suspend") {
        await Promise.all([...selectedIds].map((id) => toggleStatus(id, false)));
      } else if (actionText === "delete") {
        await Promise.all([...selectedIds].map((id) => deactivateUser(id)));
      }
      setActionText("");
      setSelectedIds(new Set());
      refetch();
    } catch (err) {
      console.error("Bulk action failed", err);
    }
  };

  const handleToggleUserStatus = async (user) => {
    try {
      await toggleStatus(user.id, !user.raw?.is_active);
      refetch();
    } catch (err) {
      console.error("Failed to toggle status", err);
    }
  };

  const handleDeactivateUser = async (user) => {
    try {
      await deactivateUser(user.id);
      refetch();
    } catch (err) {
      console.error("Failed to deactivate user", err);
    }
  };

  const formatLastLogin = (value) => {
    if (!value) return "—";
    const date = new Date(value);
    return `${date.toLocaleDateString()} ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
  };

  const totalUsers = meta?.total ?? 0;
  const currentItems = tableData;
  const selectedRoleOption = useMemo(
    () => roleFilterOptions.find((option) => option.value === roleFilter) || null,
    [roleFilter]
  );
  const selectedStatusOption = useMemo(
    () => statusFilterOptions.find((option) => option.value === statusFilter) || null,
    [statusFilter]
  );
  const selectedBulkOption = useMemo(
    () => bulkActionOptions.find((option) => option.value === actionText) || null,
    [actionText]
  );

  const openRoleModal = (user) => {
    if (!canManageUser(user)) return;
    setSelectedUserForRole(user);
    setRoleModalOpen(true);
  };

  const closeRoleModal = () => {
    setRoleModalOpen(false);
    setSelectedUserForRole(null);
  };

  const handleRoleUpdated = (updatedUser) => {
    if (!updatedUser?.uuid || !updatedUser?.role) return;
    const displayRole = updatedUser.role.charAt(0).toUpperCase() + updatedUser.role.slice(1);

    setTableData((prev) =>
      prev.map((user) =>
        user.id === updatedUser.uuid
          ? {
              ...user,
              role: displayRole,
              raw: updatedUser,
            }
          : user
      )
    );
    refetch();
  };

  return (
    <React.Fragment>
      <Head title="User List - Regular"></Head>
      <Content>
        <BlockHead size="sm">
          <BlockBetween>
            <BlockHeadContent>
              <BlockTitle tag="h3" page>
                User List
              </BlockTitle>
              <BlockDes className="text-soft">
                <p>You have total {totalUsers} users.</p>
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
                      <Button color="light" outline className="btn-white">
                        <Icon name="download-cloud"></Icon>
                        <span>Export</span>
                      </Button>
                    </li>
                  </ul>
                </div>
              </div>
            </BlockHeadContent>
          </BlockBetween>
        </BlockHead>

        {statsError && (
          <div className="alert alert-warning" role="alert">
            Failed to load user statistics: {statsError}
          </div>
        )}

        {!statsLoading && stats && (
          <>
            <Row className="g-gs mb-3">
              <Col sm="6" xl="3">
                <div className="card card-bordered">
                  <div className="card-inner">
                    <span className="text-soft">Total Users</span>
                    <div className="h4 mb-0">{stats.total_users}</div>
                  </div>
                </div>
              </Col>
              <Col sm="6" xl="3">
                <div className="card card-bordered">
                  <div className="card-inner">
                    <span className="text-soft">Active</span>
                    <div className="h4 mb-0 text-success">{stats.active_users}</div>
                  </div>
                </div>
              </Col>
              <Col sm="6" xl="3">
                <div className="card card-bordered">
                  <div className="card-inner">
                    <span className="text-soft">Inactive</span>
                    <div className="h4 mb-0 text-danger">{stats.inactive_users}</div>
                  </div>
                </div>
              </Col>
              <Col sm="6" xl="3">
                <div className="card card-bordered">
                  <div className="card-inner">
                    <span className="text-soft">Signups (30d)</span>
                    <div className="h4 mb-0">{stats.recent_registrations}</div>
                  </div>
                </div>
              </Col>
            </Row>
            <Row className="g-gs mb-3">
              <Col sm="6" xl="4">
                <div className="card card-bordered">
                  <div className="card-inner">
                    <span className="text-soft">Admins</span>
                    <div className="h4 mb-0">{stats.admin_count}</div>
                  </div>
                </div>
              </Col>
              <Col sm="6" xl="4">
                <div className="card card-bordered">
                  <div className="card-inner">
                    <span className="text-soft">Moderators</span>
                    <div className="h4 mb-0">{stats.moderator_count}</div>
                  </div>
                </div>
              </Col>
              <Col sm="6" xl="4">
                <div className="card card-bordered">
                  <div className="card-inner">
                    <span className="text-soft">Standard Users</span>
                    <div className="h4 mb-0">{stats.user_count}</div>
                  </div>
                </div>
              </Col>
            </Row>
          </>
        )}

        <Block>
          <DataTable className="card-stretch">
            <div className="card-inner position-relative card-tools-toggle">
              <div className="card-title-group">
                <div className="card-tools">
                  <div className="form-inline flex-nowrap gx-3">
                    <div className="form-wrap">
                      <RSelect
                        options={bulkActionOptions}
                        className="w-130px"
                        placeholder="Bulk Action"
                        value={selectedBulkOption}
                        onChange={onActionText}
                      />
                    </div>
                    <div className="btn-wrap">
                      <span className="d-none d-md-block">
                        <Button
                          disabled={selectedIds.size === 0 || !actionText || isMutating}
                          color="light"
                          outline
                          className="btn-dim"
                          onClick={handleBulkAction}
                        >
                          Apply
                        </Button>
                      </span>
                      <span className="d-md-none">
                        <Button
                          color="light"
                          outline
                          disabled={selectedIds.size === 0 || !actionText || isMutating}
                          className="btn-dim btn-icon"
                          onClick={handleBulkAction}
                        >
                          <Icon name="arrow-right"></Icon>
                        </Button>
                      </span>
                    </div>
                  </div>
                </div>
                <div className="card-tools me-n1">
                  <ul className="btn-toolbar gx-1">
                    <li>
                      <a
                        href="#search"
                        onClick={(ev) => {
                          ev.preventDefault();
                          toggleSearch();
                        }}
                        className="btn btn-icon search-toggle toggle-search"
                      >
                        <Icon name="search"></Icon>
                      </a>
                    </li>
                    <li className="btn-toolbar-sep"></li>
                    <li>
                      <div className="toggle-wrap">
                        <Button
                          className={`btn-icon btn-trigger toggle ${tablesm ? "active" : ""}`}
                          onClick={() => updateTableSm(true)}
                        >
                          <Icon name="menu-right"></Icon>
                        </Button>
                        <div className={`toggle-content ${tablesm ? "content-active" : ""}`}>
                          <ul className="btn-toolbar gx-1">
                            <li className="toggle-close">
                              <Button className="btn-icon btn-trigger toggle" onClick={() => updateTableSm(false)}>
                                <Icon name="arrow-left"></Icon>
                              </Button>
                            </li>
                            <li>
                              <UncontrolledDropdown>
                                <DropdownToggle tag="a" className="btn btn-trigger btn-icon dropdown-toggle">
                                  <div className="dot dot-primary"></div>
                                  <Icon name="filter-alt"></Icon>
                                </DropdownToggle>
                                <DropdownMenu end className="filter-wg dropdown-menu-xl" style={{ overflow: "visible" }}>
                                  <div className="dropdown-head">
                                    <span className="sub-title dropdown-title">Filter Users</span>
                                    <a
                                      href="#more"
                                      onClick={(ev) => {
                                        ev.preventDefault();
                                      }}
                                      className="btn btn-sm btn-icon btn-trigger"
                                    >
                                      <Icon name="more-h"></Icon>
                                    </a>
                                  </div>
                                  <div className="dropdown-body dropdown-body-rg">
                                    <Row className="gx-6 gy-3">
                                      <Col size="6">
                                        <div className="form-group">
                                          <label className="overline-title overline-title-alt">Role</label>
                                          <RSelect
                                            options={roleFilterOptions}
                                            placeholder="Any Role"
                                            value={selectedRoleOption}
                                            onChange={handleRoleFilterChange}
                                          />
                                        </div>
                                      </Col>
                                      <Col size="6">
                                        <div className="form-group">
                                          <label className="overline-title overline-title-alt">Status</label>
                                          <RSelect
                                            options={statusFilterOptions}
                                            placeholder="Any Status"
                                            value={selectedStatusOption}
                                            onChange={handleStatusFilterChange}
                                          />
                                        </div>
                                      </Col>
                                      <Col size="12">
                                        <div className="form-group text-end">
                                          <Button size="sm" color="secondary" onClick={resetFilters}>
                                            Reset Filters
                                          </Button>
                                        </div>
                                      </Col>
                                    </Row>
                                  </div>
                                  <div className="dropdown-foot between">
                                    <span className="small">Filters apply immediately</span>
                                    <a
                                      href="#save"
                                      onClick={(ev) => {
                                        ev.preventDefault();
                                      }}
                                    >
                                      Save Filter
                                    </a>
                                  </div>
                                </DropdownMenu>
                              </UncontrolledDropdown>
                            </li>
                            <li>
                              <UncontrolledDropdown>
                                <DropdownToggle color="tranparent" className="btn btn-trigger btn-icon dropdown-toggle">
                                  <Icon name="setting"></Icon>
                                </DropdownToggle>
                                <DropdownMenu end className="dropdown-menu-xs">
                                  <ul className="link-check">
                                    <li>
                                      <span>Show</span>
                                    </li>
                                    {pageSizeOptions.map((size) => (
                                      <li className={params.size === size ? "active" : ""} key={size}>
                                        <DropdownItem
                                          tag="a"
                                          href="#dropdownitem"
                                          onClick={(ev) => {
                                            ev.preventDefault();
                                            handlePageSizeChange(size);
                                          }}
                                        >
                                          {size}
                                        </DropdownItem>
                                      </li>
                                    ))}
                                  </ul>
                                  <ul className="link-check">
                                    <li>
                                      <span>Order</span>
                                    </li>
                                    <li className={sortDirection === "dsc" ? "active" : ""}>
                                      <DropdownItem
                                        tag="a"
                                        href="#dropdownitem"
                                        onClick={(ev) => {
                                          ev.preventDefault();
                                          handleSortChange("dsc");
                                        }}
                                      >
                                        DESC
                                      </DropdownItem>
                                    </li>
                                    <li className={sortDirection === "asc" ? "active" : ""}>
                                      <DropdownItem
                                        tag="a"
                                        href="#dropdownitem"
                                        onClick={(ev) => {
                                          ev.preventDefault();
                                          handleSortChange("asc");
                                        }}
                                      >
                                        ASC
                                      </DropdownItem>
                                    </li>
                                  </ul>
                                </DropdownMenu>
                              </UncontrolledDropdown>
                            </li>
                          </ul>
                        </div>
                      </div>
                    </li>
                  </ul>
                </div>
              </div>
              <div className={`card-search search-wrap ${!onSearch && "active"}`}>
                <div className="card-body">
                  <div className="search-content">
                    <Button
                      className="search-back btn-icon toggle-search active"
                      onClick={() => {
                        setSearchText("");
                        toggleSearch();
                      }}
                    >
                      <Icon name="arrow-left"></Icon>
                    </Button>
                    <input
                      type="text"
                      className="border-transparent form-focus-none form-control"
                      placeholder="Search by name or email"
                      value={searchText}
                      onChange={(e) => setSearchText(e.target.value)}
                    />
                    <Button className="search-submit btn-icon">
                      <Icon name="search"></Icon>
                    </Button>
                  </div>
                </div>
              </div>
            </div>
            {error && (
              <div className="alert alert-danger mb-0 mx-3" role="alert">
                {error}
              </div>
            )}
            <DataTableBody>
              <DataTableHead>
                <DataTableRow className="nk-tb-col-check">
                  <div className="custom-control custom-control-sm custom-checkbox notext">
                    <input type="checkbox" className="custom-control-input" onChange={selectorCheck} id="uid" />
                    <label className="custom-control-label" htmlFor="uid"></label>
                  </div>
                </DataTableRow>
                <DataTableRow>
                  <span className="sub-text">User</span>
                </DataTableRow>
                <DataTableRow size="md">
                  <span className="sub-text">Role</span>
                </DataTableRow>
                <DataTableRow size="md">
                  <span className="sub-text">Last Login</span>
                </DataTableRow>
                <DataTableRow size="sm">
                  <span className="sub-text">Status</span>
                </DataTableRow>
                <DataTableRow className="nk-tb-col-tools text-end">
                  <span className="sub-text">Actions</span>
                </DataTableRow>
              </DataTableHead>
              {loading ? (
                <DataTableItem>
                  <DataTableRow className="w-100 text-center py-4">
                    <div className="text-center w-100">Loading users...</div>
                  </DataTableRow>
                </DataTableItem>
              ) : currentItems.length > 0 ? (
                currentItems.map((item) => {
                  const detailLink = `/user-details-regular/${item.uuid || item.id}`;
                  const isActive = item.raw?.is_active;
                  const canManage = canManageUser(item);
                  const canChangeRole = normalizedCurrentRole === "super_admin";
                  return (
                    <DataTableItem key={item.id}>
                      <DataTableRow className="nk-tb-col-check">
                        <div className="custom-control custom-control-sm custom-checkbox notext">
                          <input
                            type="checkbox"
                            className="custom-control-input"
                            checked={item.checked && canManage}
                            onChange={canManage ? (e) => onSelectChange(e, item.id) : undefined}
                            disabled={!canManage}
                            id={`${item.id}-uid`}
                          />
                          <label className="custom-control-label" htmlFor={`${item.id}-uid`}></label>
                        </div>
                      </DataTableRow>
                      <DataTableRow>
                        <Link to={detailLink}>
                          <div className="user-card">
                            <UserAvatar
                              className="sm"
                              theme={item.avatarBg || "primary"}
                              text={findUpper(item.name || "U")}
                            ></UserAvatar>
                            <div className="user-info">
                              <span className="tb-lead">
                                {item.name} <span className="dot dot-success d-md-none ms-1"></span>
                              </span>
                              <span>{item.email}</span>
                            </div>
                          </div>
                        </Link>
                      </DataTableRow>
                      <DataTableRow size="md">
                        <span className="badge badge-dim badge-info text-capitalize">{item.role || "user"}</span>
                      </DataTableRow>
                      <DataTableRow size="md">
                        <span className="tb-sub">{formatLastLogin(item.raw?.last_login)}</span>
                      </DataTableRow>
                      <DataTableRow size="sm">
                        <span className={`badge badge-dim ${isActive ? "badge-success" : "badge-danger"}`}>
                          {isActive ? "Active" : "Inactive"}
                        </span>
                      </DataTableRow>
                      <DataTableRow className="nk-tb-col-tools">
                        <ul className="nk-tb-actions gx-1">
                          <li className="nk-tb-action-hidden">
                            <TooltipComponent icon="eye" direction="top" text="View Details">
                              <Link to={detailLink} className="btn btn-trigger btn-icon">
                                <Icon name="eye"></Icon>
                              </Link>
                            </TooltipComponent>
                          </li>
                          <li className="nk-tb-action-hidden">
                            <TooltipComponent
                              icon="user-check"
                              direction="top"
                              text={isActive ? "Deactivate user" : "Activate user"}
                            >
                              <Button
                                className="btn btn-trigger btn-icon"
                                onClick={canManage ? () => handleToggleUserStatus(item) : undefined}
                                disabled={isMutating || !canManage}
                                color="transparent"
                              >
                                <Icon name={isActive ? "user-cross" : "user-check"}></Icon>
                              </Button>
                            </TooltipComponent>
                          </li>
                          <li>
                            <UncontrolledDropdown>
                              <DropdownToggle tag="a" className="dropdown-toggle btn btn-icon btn-trigger">
                                <Icon name="more-h"></Icon>
                              </DropdownToggle>
                              <DropdownMenu end>
                                <DropdownItem tag={Link} to={detailLink}>
                                  <Icon name="eye"></Icon>
                                  <span>View</span>
                                </DropdownItem>
                                {canChangeRole && (
                                  <DropdownItem
                                    href="#change-role"
                                    onClick={(ev) => {
                                      ev.preventDefault();
                                      if (canChangeRole) {
                                        openRoleModal(item);
                                      }
                                    }}
                                  >
                                    <Icon name="shield"></Icon>
                                    <span>Change Role</span>
                                  </DropdownItem>
                                )}
                                <DropdownItem
                                  href="#toggle"
                                  onClick={(ev) => {
                                    ev.preventDefault();
                                    if (canManage) {
                                      handleToggleUserStatus(item);
                                    }
                                  }}
                                  disabled={!canManage}
                                >
                                  <Icon name="repeat"></Icon>
                                  <span>{isActive ? "Set Inactive" : "Activate"}</span>
                                </DropdownItem>
                                <DropdownItem
                                  href="#deactivate"
                                  onClick={(ev) => {
                                    ev.preventDefault();
                                    if (canManage) {
                                      handleDeactivateUser(item);
                                    }
                                  }}
                                  disabled={!canManage}
                                >
                                  <Icon name="user-cross"></Icon>
                                  <span>Deactivate</span>
                                </DropdownItem>
                              </DropdownMenu>
                            </UncontrolledDropdown>
                          </li>
                        </ul>
                      </DataTableRow>
                    </DataTableItem>
                  );
                })
              ) : (
                <DataTableItem>
                  <DataTableRow className="w-100 text-center py-4">
                    <div className="text-center w-100">No users found</div>
                  </DataTableRow>
                </DataTableItem>
              )}
            </DataTableBody>
            <div className="card-inner">
              <PaginationComponent
                itemPerPage={params.size || 10}
                totalItems={totalUsers}
                paginate={handlePageChange}
                currentPage={meta?.page || 1}
              />
            </div>
          </DataTable>
        </Block>
        {selectedUserForRole && (
          <RoleModal
            isOpen={roleModalOpen}
            onClose={closeRoleModal}
            userUuid={selectedUserForRole.uuid}
            currentRole={selectedUserForRole.raw?.role || selectedUserForRole.role?.toLowerCase()}
            onRoleChange={handleRoleUpdated}
          />
        )}
      </Content>
    </React.Fragment>
  );
};

export default UserListRegularPage;
