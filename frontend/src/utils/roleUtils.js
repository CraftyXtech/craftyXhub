/**
 * Role-based access control utilities
 * Ported from admin/src/utils/roleUtils.js
 */

const ROLE_ORDER = {
  user: 0,
  moderator: 1,
  admin: 2,
  super_admin: 3,
};

/**
 * Filter menu items based on user role
 * @param {Array} menuItems - Menu items with roles array
 * @param {string} userRole - Current user's role
 * @returns {Array} Filtered menu items
 */
export const filterMenuByRole = (menuItems, userRole) => {
  if (!userRole) {
    console.warn('No user role found. Defaulting to "user" role.');
    userRole = 'user';
  }

  const normalizedRole = userRole.toLowerCase();

  return menuItems
    .filter((item) => {
      // If item has no role restriction, show it to everyone
      if (!item.roles) return true;
      // Super admin can see everything
      if (normalizedRole === 'super_admin') return true;
      // Check if user's role is in the allowed roles
      return item.roles.includes(normalizedRole);
    })
    .map((item) => {
      if (item.children) {
        return {
          ...item,
          children: filterMenuByRole(item.children, userRole),
        };
      }
      return item;
    });
};

/**
 * Check if user has required role (with hierarchy support)
 * @param {string} userRole - User's current role
 * @param {string|Array} allowedRoles - Required role(s)
 * @returns {boolean}
 */
export const hasRole = (userRole, allowedRoles) => {
  if (!userRole || !allowedRoles) return false;

  const normalizedRole = userRole.toLowerCase();
  const userRank = ROLE_ORDER[normalizedRole];

  // Handle single role as minimum required
  if (typeof allowedRoles === 'string') {
    const minRequiredRank = ROLE_ORDER[allowedRoles.toLowerCase()];
    if (minRequiredRank === undefined || userRank === undefined) return false;
    return userRank >= minRequiredRank;
  }

  // Handle array of roles
  const normalizedAllowed = allowedRoles.map((r) => r.toLowerCase());

  // Direct match
  if (normalizedAllowed.includes(normalizedRole)) return true;

  // Super admin can access everything
  if (normalizedRole === 'super_admin') return true;

  // Single role in array = minimum required
  if (normalizedAllowed.length === 1) {
    const minRequiredRank = ROLE_ORDER[normalizedAllowed[0]];
    if (minRequiredRank === undefined || userRank === undefined) return false;
    return userRank >= minRequiredRank;
  }

  return false;
};

export const isAdmin = (userRole) => {
  const role = userRole?.toLowerCase();
  return role === 'admin' || role === 'super_admin';
};

export const isModerator = (userRole) => {
  const role = userRole?.toLowerCase();
  return role === 'moderator' || role === 'admin' || role === 'super_admin';
};

export const isUser = (userRole) => {
  return userRole?.toLowerCase() === 'user';
};

export const canAccessAdminFeatures = (userRole) => {
  return isAdmin(userRole);
};

export const canAccessModeratorFeatures = (userRole) => {
  return isModerator(userRole);
};
