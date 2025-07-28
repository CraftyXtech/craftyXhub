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

// Pages

const AccordionPage = lazy(() => import("./Pages/Elements/Accordion"));
const ButtonPage = lazy(() => import("./Pages/Elements/Button"));
const TeamPage = lazy(() => import("./Pages/Elements/Team"));
const TeamCarouselPage = lazy(() => import("./Pages/Elements/TeamCarousel"));
const ClientPage = lazy(() => import("./Pages/Elements/Clients"));
const ClientCarouselPage = lazy(() =>
  import("./Pages/Elements/ClientCarousel")
);
const SubscribePage = lazy(() => import("./Pages/Elements/Subscribe"));
const CallToActionPage = lazy(() => import("./Pages/Elements/CallToAction"));
const TabPage = lazy(() => import("./Pages/Elements/Tab"));
const GoogleMapPage = lazy(() => import("./Pages/Elements/GoogleMap"));
const ContactFormPage = lazy(() => import("./Pages/Elements/ContactForm"));
const ImageGalleryPage = lazy(() => import("./Pages/Elements/ImageGallery"));
const ProgressBarPage = lazy(() => import("./Pages/Elements/ProgressBar"));
const IconWithTextPage = lazy(() => import("./Pages/Elements/IconWithText"));
const OverLineIconBoxPage = lazy(() =>
  import("./Pages/Elements/OverLineIconBox")
);
const CustomIconWithTextPage = lazy(() =>
  import("./Pages/Elements/CustomIconWithText")
);
const CountersPage = lazy(() => import("./Pages/Elements/Counters"));
const CountDownPage = lazy(() => import("./Pages/Elements/CountDown"));
const PieChartPage = lazy(() => import("./Pages/Elements/PieChart"));
const FancyTextBoxPage = lazy(() => import("./Pages/Elements/FancyTextBox"));
const TextBoxPage = lazy(() => import("./Pages/Elements/TextBox"));
const FancyTextPage = lazy(() => import("./Pages/Elements/FancyText"));
const TestimonialsPage = lazy(() => import("./Pages/Elements/Testimonials"));
const TestimonialsCarouselPage = lazy(() =>
  import("./Pages/Elements/TestimonialsCarousel")
);
const VideoPage = lazy(() => import("./Pages/Elements/Video"));
const InteractiveBannersPage = lazy(() =>
  import("./Pages/Elements/InteractiveBanners")
);
const ServicesPage = lazy(() => import("./Pages/Elements/Services"));
const InfoBannerPage = lazy(() => import("./Pages/Elements/InfoBanner"));
const RotateBoxPage = lazy(() => import("./Pages/Elements/RotateBox"));
const ProcessStepPage = lazy(() => import("./Pages/Elements/ProcessStep"));
const InstagramPage = lazy(() => import("./Pages/Elements/Instagram"));
const ParallaxScrollingPage = lazy(() =>
  import("./Pages/Elements/ParallaxScrolling")
);
const TextSliderPage = lazy(() => import("./Pages/Elements/TextSlider"));
const HeadingPage = lazy(() => import("./Pages/Elements/Heading"));
const DropCapsPage = lazy(() => import("./Pages/Elements/DropCaps"));
const ColumnsPage = lazy(() => import("./Pages/Elements/Columns"));
const BlockquotePage = lazy(() => import("./Pages/Elements/Blockquote"));
const HighlightsPage = lazy(() => import("./Pages/Elements/Highlights"));
const MessageBoxPage = lazy(() => import("./Pages/Elements/MessageBox"));
const SocialIconsPage = lazy(() => import("./Pages/Elements/SocialIcons"));
const ListsPage = lazy(() => import("./Pages/Elements/Lists"));
const SeparatorsPage = lazy(() => import("./Pages/Elements/Separators"));
const PricingTablePage = lazy(() => import("./Pages/Elements/PricingTable"));
const ElementPage = lazy(() => import("./Pages/Elements"));



