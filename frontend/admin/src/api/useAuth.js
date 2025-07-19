import { useAuth as useAuthFromProvider } from "./AuthProvider";

const useAuth = () => {
    return useAuthFromProvider();
}

export default useAuth;