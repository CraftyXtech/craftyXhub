import React, { useMemo } from "react";
import { Outlet } from "react-router-dom";
import menu from "./sidebar/MenuData";
import Sidebar from "./sidebar/Sidebar";
import Head from "./head/Head";
import Header from "./header/Header";
import Footer from "./footer/Footer";
import AppRoot from "./global/AppRoot";
import AppMain from "./global/AppMain";
import AppWrap from "./global/AppWrap";
import useAuth from "@/api/useAuth";
import { filterMenuByRole } from "@/utils/roleUtils";

import FileManagerProvider from "@/pages/app/file-manager/components/Context";

const Layout = ({title, ...props}) => {
  const { auth } = useAuth();
  
  const filteredMenu = useMemo(() => {
    const userRole = auth?.user?.role;
    console.log('Auth object:', auth);
    console.log('User role from auth:', userRole);
    console.log('Full user object:', auth?.user);
    const filtered = filterMenuByRole(menu, userRole);
    console.log('Filtered menu items:', filtered.length);
    return filtered;
  }, [auth?.user?.role]);

  return (
    <FileManagerProvider>
      <Head title={!title && 'Loading'} />
      <AppRoot>
        <AppMain>
          <Sidebar menuData={filteredMenu} fixed />
          <AppWrap>
            <Header fixed />
              <Outlet />
            <Footer />
          </AppWrap>
        </AppMain>
      </AppRoot>
    </FileManagerProvider>
  );
};
export default Layout;
