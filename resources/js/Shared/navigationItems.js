// Define shared navigation items
import { usePage } from '@inertiajs/vue3';

export const navItemsLeft = [
    { name: 'Technology', dropdown: ['Web Dev', 'AI', 'Hardware'] },
    { name: 'Finance', dropdown: ['Investing', 'Budgeting'] },
    { name: 'Health', dropdown: ['Fitness', 'Nutrition'] },
    { name: 'Education', dropdown: ['Courses', 'Tutorials'] },
];

export const navItemsRight = [
    { name: 'Sports', dropdown: ['Football', 'Basketball'] },
    { name: 'Travel', dropdown: ['Destinations', 'Tips'] },
    { name: 'Lifestyle', dropdown: ['Fashion', 'Food'] },
    { name: 'Community', dropdown: ['Forums', 'Events'] },
];

export const getAuthItems = () => {
    const { auth } = usePage().props;
    
    if (auth.user) {
        return [
            {
                name: auth.user.name,
                dropdown: ['Profile', 'Settings', 'Log Out'],
                type: 'auth'
            }
        ];
    }
    
    return [
        { name: 'Sign In', href: route('login'), type: 'auth' },
        { name: 'Register', href: route('register'), type: 'auth', highlight: true }
    ];
}; 