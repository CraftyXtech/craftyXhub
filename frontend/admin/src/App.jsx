import Router from "./route/Index";
import { AuthProvider } from "./api/AuthProvider";
import { AiDraftProvider } from "./context/AiDraftContext";
import { NotificationProvider } from "./context/NotificationContext";

const App = () => {
  return (
      <AuthProvider>
        <NotificationProvider>
          <AiDraftProvider>
            <Router />
          </AiDraftProvider>
        </NotificationProvider>
      </AuthProvider>
  );
};
export default App;