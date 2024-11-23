/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
      './templates/**/*.html',
      './**/templates/**/*.html',
  ],
  safelist: [
      "checkbox-sm",
      "file-input-sm",
      "select-sm",
      "file-input-sm",
      "checkbox-xs",
      "file-input-xs",
      "input-xs",
      "select-xs",
      "input-sm",
      "w-10",
      "w-12",
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
     "sans": ["Noto Sans", "Ubuntu", "Fira Sans", "Noto Sans", "Catamaran", "Cabin", "Roboto"],
     "jersey": ['Graduate', 'sans-serif'],
    },
  },
  plugins: [
      require("@tailwindcss/typography"),
      require("daisyui"),
  ],
  // daisyui: {
  //  themes: ["fantasy", "dark"]
  //},
  //darkMode: ['selector', '[data-theme="dark"]']
}