// Header
const TransparentHeaderPage = lazy(() =>
  import("./Pages/Header/TransparentHeaderPage")
);
const WhiteHeaderPage = lazy(() => import("./Pages/Header/WhiteHeaderPage"));
const DarkHeaderPage = lazy(() => import("./Pages/Header/DarkHeaderPage"));
const HeaderwithTopbarPage = lazy(() =>
  import("./Pages/Header/HeaderwithTopbarPage")
);
const HeaderWithPushPage = lazy(() =>
  import("./Pages/Header/HeaderWithPushPage")
);
const CenterNavigationPage = lazy(() =>
  import("./Pages/Header/CenterNavigationPage")
);
const CenterLogoPage = lazy(() => import("./Pages/Header/CenterLogoPage"));
const TopLogoPage = lazy(() => import("./Pages/Header/TopLogoPage"));
const OnePageNavigationPage = lazy(() =>
  import("./Pages/Header/OnePageNavigationPage")
);
const LeftMenuClassicPage = lazy(() =>
  import("./Pages/Header/LeftMenuClassicPage")
);
const LeftMenuModernPage = lazy(() =>
  import("./Pages/Header/LeftMenuModernPage")
);
const HeaderAlwaysFixedPage = lazy(() =>
  import("./Pages/Header/HeaderTypes/HeaderAlwaysFixedPage")
);
const HeaderResponsiveSticky = lazy(() =>
  import("./Pages/Header/HeaderTypes/HeaderResponsiveSticky")
);
const HeaderDisableFixed = lazy(() =>
  import("./Pages/Header/HeaderTypes/HeaderDisableFixed")
);
const HeaderReverseScroll = lazy(() =>
  import("./Pages/Header/HeaderTypes/HeaderReverseScroll")
);
const MobileMenuClassicPage = lazy(() =>
  import("./Pages/Header/MobileMenu/MobileMenuClassicPage")
);
const MobileMenuModernPage = lazy(() =>
  import("./Pages/Header/MobileMenu/MobileMenuModernPage")
);
const MobileMenuFullScreen = lazy(() =>
  import("./Pages/Header/MobileMenu/MobileMenuFullScreen")
);
const HamburgerMenuPage = lazy(() =>
  import("./Pages/Header/HamburgerMenu/HamburgerMenuPage")
);
const HamburgerMenuModernPage = lazy(() =>
  import("./Pages/Header/HamburgerMenu/HamburgerMenuModernPage")
);
const HamburgerMenuHalfPage = lazy(() =>
  import("./Pages/Header/HamburgerMenu/HamburgerMenuHalfPage")
);

// Footer
const FooterStyle05Page = lazy(() =>
  import("./Pages/Footer/FooterStyle05Page")
);

// Model-Popup
const ModalPopupPage = lazy(() => import("./Pages/ModalPopup"));
const SimpleModel = lazy(() => import("./Pages/ModelPopup/SimpleModel"));
const ContactFormModal = lazy(() =>
  import("./Pages/ModelPopup/ContactFormModal")
);
const SubscriptionModal = lazy(() =>
  import("./Pages/ModelPopup/SubscriptionModal")
);
const VimeoVideoModal = lazy(() =>
  import("./Pages/ModelPopup/VimeoVideoModal")
);
const YouTubeVideoModal = lazy(() =>
  import("./Pages/ModelPopup/YouTubeVideoModal")
);
const GoogleMapModal = lazy(() => import("./Pages/ModelPopup/GoogleMapModal"));

// Icon Packs
const IconsMindLinePage = lazy(() => import("./Pages/Icons/IconsMindIconPage"));
const IconsMindSolidPage = lazy(() =>
  import("./Pages/Icons/IconsMindSolidPage")
);
const FontAwesomeIconPage = lazy(() =>
  import("./Pages/Icons/FontAwesomeIconPage")
);
const FeatherIconPage = lazy(() => import("./Pages/Icons/FeatherIconPage"));
const EtLineIconPage = lazy(() => import("./Pages/Icons/EtLineIconPage"));
const SimplelineIconPage = lazy(() =>
  import("./Pages/Icons/SimplelineIconPage")
);
const ThemifyIconPage = lazy(() => import("./Pages/Icons/ThemifyIconPage"));
const AnimationPage = lazy(() => import("./Pages/Animation"));

