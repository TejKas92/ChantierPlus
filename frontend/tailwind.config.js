/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: '#f59e0b', // Amber 500 - Construction vibe
                secondary: '#1e293b', // Slate 800
            }
        },
    },
    plugins: [],
}
