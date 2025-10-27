const menu = [
  {
    icon: "home",
    text: "Dashboard",
    link: "/",
  },
  /*{
    heading: "Pre-built Pages",
  },
  {
    icon: "tile-thumb",
    text: "Projects",
    subMenu: [
      {
        text: "Project Cards",
        link: "/project-card",
      },
      {
        text: "Project List",
        link: "/project-list",
      },
    ],
  }, */
  {
    icon: "users",
    text: "User Manage",
    subMenu: [
      {
        text: "User List - Regular",
        link: "/user-list-regular",
      },
      {
        text: "User List - Compact",
        link: "/user-list-compact",
      },
      {
        text: "User Details - Regular",
        link: "/user-details-regular/1",
      },
      {
        text: "User Profile - Regular",
        link: "/user-profile-regular",
      },
      {
        text: "User Contact - Card",
        link: "/user-contact-card",
      },
    ],
  },
  /*{
    icon: "file-docs",
    text: "AML / KYCs",
    subMenu: [
      {
        text: "KYC List - Regular",
        link: "/kyc-list-regular",
      },
      {
        text: "KYC Details - Regular",
        link: "/kyc-details-regular/UD01544",
      },
    ],
  },
  {
    icon: "tranx",
    text: "Transaction",
    subMenu: [
      {
        text: "Trans List - Basic",
        link: "/transaction-basic",
      },
    ],
  },
  
  {
    icon: "grid-alt",
    text: "Applications",
    subMenu: [
      {
        text: "Messages",
        link: "/app-messages",
      },
      {
        text: "Chats / Messenger",
        link: "/app-chat",
      },
      {
        text: "Inbox / Mail",
        link: "/app-inbox",
      },
      {
        text: "Calendar",
        link: "/app-calender",
      },
      {
        text: "File Manager",
        link: "/app-file-manager",
        badge: "new",
      },
      {
        text: "Kanban Board",
        link: "/app-kanban",
      },
    ],
  },
  */

  {
    icon: "file-text",
    text: "Posts Management",
    subMenu: [
      {
        text: "Create Post",
        link: "/posts-create",
      },
      {
        text: "Posts List",
        link: "/posts-list",
      },
      {
        text: "Categories",
        link: "/posts-categories",
      },
      {
        text: "Tags",
        link: "/posts-tags",
      },
      {
        text: "Statistics",
        link: "/posts-stats",
      },
    ],
  },
  {
    icon: "shield-check",
    text: "Content Moderation",
    subMenu: [
      {
        text: "Comment Moderation",
        link: "/moderation/comments",
      },
      {
        text: "Post Reports",
        link: "/moderation/reports",
      },
    ],
  },

  {
    icon: "file-docs",
    text: "Invoice",
    subMenu: [
      {
        text: "Invoice List",
        link: "/invoice-list",
      },
      {
        text: "Invoice Details",
        link: "/invoice-details/1",
      },
    ],
  },
  
  {
    icon: "img",
    text: "Image Gallery",
    link: "/image-gallery",
  },
  {
    heading: "Misc Pages",
  },
  
 ];
export default menu;
