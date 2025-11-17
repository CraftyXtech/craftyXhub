import React, { useEffect, useMemo, useState, createContext } from "react";
import { Outlet } from "react-router-dom";
import { useGetAdminUsers } from "@/api/adminUserHooks";

export const UserContext = createContext({
  contextData: [[], () => {}],
  meta: { total: 0, page: 1, size: 10, pages: 0, has_next: false, has_prev: false },
  loading: false,
  error: null,
  params: { page: 1, size: 10 },
  setParams: () => {},
  refetch: () => {},
  rawUsers: [],
});

const adaptUserRecord = (user, index) => {
  const formatDate = (value) => {
    if (!value) return "—";
    const date = new Date(value);
    return date.toLocaleDateString();
  };

  return {
    id: user.uuid,
    uuid: user.uuid,
    avatarBg: "primary",
    name: user.full_name || user.username || `User ${index + 1}`,
    displayName: user.username || "",
    dob: user.profile?.birth_date ? formatDate(user.profile.birth_date) : "—",
    role: user.role ? user.role.charAt(0).toUpperCase() + user.role.slice(1) : "User",
    checked: false,
    email: user.email,
    balance: user.profile?.balance || "0.00",
    phone: user.profile?.phone || "—",
    emailStatus: user.is_verified ? "success" : "pending",
    kycStatus: user.is_verified ? "success" : "pending",
    lastLogin: formatDate(user.last_login),
    status: user.is_active ? "Active" : "Inactive",
    country: user.profile?.location || "—",
    designation: user.profile?.designation || "Member",
    projects: user.profile?.projects || "—",
    performed: user.profile?.performed || "—",
    tasks: user.profile?.tasks || "—",
    raw: user,
  };
};

export const UserContextProvider = () => {
  const [params, setParams] = useState({ page: 1, size: 10 });
  const { users, total, page, size, pages, has_next, has_prev, loading, error, refetch } =
    useGetAdminUsers(params);
  const [data, setData] = useState([]);

  useEffect(() => {
    const adapted = users.map((user, index) => adaptUserRecord(user, index));
    setData(adapted);
  }, [users]);

  const value = useMemo(
    () => ({
      contextData: [data, setData],
      meta: { total, page, size, pages, has_next, has_prev },
      loading,
      error,
      params,
      setParams,
      refetch,
      rawUsers: users,
    }),
    [data, total, page, size, pages, has_next, has_prev, loading, error, params, users, refetch]
  );

  return (
    <UserContext.Provider value={value}>
      <Outlet />
    </UserContext.Provider>
  );
};
