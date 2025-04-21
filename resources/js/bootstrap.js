import axios from 'axios';
window.axios = axios;

window.axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

/**
 * We'll load the axios HTTP library which allows us to easily issue requests
 * to our Laravel back-end. This library automatically handles sending the
 * CSRF token as a header based on the value of the "XSRF" token cookie.
 */
window.axios.defaults.withCredentials = true;
window.axios.defaults.withXSRFToken = true; // Use this if available, otherwise manual setup below

// Optional: Manual XSRF Token setup if defaults.withXSRFToken is not supported/working
// import Cookies from 'js-cookie'; // You might need to npm install js-cookie
// const xsrfToken = Cookies.get('XSRF-TOKEN');
// if (xsrfToken) {
//     window.axios.defaults.headers.common['X-XSRF-TOKEN'] = decodeURIComponent(xsrfToken);
// }
