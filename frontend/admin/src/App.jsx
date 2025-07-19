import Router from "./route/Index";
import { AuthProvider } from "./api/AuthProvider";

const App = () => {
  return (
      <AuthProvider>
        <Router />
      </AuthProvider>
  );
};
export default App;