// Helper function to generate social links from environment variables
const getSocialLinks = () => [
  import.meta.env.VITE_FACEBOOK_URL && {
    title: "facebook",
    link: import.meta.env.VITE_FACEBOOK_URL,
    icon: "fab fa-facebook-f",
  },
  import.meta.env.VITE_INSTAGRAM_URL && {
    title: "instagram",
    link: import.meta.env.VITE_INSTAGRAM_URL,
    icon: "fa-brands fa-instagram",
  },
  import.meta.env.VITE_TWITTER_URL && {
    title: "twitter",
    link: import.meta.env.VITE_TWITTER_URL,
    icon: "fa-brands fa-twitter",
  },
  import.meta.env.VITE_LINKEDIN_URL && {
    title: "linkedin",
    link: import.meta.env.VITE_LINKEDIN_URL,
    icon: "fa-brands fa-linkedin-in",
  },
  import.meta.env.VITE_DRIBBBLE_URL && {
    title: "dribbble",
    link: import.meta.env.VITE_DRIBBBLE_URL,
    icon: "fa-brands fa-dribbble",
  },
].filter(Boolean);

const TeamData01 = [
  {
    img: "https://via.placeholder.com/525x639",
    name: "Alexander Harvard",
    designation: "CO FOUNDER",
    social_links: getSocialLinks(),
  },
  {
    img: "https://via.placeholder.com/525x639",
    name: "Bryan Jonhson",
    designation: "MANAGER",
    social_links: getSocialLinks(),
  },
  {
    img: "https://via.placeholder.com/525x639",
    name: "Jemmy Watson",
    designation: "DESIGNER",
    social_links: getSocialLinks(),
  },
  {
    img: "https://via.placeholder.com/525x639",
    name: "Jeremy Dupont",
    designation: "MANAGER",
    social_links: getSocialLinks(),
  },
  {
    img: "https://via.placeholder.com/525x639",
    name: "Alexander Harvard",
    designation: "CO FOUNDER",
    social_links: getSocialLinks(),
  },
  {
    img: "https://via.placeholder.com/525x639",
    name: "Bryan Jonhson",
    designation: "MANAGER",
    social_links: getSocialLinks(),
  },
  {
    img: "https://via.placeholder.com/525x639",
    name: "Jemmy Watson",
    designation: "DESIGNER",
    social_links: getSocialLinks(),
  },
  {
    img: "https://via.placeholder.com/525x639",
    name: "Jeremy Dupont",
    designation: "MANAGER",
    social_links: getSocialLinks(),
  },
];

const TeamData02 = [
  {
    img: "https://via.placeholder.com/721x902",
    name: "Alexander Harvard",
    designation: "Operations officer",
    social_links: getSocialLinks(),
  },
  {
    img: "https://via.placeholder.com/721x902",
    name: "Bryan Jonhson",
    designation: "Graphic designer",
    social_links: getSocialLinks(),
  },
  {
    img: "https://via.placeholder.com/721x902",
    name: "Jeremy Dupont",
    designation: "Web developer",
    social_links: getSocialLinks(),
  },
];

const TeamData03 = [
  {
    img: "https://via.placeholder.com/375x460",
    name: "Alexander Harvard",
    designation: "GENERALIST CONSULTANT",
    social_links: getSocialLinks(),
  },
  {
    img: "https://via.placeholder.com/375x460",
    name: "Bryan Jonhson",
    designation: "SPECIALIST CONSULTANT",
    social_links: getSocialLinks(),
  },
  {
    img: "https://via.placeholder.com/375x460",
    name: "Jemmy Watson",
    designation: "FINANCIAL CONSULTANT",
    social_links: getSocialLinks(),
  },
  {
    img: "https://via.placeholder.com/375x460",
    name: "Jeremy Dupont",
    designation: "BUSINESS CONSULTANT",
    social_links: getSocialLinks(),
  },
];

const TeamData04 = [
  {
    img: "https://via.placeholder.com/800x1000",
    name: "JEMMY WATSON",
    designation: "GRAPHIC DESIGNER",
    title: "I AM CREATIVE",
    social_links: getSocialLinks(),
  },
  {
    img: "https://via.placeholder.com/800x1000",
    name: "JEREMY DUPONT",
    designation: "WEB DEVELOPER",
    title: "I AM TRENDY",
    social_links: getSocialLinks(),
  },
  {
    img: "https://via.placeholder.com/800x1000",
    name: "BRYAN JONHSON",
    designation: "OPERATIONS OFFICER",
    title: "I AM PANCTUAL",
    social_links: getSocialLinks(),
  },
];

const TeamData05 = [
  {
    img: "https://via.placeholder.com/800x1005",
    name: "JEMMY WATSON",
    designation: "BOOTCAMP TRAINER",
    social_links: getSocialLinks(),
  },
  {
    img: "https://via.placeholder.com/800x1005",
    name: "BRYAN JONHSON",
    designation: "CROSSFIT TRAINER",
    social_links: getSocialLinks(),
  },
  {
    img: "https://via.placeholder.com/800x1005",
    name: "JEREMY DUPONT",
    designation: "SPINNING TRAINER",
    social_links: getSocialLinks(),
  },
];

export { TeamData01, TeamData02, TeamData03, TeamData04, TeamData05 };
