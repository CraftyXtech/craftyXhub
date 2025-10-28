import React, { Suspense, useEffect, useState, lazy } from "react";

// Libraries
import { Routes, Route, useLocation } from "react-router-dom";
import retina from "retinajs";
import { AnimatePresence } from "framer-motion";

// Context
import GlobalContext from "./Context/Context";
import { AuthProvider } from "./Components/auth/AuthProvider";

// Components
import ScrollToTopButton from "./Components/ScrollToTop";

// Home
const MagazinePage = lazy(() => import("./Pages/Home/Magazine"));
const FeaturedArticlesPage = lazy(() => import("./Pages/Home/FeaturedArticlesPage"));
const TrendingArticlesPage = lazy(() => import("./Pages/Home/TrendingArticlesPage"));

// Pages (demo element pages removed)



// Header (demo pages removed)

// Footer (demo pages removed)

// Model-Popup (demo pages removed)

// Icon Packs (demo pages removed)

// Page-Title (demo pages removed)

// Marketing pages (imports removed; files retained)

// Additional Pages (only keep NotFound and SearchResult)
const NotFoundPage = lazy(() => import("./Pages/404"));
const SearchResultPage = lazy(() => import("./Pages/AdditionalPages/SearchResultPage"));


const Privacy = lazy(() => import("./Pages/Privacy"));

// Blogs
const BlogListingPage = lazy(() => import("./Pages/Blogs/BlogListingPage"));
const CategoryPage = lazy(() => import("./Pages/Blogs/CategoryPage"));
const AuthorPage = lazy(() => import("./Pages/Blogs/AuthorPage"));

// Blogs Types
const PostDetails = lazy(() =>
  import("./Pages/Blogs/PostDetail/PostDetails")
);

// Posts Management
const CreatePost = lazy(() =>
  import("./Pages/Posts/CreatePost")
);
const UserPosts = lazy(() =>
  import("./Pages/User/UserPosts")
);
const Dashboard = lazy(() =>
  import("./Pages/User/Dashboard")
);

// User Profile & Social Features
const Followers = lazy(() =>
  import("./Pages/User/Followers")
);
const Following = lazy(() =>
  import("./Pages/User/Following")
);
const MediaLibrary = lazy(() =>
  import("./Pages/User/MediaLibrary")
);
const Bookmarks = lazy(() =>
  import("./Pages/User/Bookmarks")
);
const Profile = lazy(() =>
  import("./Pages/User/Profile")
);



// Auth Pages
const LoginPage = lazy(() => import("./Pages/auth/Login"));
const RegisterPage = lazy(() => import("./Pages/auth/Register"));
const ForgotPasswordPage = lazy(() => import("./Pages/auth/ForgotPassword"));
const AuthSuccessPage = lazy(() => import("./Pages/auth/AuthSuccess"));
const AuthFailurePage = lazy(() => import("./Pages/auth/AuthFailure"));