// Page-Title
const LeftAlignmentPage = lazy(() =>
  import("./Pages/PageTitle/LeftAlignmentPage")
);
const RightAlignmentPage = lazy(() =>
  import("./Pages/PageTitle/RightAlignmentPage")
);
const CenterAlignmentPage = lazy(() =>
  import("./Pages/PageTitle/CenterAlignmentPage")
);
const ColorfulStylePage = lazy(() =>
  import("./Pages/PageTitle/ColorfulStylePage")
);
const ParallaxBackground = lazy(() =>
  import("./Pages/PageTitle/ParallaxBackground")
);
const SeparateBreadcrumbsPage = lazy(() =>
  import("./Pages/PageTitle/SeparateBreadcrumbsPage")
);
const GalleryBackgroundPage = lazy(() =>
  import("./Pages/PageTitle/GalleryBackgroundPage")
);
const BackgroundVideoPage = lazy(() =>
  import("./Pages/PageTitle/BackgroundVideoPage")
);
const MiniVersionPage = lazy(() => import("./Pages/PageTitle/MiniVersionPage"));
const BigTypographyPage = lazy(() =>
  import("./Pages/PageTitle/BigTypographyPage")
);
const PageTitle = lazy(() => import("./Pages/PageTitle"));

// About Pages
const AboutUsPage = lazy(() => import("./Pages/About/AboutUsPage"));

// Services Pages
const OurServicesPage = lazy(() => import("./Pages/Services/OurServicesPage"));

// Contact Pages
const ContactUsModernPage = lazy(() =>
  import("./Pages/Contact/ContactUsModernPage")
);

// Additional Pages
const LatestNewsPage = lazy(() =>
  import("./Pages/AdditionalPages/LatestNewsPage")
);
const OurTeamPage = lazy(() => import("./Pages/AdditionalPages/OurTeamPage"));

const PricingPackagesPage = lazy(() =>
  import("./Pages/AdditionalPages/PricingPackagesPage")
);
const NotFoundPage = lazy(() => import("./Pages/404"));
const MaintenancePage = lazy(() =>
  import("./Pages/AdditionalPages/MaintenancePage")
);
const ComingSoonPage = lazy(() =>
  import("./Pages/AdditionalPages/ComingSoonPage")
);
const ComingSoonV2Page = lazy(() =>
  import("./Pages/AdditionalPages/ComingSoonV2Page")
);
const FaqSPage = lazy(() => import("./Pages/AdditionalPages/FaqSPage"));
const SearchResultPage = lazy(() =>
  import("./Pages/AdditionalPages/SearchResultPage")
);


const Footer = lazy(() => import("./Pages/Footer"));
const Privacy = lazy(() => import("./Pages/Privacy"));

// Blogs
const BlogPage = lazy(() => import("./Pages/Blogs"));
const BlogListingPage = lazy(() => import("./Pages/Blogs/BlogListingPage"));
const CategoryPage = lazy(() => import("./Pages/Blogs/CategoryPage"));
const AuthorPage = lazy(() => import("./Pages/Blogs/AuthorPage"));

const BlogPostLayout04 = lazy(() =>
  import("./Pages/Blogs/LayoutPage/BlogPostLayout04")
);

// Blogs Types
const PostDetails = lazy(() =>
  import("./Pages/Blogs/PostDetail/PostDetails")
);

