import defaultTheme from 'tailwindcss/defaultTheme';
import forms from '@tailwindcss/forms';

/** @type {import('tailwindcss').Config} */
export default {
    content: [
        './vendor/laravel/framework/src/Illuminate/Pagination/resources/views/*.blade.php',
        './storage/framework/views/*.php',
        './resources/views/**/*.blade.php',
        './resources/js/**/*.vue',
    ],

    theme: {
        extend: {
            colors: {
                primary: '#007bff',  // blue from original CSS
                'primary-dark': '#0056b3', // darker blue for hover
                secondary: '#6c757d', // gray from original CSS
                'dark': '#212529',
                'light': '#f8f9fa',
                'border': '#dee2e6',
                'text': '#495057',
            },
            fontFamily: {
                sans: ['Open Sans', 'Roboto', ...defaultTheme.fontFamily.sans],
                heading: ['Montserrat', ...defaultTheme.fontFamily.sans],
            },
            spacing: {
                'sm': '8px',
                'md': '16px',
                'lg': '24px',
                'xl': '32px',
            },
            maxWidth: {
                'container': '1200px',
            },
            typography: {
                DEFAULT: {
                    css: {
                        maxWidth: '1200px',
                        a: {
                            color: '#007bff',
                            '&:hover': {
                                color: '#0056b3',
                            },
                        },
                    },
                },
            },
        },
    },

    plugins: [forms],
};
