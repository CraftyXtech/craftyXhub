import { describe, it, expect, beforeEach, vi } from "vitest";
import { userService } from "./userService";

vi.mock("./axios", () => {
  const mockAxios = {
    get: vi.fn(() => Promise.resolve({ data: {} })),
    post: vi.fn(() => Promise.resolve({ data: {} })),
    put: vi.fn(() => Promise.resolve({ data: {} })),
    patch: vi.fn(() => Promise.resolve({ data: {} })),
    delete: vi.fn(() => Promise.resolve({ data: {} })),
  };
  return { axiosPrivate: mockAxios };
});

// Import after mocking
import { axiosPrivate } from "./axios";

describe("userService admin methods", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("calls GET /admin/users with params when fetching users", async () => {
    const params = { page: 2, size: 20, search: "john" };
    await userService.getUsers(params);
    expect(axiosPrivate.get).toHaveBeenCalledWith("/admin/users", { params });
  });

  it("updates user status via PATCH request", async () => {
    await userService.toggleUserStatus("user-uuid", true);
    expect(axiosPrivate.patch).toHaveBeenCalledWith("/admin/users/user-uuid/status", {
      is_active: true,
    });
  });

  it("fetches admin user statistics", async () => {
    await userService.getUserStats();
    expect(axiosPrivate.get).toHaveBeenCalledWith("/admin/users/stats");
  });
});

