const ROLE_ORDER = {
  user: 0,
  moderator: 1,
  admin: 2,
  super_admin: 3,
};

export const filterMenuByRole = (menuItems, userRole) => {
  // If no userRole provided, default to 'user' role for backward compatibility
  if (!userRole) {
    console.warn('No user role found in auth context. Please log out and log back in to refresh your session.');
    console.warn('Defaulting to "user" role for now.');
    userRole = 'user';
  }

  const normalizedRole = userRole.toLowerCase();
  console.log('Filtering menu for role:', normalizedRole);

  return menuItems
    .filter((item) => {
      // If item has no role restriction, show it to everyone
      if (!item.roles) return true;
      // Super admin can see everything regardless of explicit roles
      if (normalizedRole === "super_admin") return true;
      // Check if user's role is in the allowed roles
      const hasAccess = item.roles.includes(normalizedRole);
      if (!hasAccess) {
        console.log(`Hiding menu item "${item.text}" - requires roles:`, item.roles);
      }
      return hasAccess;
    })
    .map((item) => {
      if (item.subMenu) {
        return {
          ...item,
          subMenu: filterMenuByRole(item.subMenu, userRole),
        };
      }
      return item;
    });
};

export const hasRole = (userRole, allowedRoles) => {
  if (!userRole || !allowedRoles || allowedRoles.length === 0) return false;

  const normalizedRole = userRole.toLowerCase();
  const userRank = ROLE_ORDER[normalizedRole];
  const normalizedAllowed = allowedRoles.map((r) => r.toLowerCase());

  // Direct match still allowed
  if (normalizedAllowed.includes(normalizedRole)) {
    return true;
  }

  // Treat a single allowed role as the minimum required role in the hierarchy.
  // Example:
  //  - ['admin'] -> admin and super_admin
  //  - ['moderator'] -> moderator, admin, super_admin
  if (normalizedAllowed.length === 1) {
    const minRequiredRank = ROLE_ORDER[normalizedAllowed[0]];
    if (minRequiredRank === undefined || userRank === undefined) return false;
    return userRank >= minRequiredRank;
  }

  // Backwards compatibility for multiple roles arrays:
  // super_admin should be allowed anywhere a higher role exists.
  if (normalizedRole === "super_admin") {
    return true;
  }

  return false;
};

export const isAdmin = (userRole) => {
  const role = userRole?.toLowerCase();
  return role === "admin" || role === "super_admin";
};

export const isModerator = (userRole) => {
  const role = userRole?.toLowerCase();
  return role === "moderator" || role === "admin" || role === "super_admin";
};

export const isUser = (userRole) => {
  return userRole?.toLowerCase() === "user";
};

export const canAccessAdminFeatures = (userRole) => {
  return isAdmin(userRole);
};

export const canAccessModeratorFeatures = (userRole) => {
  return isAdmin(userRole) || isModerator(userRole);
};