// Auth Pages
const LoginPage = lazy(() => import("./Pages/auth/Login"));
const RegisterPage = lazy(() => import("./Pages/auth/Register"));
const ForgotPasswordPage = lazy(() => import("./Pages/auth/ForgotPassword"));

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

                  {/* Headers */}
                  <Route path="headers">
                    <Route
                      path="transparent-header"
                      element={
                        <TransparentHeaderPage
                          style={{ "--base-color": "#0038e3" }}
                        />
                      }
                    />
                    <Route path="white-header" element={<WhiteHeaderPage />} />
                    <Route path="dark-header" element={<DarkHeaderPage />} />
                    <Route
                      path="header-with-top-bar"
                      element={
                        <HeaderwithTopbarPage
                          style={{ "--base-color": "#828282" }}
                        />
                      }
                    />
                    <Route
                      path="header-with-push"
                      element={
                        <HeaderWithPushPage
                          style={{ "--base-color": "#828282" }}
                        />
                      }
                    />
                    <Route
                      path="center-navigation"
                      element={<CenterNavigationPage />}
                    />{" "}
                    <Route path="center-logo" element={<CenterLogoPage />} />
                    <Route path="top-logo" element={<TopLogoPage />} />
                    <Route
                      path="one-page-navigation"
                      element={
                        <OnePageNavigationPage
                          style={{ "--base-color": "#f4d956" }}
                        />
                      }
                    />
                    <Route
                      path="header-always-fixed"
                      element={<HeaderAlwaysFixedPage />}
                    />{" "}
                    <Route
                      path="header-disable-fixed"
                      element={<HeaderDisableFixed />}
                    />
                    <Route
                      path="header-reverse-scroll"
                      element={<HeaderReverseScroll />}
                    />{" "}
                    <Route
                      path="header-responsive-sticky"
                      element={
                        <HeaderResponsiveSticky
                          style={{ "--base-color": "#fff" }}
                        />
                      }
                    />
                    <Route
                      path="left-menu-classic"
                      element={<LeftMenuClassicPage />}
                    />{" "}
                    <Route
                      path="left-menu-modern"
                      element={
                        <LeftMenuModernPage
                          style={{ "--base-color": "#c7da26" }}
                        />
                      }
                    />
                    <Route
                      path="mobile-menu-classic"
                      element={<MobileMenuClassicPage />}
                    />{" "}
                    <Route
                      path="mobile-menu-modern"
                      element={<MobileMenuModernPage />}
                    />
                    <Route
                      path="mobile-menu-full-screen"
                      element={<MobileMenuFullScreen />}
                    />{" "}
                    <Route
                      path="hamburger-menu"
                      element={<HamburgerMenuPage />}
                    />
                    <Route
                      path="hamburger-menu-modern"
                      element={
                        <HamburgerMenuModernPage
                          style={{ "--base-color": "#fff" }}
                        />
                      }
                    />
                    <Route
                      path="hamburger-menu-half"
                      element={
                        <HamburgerMenuHalfPage
                          style={{ "--base-color": "#fff" }}
                        />
                      }
                    />
                  </Route>

                  {/* Footers */}
                  <Route
                    path="footers"
                    element={<Footer style={{ "--base-color": "#0038e3" }} />}
                  >
                    <Route
                      path="footer-style-05"
                      element={
                        <FooterStyle05Page
                          style={{ "--base-color": "#0038e3" }}
                        />
                      }
                    />
                  </Route>

                  {/* Home Blog Pages */}
                  <Route
                    path="/home-magazine"
                    element={
                      <MagazinePage style={{ "--base-color": "#c89965" }} />
                    }
                  />



                  {/* Elements */}
                  <Route
                    path="elements"
                    element={
                      <ElementPage style={{ "--base-color": "#0038e3" }} />
                    }
                  >
                    <Route path="accordions" element={<AccordionPage />} />
                    <Route path="buttons" element={<ButtonPage />} />
                    <Route path="teams" element={<TeamPage />} />
                    <Route
                      path="team-carousel"
                      element={<TeamCarouselPage />}
                    />
                    <Route path="clients" element={<ClientPage />} />
                    <Route
                      path="client-carousel"
                      element={<ClientCarouselPage />}
                    />{" "}
                    <Route path="subscribe" element={<SubscribePage />} />
                    <Route
                      path="call-to-action"
                      element={<CallToActionPage />}
                    />
                    <Route path="tab" element={<TabPage />} />
                    <Route path="google-map" element={<GoogleMapPage />} />
                    <Route path="contact-form" element={<ContactFormPage />} />
                    <Route
                      path="image-gallery"
                      element={<ImageGalleryPage />}
                    />
                    <Route path="progress-bar" element={<ProgressBarPage />} />
                    <Route
                      path="icon-with-text"
                      element={<IconWithTextPage />}
                    />
                    <Route
                      path="overline-icon-box"
                      element={<OverLineIconBoxPage />}
                    />{" "}
                    <Route
                      path="custom-icon-with-text"
                      element={<CustomIconWithTextPage />}
                    />
                    <Route path="counters" element={<CountersPage />} />
                    <Route path="countdown" element={<CountDownPage />} />
                    <Route path="pie-chart" element={<PieChartPage />} />
                    <Route
                      path="fancy-text-box"
                      element={<FancyTextBoxPage />}
                    />
                    <Route path="text-box" element={<TextBoxPage />} />
                    <Route path="team" element={<TeamPage />} />
                    <Route path="fancy-text" element={<FancyTextPage />} />
                    <Route path="testimonials" element={<TestimonialsPage />} />
                    <Route
                      path="testimonials-carousel"
                      element={<TestimonialsCarouselPage />}
                    />{" "}
                    <Route path="video" element={<VideoPage />} />
                    <Route
                      path="interactive-banners"
                      element={<InteractiveBannersPage />}
                    />{" "}
                    <Route path="services" element={<ServicesPage />} />
                    <Route path="info-banner" element={<InfoBannerPage />} />
                    <Route path="rotate-box" element={<RotateBoxPage />} />
                    <Route path="process-step" element={<ProcessStepPage />} />
                    <Route path="instagram" element={<InstagramPage />} />
                    <Route
                      path="parallax-scrolling"
                      element={<ParallaxScrollingPage />}
                    />{" "}
                    <Route path="text-slider" element={<TextSliderPage />} />
                    <Route path="heading" element={<HeadingPage />} />
                    <Route path="dropcaps" element={<DropCapsPage />} />
                    <Route path="columns" element={<ColumnsPage />} />
                    <Route path="blockquote" element={<BlockquotePage />} />
                    <Route path="highlights" element={<HighlightsPage />} />
                    <Route path="message-box" element={<MessageBoxPage />} />
                    <Route path="social-icons" element={<SocialIconsPage />} />
                    <Route path="lists" element={<ListsPage />} />
                    <Route path="separators" element={<SeparatorsPage />} />
                    <Route
                      path="pricing-table"
                      element={<PricingTablePage />}
                    />
                  </Route>

               

                 

                  {/* Blogs */}
                  <Route path="blog" element={<BlogListingPage />} />
                                  <Route
                  path="blogs"
                  element={<BlogPage style={{ "--base-color": "#0038e3" }} />}
                >
                  <Route path="category">
                    <Route path=":category" element={<CategoryPage />} />
                  </Route>
                  <Route path="author">
                    <Route path=":author" element={<AuthorPage />} />
                  </Route>
                </Route>
                
                {/* Direct category routes */}
                <Route path="category">
                  <Route path=":categorySlug" element={<CategoryPage />} />
                </Route>

                  {/* Blogs Types */}
                  <Route path="blog-types">
                    <Route path="blog-standard-post">
                      <Route
                        path=":id"
                        element={
                          <PostDetails
                            style={{ "--base-color": "#0038e3" }}
                          />
                        }
                      />
                    </Route>
                  </Route>

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

                  {/* Model-Popup */}
                  <Route path="model-popup" element={<ModalPopupPage />}>
                    <Route path="simple-modal" element={<SimpleModel />} />
                    <Route
                      path="subscription"
                      element={<SubscriptionModal />}
                    />
                    <Route path="contact-form" element={<ContactFormModal />} />
                    <Route
                      path="youtube-video"
                      element={<YouTubeVideoModal />}
                    />
                    <Route path="vimeo-video" element={<VimeoVideoModal />} />
                    <Route path="Google-map" element={<GoogleMapModal />} />
                  </Route>

                  {/* Icon Packs */}
                  <Route path="iconsmindline" element={<IconsMindLinePage />} />
                  <Route
                    path="iconsmindsolid"
                    element={<IconsMindSolidPage />}
                  />
                  <Route path="ETlineicon" element={<EtLineIconPage />} />
                  <Route path="fontawesome" element={<FontAwesomeIconPage />} />
                  <Route path="feather" element={<FeatherIconPage />} />
                  <Route path="simple-line" element={<SimplelineIconPage />} />
                  <Route path="themify" element={<ThemifyIconPage />} />
                  <Route path="animation" element={<AnimationPage />} />

                  {/* Page-Title */}
                  <Route path="page-title" element={<PageTitle />}>
                    <Route
                      path="left-alignment"
                      element={<LeftAlignmentPage />}
                    />{" "}
                    <Route
                      path="right-alignment"
                      element={<RightAlignmentPage />}
                    />
                    <Route
                      path="center-alignment"
                      element={<CenterAlignmentPage />}
                    />{" "}
                    <Route
                      path="colorful-style"
                      element={<ColorfulStylePage />}
                    />
                    <Route
                      path="big-typography"
                      element={<BigTypographyPage />}
                    />{" "}
                    <Route
                      path="parallax-background"
                      element={<ParallaxBackground />}
                    />
                    <Route
                      path="separate-breadcrumbs"
                      element={<SeparateBreadcrumbsPage />}
                    />{" "}
                    <Route
                      path="gallery-background"
                      element={<GalleryBackgroundPage />}
                    />
                    <Route
                      path="background-video"
                      element={<BackgroundVideoPage />}
                    />{" "}
                    <Route path="mini-version" element={<MiniVersionPage />} />
                  </Route>

                  {/* PostLayout */}
                  <Route
                    path="/blogs/blog-post-layout-04"
                    element={<BlogPostLayout04 />}
                  />

                  {/*About Pages */}
                  <Route
                    path="/page/about-us"
                    element={
                      <AboutUsPage style={{ "--base-color": "#0038e3" }} />
                    }
                  />

                  {/* Services Pages */}
                  <Route
                    path="/page/our-services"
                    element={
                      <OurServicesPage style={{ "--base-color": "#0038e3" }} />
                    }
                  />

                  {/* Contact Pages */}
                  <Route
                    path="/page/contact-modern"
                    element={
                      <ContactUsModernPage
                        style={{ "--base-color": "#0038e3" }}
                      />
                    }
                  />

                  {/* Auth Pages */}
                  <Route path="/auth">
                    <Route path="login" element={<LoginPage />} />
                    <Route path="register" element={<RegisterPage />} />
                    <Route path="forgot-password" element={<ForgotPasswordPage />} />
                  </Route>

                  {/* Additional Pages */}
                  <Route
                    path="/page/our-team"
                    element={
                      <OurTeamPage style={{ "--base-color": "#0038e3" }} />
                    }
                  />
                  <Route
                    path="/page/latest-news"
                    element={
                      <LatestNewsPage style={{ "--base-color": "#0038e3" }} />
                    }
                  />
                  <Route
                    path="/page/pricing-packages"
                    element={
                      <PricingPackagesPage
                        style={{ "--base-color": "#0038e3" }}
                      />
                    }
                  />
                  <Route
                    path="/page/error-404"
                    element={
                      <NotFoundPage style={{ "--base-color": "#0038e3" }} />
                    }
                  />
                  <Route
                    path="/page/maintenance"
                    element={<MaintenancePage />}
                  />
                  <Route
                    path="/page/coming-soon"
                    element={<ComingSoonPage />}
                  />
                  <Route
                    path="/page/coming-soon-V2"
                    element={<ComingSoonV2Page />}
                  />
                  <Route
                    path="/page/faq-s"
                    element={<FaqSPage style={{ "--base-color": "#0038e3" }} />}
                  />
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
