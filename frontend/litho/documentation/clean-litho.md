# Litho Cleanup Candidates (Draft)

Purpose: Identify template/demo files not required for CraftyXhub so we can review together before removal. This list is based on route mapping, imports, and current usage in `src/App.js` and core pages.

Review status: DRAFT – do not delete yet. We will confirm each item.

## Keep for future use (reusable building blocks)

These are generic, well-structured UI blocks that can speed up future features. Even if the current MVP doesn’t use them, they’re valuable to keep in the repo:

- Components/Form: `Input`, `TextArea`, `RichTextEditor` – forms across dashboard/profile/posting.
- Components/CustomModal.jsx – accessible modal wrapper for confirmations, media previews, etc.
- Components/Button/Buttons.jsx – brand-aware, versatile button with variants and icon support.
- Components/Instagram/Instagram.jsx – can repurpose as a generic carousel/gallery.
- Components/ImageGallery/\* – for future media features or post galleries.
- Components/Testimonials/_ and TestimonialCarousel/_ – can be adapted for quotes/endorsements.
- Components/PricingTable/\* – useful for future pricing/plan pages if we add memberships.
- Components/ProcessStep/_, OverlineIconBox/_, IconWithText/\* – good for onboarding/How‑it‑works sections.
- Components/Services/_, Team/_, Clients/\* – marketing pages if we introduce “About” later.
- Components/Tab/_, Accordion/_, Progressbar/_, Counters/_, PieChart/_, TextSlider/_ – utility UI patterns.
- Components/GoogleMap/GoogleMap.jsx – locations/contact if needed.
- Components/Overlap/Overlap.js – simple layout helper for featured sections.
- Pages/AdditionalPages/SearchResultPage.jsx – if we keep a dedicated search results screen.
- Pages/About/AboutUsPage.jsx, Services/OurServicesPage.jsx, Contact/ContactUsModernPage.jsx – retain as stubs for eventual marketing pages.
- Pages/ModelPopup/\* – reference patterns for embedding videos/forms in modals.
- Public icon packs and `src/Assets/css/icons.css` – keep until we fully standardize on Feather; deprecate gradually.

## Pages (likely removable)

- Headers demo pages (`src/Pages/Header/**`):

  - Reason: Demo-only variations (transparent, dark, center logo, mobile menu, hamburger, sticky, etc.). Not linked in product navigation; used only via demo routes.
  - Impact: None on blog flows. Keep `Components/Header/**` as they are used site-wide.

- Footers demo pages (`src/Pages/Footer/**`):

  - Reason: Style showcase routes; actual footer uses `Components/Footers/FooterStyle05.jsx`.
  - Impact: Safe; keep `Components/Footers/**` used by pages.

- Elements index and subpages (`src/Pages/Elements.jsx`, `src/Pages/Elements/**`):

  - Reason: Component gallery routes (accordion, pricing table, etc.). Not part of CraftyXhub UX.
  - Impact: Removing pages doesn’t affect components still imported elsewhere.

- Icon packs pages (`src/Pages/Icons/**`):

  - Reason: Library icon showcase; not needed for blog.
  - Impact: None.

- Page title demos (`src/Pages/PageTitle.jsx`, `src/Pages/PageTitle/**`):

  - Reason: Title layout showcase.
  - Impact: None.

- Additional template pages (`src/Pages/AdditionalPages/**`):

  - Candidates: `ComingSoon*`, `MaintenancePage`, `PricingPackagesPage`, `FaqSPage`, `LatestNewsPage`, `OurTeamPage`, `SearchResultPage` (confirm if search UI is needed).
  - Reason: Marketing/demo pages not tied to core blog flows.
  - Impact: None, except SearchResultPage – confirm if header search should land here.

- About/Services/Contact pages (`src/Pages/About/AboutUsPage.jsx`, `src/Pages/Services/OurServicesPage.jsx`, `src/Pages/Contact/ContactUsModernPage.jsx`):

  - Reason: Corporate pages; not in blog MVP scope.
  - Impact: Low; header links should not point to them in current menu.

- Modal demo pages (`src/Pages/ModelPopup/**`, `src/Pages/ModalPopup.jsx`):

  - Reason: Modal gallery pages; not used in product.
  - Impact: None.

- Legacy blog layout pages (`src/Pages/Blogs/LayoutPage/**`, `src/Pages/Blogs/PostTypes/**`):

  - Reason: Old demo layouts. Current blog uses `BlogListingPage.jsx`, `CategoryPage.jsx`, and `PostDetail/PostDetails.jsx`.
  - Impact: None.

- Followers/Following pages (`src/Pages/User/Followers.jsx`, `src/Pages/User/Following.jsx`):
  - Reason: Comment in `App.js` indicates these are integrated into Dashboard; routes exist but not used directly.
  - Action: Confirm removal or hide routes; `FollowButton.jsx` component remains if reused.

## Components (remove if not referenced by kept pages)

- Portfolio components (`src/Components/Portfolio/**`):

  - Reason: Only used by header/mobile demo pages; not in blog flows.

- Pricing tables (`src/Components/PricingTable/**`):

  - Reason: Only used by Elements/Services/Additional Pricing pages.

