import Router from "./route/Index";
import { AuthProvider } from "./api/AuthProvider";
import { AiDraftProvider } from "./context/AiDraftContext";

const App = () => {
  return (
      <AuthProvider>
        <AiDraftProvider>
          <Router />
        </AiDraftProvider>
      </AuthProvider>
  );
};
export default App;