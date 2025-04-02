module.exports = {
  content: [
    "./src/**/*.{html,js,jsx,ts,tsx}", // Cette ligne permet à Tailwind de scanner tes fichiers
  ],
  theme: {
    extend: {
      colors: {
        customColor: '#abc123',
      },
      animation: {
        fadeIn: 'fadeIn 2s ease-out forwards',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      }
    },
  },
  plugins: [],
}
