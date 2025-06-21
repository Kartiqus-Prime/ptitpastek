module.exports = {
  content: [
    '../../templates/**/*.html',
    '../../**/templates/**/*.html',
    './templates/**/*.html',
    './static_src/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        // Ajoutez toutes les couleurs utilisées dans vos templates
        'brand-primary': '#EF4444', // Exemple - remplacez par votre couleur
        'brand-secondary': '#F59E0B', // Exemple
        'watermelon-red': '#FF6B6B',
        'watermelon-pink': '#FF9E9E',
        'watermelon-green': '#48BB78',
        'watermelon-cream': '#FFF5F5',
        'watermelon-red-dark': '#DC2626',
        'watermelon-red-light': '#FECACA',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
}