function App() {
  const [headerHeight, setHeaderHeight] = useState(0);
  const [footerHeight, setFooterHeight] = useState(0);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [customModal, setCustomModal] = useState({
    el: null,
    isOpen: false,
  });
  const location = useLocation();

  // RetinaJS
  useEffect(() => {
    window.addEventListener("load", retina(document.querySelectorAll("img")));
  }, []);

  useEffect(() => {
    setTimeout(() => {
      import("./Functions/Utilities").then((module) => {
        module.SetHeaderMenuPos();
        module.setDocumentFullHeight();
      });
    }, 1000);
  }, [location]);

  useEffect(() => {
    if (isModalOpen === true) {
      document.querySelector("body").classList.add("overflow-hidden");
    } else {
      document.querySelector("body").classList.remove("overflow-hidden");
    }
  }, [isModalOpen]);

  // Get the current location and set the window to top
  useEffect(() => {
    window.scrollTo({
      top: 0,
      left: 0,
      behavior: "instant",
    });
    setFooterHeight(0);
    setCustomModal({
      ...customModal,
      el: null,
      isOpen: false,
    });

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location]);

  return (
    <AuthProvider>
      <GlobalContext.Provider
        value={{
          headerHeight,
          setHeaderHeight,
          footerHeight,
          setFooterHeight,
          isModalOpen,
          setIsModalOpen,
          customModal,
          setCustomModal,
        }}
      >
        <div className="App" style={{ "--header-height": `${headerHeight}px` }}>
        {
          <main style={{ marginTop: headerHeight, marginBottom: footerHeight }}>
            <ScrollToTopButton />
            <AnimatePresence mode="wait">
              <Suspense fallback={<></>}>
                <Routes>
                  <Route path="/" element={<MagazinePage />} />
                  
                  {/* Featured and Trending Articles Routes */}
                  <Route 
                    path="/featured-articles" 
                    element={
                      <FeaturedArticlesPage
                        style={{ "--base-color": "#0038e3" }}
                      />
                    } 
                  />
                  <Route 
                    path="/trending-articles" 
                    element={
                      <TrendingArticlesPage
                        style={{ "--base-color": "#0038e3" }}
                      />
                    } 
                  />

                  {/* Demo header routes removed */}

                  {/* Demo footer routes removed */}

                  {/* Duplicate home route removed */}



                  {/* Demo elements routes removed */}

               

                 

                  {/* Blogs */}
                  <Route path="blog" element={<BlogListingPage />} />
                
                {/* Direct category routes */}
                <Route path="category/:categorySlug" element={<CategoryPage />} />

                  {/* Legacy blog type routes removed */}

                  {/* Create/Edit Post Route */}
                  <Route 
                    path="posts/create" 
                    element={
                      <CreatePost
                        style={{ "--base-color": "#0038e3" }}
                      />
                    } 
                  />

                  {/* Edit Post Route */}
                  <Route 
                    path="posts/edit/:uuid" 
                    element={
                      <CreatePost
                        style={{ "--base-color": "#0038e3" }}
                      />
                    } 
                  />

                  {/* User Dashboard Route */}
                  <Route 
                    path="dashboard" 
                    element={
                      <Dashboard
                        style={{ "--base-color": "#0038e3" }}
                      />
                    } 
                  />

                  {/* User Posts Route */}
                  <Route 
                    path="user/posts" 
                    element={
                      <UserPosts
                        style={{ "--base-color": "#0038e3" }}
                      />
                    } 
                  />

                  {/* Followers/Following now integrated into Dashboard */}

                  {/* Media Library Route */}
                  <Route 
                    path="user/media-library" 
                    element={
                      <MediaLibrary
                        style={{ "--base-color": "#0038e3" }}
                      />
                    } 
                  />



                  {/* User Bookmarks Route */}
                  <Route 
                    path="user/bookmarks" 
                    element={
                      <Bookmarks
                        style={{ "--base-color": "#0038e3" }}
                      />
                    } 
                  />

                  {/* User Profile Route */}
                  <Route 
                    path="profile" 
                    element={
                      <Profile
                        style={{ "--base-color": "#0038e3" }}
                      />
                    } 
                  />



                  {/* New Post Detail Route - Primary route for all blog posts */}
                  <Route 
                    path="posts/:slug" 
                    element={
                      <PostDetails
                        style={{ "--base-color": "#0038e3" }}
                      />
                    } 
                  />

                  {/* Legacy blog post route */}
                  <Route 
                    path="blog/post/:slug" 
                    element={
                      <PostDetails
                        style={{ "--base-color": "#0038e3" }}
                      />
                    } 
                  />

                  {/* Demo modal routes removed */}

                  {/* Icon pack demo routes removed */}

                  {/* Page title demo routes removed */}

                  {/* Legacy post layout route removed */}

                  {/* Marketing page routes removed (files retained for future) */}

                  {/* Auth Pages */}
                  <Route path="/auth">
                    <Route path="login" element={<LoginPage />} />
                    <Route path="register" element={<RegisterPage />} />
                    <Route path="forgot-password" element={<ForgotPasswordPage />} />
                    <Route path="success" element={<AuthSuccessPage />} />
                    <Route path="failure" element={<AuthFailurePage />} />
                  </Route>

                  {/* Additional demo pages removed */}
                  <Route
                    path="/page/search-result"
                    element={
                      <SearchResultPage style={{ "--base-color": "#0038e3" }} />
                    }
                  />
                  <Route path="*" element={<NotFoundPage />} />
                  <Route
                    path="/privacy"
                    element={<Privacy style={{ "--base-color": "#0038e3" }} />}
                  />
                </Routes>
              </Suspense>
            </AnimatePresence>
          </main>
        }
      </div>
    </GlobalContext.Provider>
    </AuthProvider>
  );
}

export default App;
