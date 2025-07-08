import './bootstrap';

import { createInertiaApp } from '@inertiajs/react';
import { resolvePageComponent } from 'laravel-vite-plugin/inertia-helpers';
import { createRoot } from 'react-dom/client';

// Libraries
import { ParallaxProvider } from 'react-scroll-parallax';
import { LazyMotion, domMax } from 'framer-motion';

// CSS imports following Litho template structure
import './Assets/css/icons.css';
import './Assets/css/global.css';
import './Assets/css/pages.css';
import '../css/app.css';
import './index.scss';

const appName = import.meta.env.VITE_APP_NAME || 'Laravel';

createInertiaApp({
    title: (title) => `${title} - ${appName}`,
    resolve: (name) =>
        resolvePageComponent(
            `./Pages/${name}.jsx`,
            import.meta.glob('./Pages/**/*.jsx'),
        ),
    setup({ el, App, props }) {
        const root = createRoot(el);

        root.render(
            <LazyMotion features={domMax}>
                <ParallaxProvider>
                    <App {...props} />
                </ParallaxProvider>
            </LazyMotion>
        );
    },
    progress: {
        color: '#4B5563',
    },
});
