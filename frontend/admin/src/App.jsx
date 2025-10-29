import Router from "./route/Index";
import { AuthProvider } from "./api/AuthProvider";
import { AiDocumentProvider } from "./context/AiDocumentContext";

const App = () => {
  return (
      <AuthProvider>
        <AiDocumentProvider>
          <Router />
        </AiDocumentProvider>
      </AuthProvider>
  );
};
export default App;