- Clients, Team, FancyTextBox, IconWithText, Counters, Overlap, ProcessStep, Testimonials, Instagram, InteractiveBanners, TextSlider, PieChart, Countdown, RotateBox, Tab, Lists, Dropcaps, MessageBox, InfoBanner, ImageGallery (some variants):

  - Reason: Primarily showcased via Elements/Headers/About/Services demos. Keep only if referenced by `Magazine.jsx`, `FeaturedArticlesPage.jsx`, `TrendingArticlesPage.jsx`, `Dashboard.jsx`, `BlogListingPage.jsx`, `CategoryPage.jsx`, `PostDetails.jsx`.
  - Current confirmed uses:
    - `Blogs/BlogClassic.jsx`, `Blogs/BlogMetro.jsx`, `Blogs/BlogWidget.jsx`, `Blogs/ContentRenderer.jsx`, `Blogs/BookmarkButton.jsx`, `Blogs/ReportModal.jsx` – KEEP.
    - `Header/**`, `Footers/FooterStyle05.jsx`, `Logo/**`, `Form/**`, `CustomModal.jsx` (used in About/Headers demos) – KEEP header/footer/logo/form; CustomModal used in About and header demos only.
    - `Instagram/Instagram.jsx` – USED in `Magazine.jsx`.

- PortfolioPlaceholder, TestimonialCarousel variants, Services styles, TeamStyle variants:

  - Reason: Demo-only. Remove with associated demo pages.

- `ProfileManagement.jsx` (component):

  - Reason: Possibly superseded by `Pages/User/Profile.jsx` and dashboard; confirm not imported in active pages.

- `MouseMove.jsx`, `Overlap/Overlap.js`:
  - Reason: Used by demo pages; remove if associated pages removed.

## API/Hooks/Utilities

- `src/api/*` – KEEP. Used across core pages (`usePosts`, `useAuth`, etc.).
- `src/Functions/*` – KEEP. Utilities used (animations, header menu position).
- `src/utils/dateUtils.js` – KEEP. Used in `PostDetails`.

## Public assets

- `public/assets/img/hero/*.jpg` – USED in `Magazine.jsx` hero slider.
- `public/assets/img/no-data-bro.svg` – USED in `CategoryPage.jsx`.
- Icon font files under `public/assets/fonts/**` – used by `icons.css` and components; KEEP for now. Can be pruned later if we standardize on Feather only.
- `public/assets/webp/**` – many template images referenced by demo pages; removable along with pages. Keep logos referenced by header/footer.
- `public/assets/css/loader.css` – referenced in `public/index.html`, but file not present under `public/assets/css`. Either remove the link or add the file. Recommend removal of link if unused.

## Server folder

- `frontend/litho/server/*` (Express mailer):
  - Reason: Frontend-only app; backend handled by FastAPI. Not used by React code.
  - Proposal: Remove entire `server/` directory.

## Routing candidates to delete from `src/App.js`

- Headers, Footers, Elements, Icons, Page-Title, ModalPopup routes
- AdditionalPages (ComingSoon, Maintenance, PricingPackages, FaqS, OurTeam, LatestNews) – unless required
- About, Services, Contact
- Legacy blog layout routes
- Followers/Following routes (if confirmed redundant)

## Keep list (core flows)

- Home: `Pages/Home/Magazine.jsx`, `Home/FeaturedArticlesPage.jsx`, `Home/TrendingArticlesPage.jsx`
- Blog: `Pages/Blogs/BlogListingPage.jsx`, `Pages/Blogs/CategoryPage.jsx`, `Pages/Blogs/AuthorPage.jsx` (if used), `Pages/Blogs/PostDetail/PostDetails.jsx`
- Posts: `Pages/Posts/CreatePost.jsx`
- User: `Pages/User/Dashboard.jsx`, `Pages/User/UserPosts.jsx`, `Pages/User/MediaLibrary.jsx`, `Pages/User/Bookmarks.jsx`, `Pages/User/Profile.jsx`
- Auth: `Pages/auth/*`
- Shared layout: `Components/Header/**`, `Components/Footers/FooterStyle05.jsx`, `Components/Logo/**`, `Components/Blogs/**`, `Components/Form/**`, `Components/Posts/**`

## Open questions for you

1. Should we keep a search results page (`AdditionalPages/SearchResultPage.jsx`) or switch header search to a simple navigate to `/blogs` with query filtering?
2. Remove Followers/Following pages and routes now that dashboard integrates them?
3. Are About/Services/Contact needed for CraftyXhub, or should we remove their pages and routes?
4. Do we standardize on Feather icons only and purge other icon font packs (FontAwesome, Themify, SimpleLine, etc.)?
5. Can we delete the `server/` directory (Express mailer) since FastAPI handles backend/email?

---

Actions taken:

- Removed demo pages/routes from routing (headers, footers, elements, icons, page-title, modals, legacy layouts, extra marketing routes). Kept `/page/search-result`.
- Disabled `Components/SideButtons.jsx` (no-op; removed Buy Now and 37 demos UI).
- Deleted demo page files under `src/Pages/Header/**`, `src/Pages/Footer/**`, `src/Pages/ModelPopup/**`, `src/Pages/Blogs/LayoutPage/**`.
- Removed `frontend/litho/server/` and stripped the unused loader link from `public/index.html`.
- Retained reusable components and future-use pages listed above.

All changes will be incremental with commits per group (routes → pages → components → assets) to reduce breakage.
