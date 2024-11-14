/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
      './templates/**/*.html',
      './**/templates/**/*.html',
  ],
  theme: {
    extend: {
      screens: {
        tablet: '640px',
        laptop: '1064px',
        desktop: '1280px'
      }
    },
    fontFamily: {
     "sans": ["Ubuntu", "Fira Sans", "Noto Sans", "Catamaran", "Cabin", "Roboto"],
     "jersey": ['Graduate', 'sans-serif'],
    },
  },
  plugins: [
      require("@tailwindcss/typography"),
      require("daisyui"),
  ],
}

