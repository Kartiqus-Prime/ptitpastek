/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // Chemins vers vos templates Django
    '../../templates/**/*.html',
    // Chemins vers vos fichiers Python avec du HTML
    './**/templates/**/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}