
import axios from './axios';
import useAuth from './useAuth';
 
import { useNavigate } from "react-router-dom";
const useRefreshToken = () => {
    const { setAuth } = useAuth();
    const navigate = useNavigate();
    const refresh = async (auth) => {

console.log(auth);



        const req = {
            token: auth.accessToken,
            refreshToken: auth.refreshToken,
            tokenExpiration: auth.tokenExpiration
        }

        try {





            const headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + auth.accessToken
            }

            const response = await axios.post('/Token/refresh', req, {
                headers: headers
            }, {
                withCredentials: true
            });

          
            const resp = response.data;
            const accessToken = resp.token;
            const tokenExpiration = resp.tokenExpiration;
            const refreshToken = resp.refreshToken;
            const usertype = auth.usertype;
            const active = auth.active;
            const firstname = auth.firstname;
            const lastname = auth.lastname;
            const username = auth.username;
            const roles = auth.roles;
            setAuth(prev => {
                
                

              

                localStorage.setItem("token", { accessToken, tokenExpiration, refreshToken, usertype, active, firstname, lastname, username, roles })

                setAuth({ accessToken, tokenExpiration, refreshToken, usertype, active, firstname, lastname, username, roles });

                return { ...prev, accessToken: accessToken}
            });
            return accessToken;
        }
        catch (err) {
console.log(err);

              // navigate(`${process.env.PUBLIC_URL}/login`);
            return refresh;

        }


    }
    return refresh;
};

export default useRefreshToken;
