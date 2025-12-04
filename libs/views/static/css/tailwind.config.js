module.exports = {
  darkMode: 'class',
  content: [
    '../../**/*.html',
    '../../js/**/*.js',
    '../../static/js/**/*.js',
  ],
  safelist: [{ pattern: /.*/ }],
  theme: {
    extend: {
      colors: {
        primary: 'var(--color-accent)',
        background: 'var(--color-bg)',
        'background-alt': 'var(--color-bg-alt)',
        surface: 'var(--color-surface)',
        'text-primary': 'var(--color-text)',
        'text-muted': 'var(--color-text-muted)',
        success: 'var(--color-success)',
        warning: 'var(--color-warning)',
        danger: 'var(--color-danger)',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
      fontSize: {
        xs: ['11px', '16px'],
        sm: ['13px', '18px'],
        base: ['14px', '20px'],
        lg: ['16px', '24px'],
        xl: ['18px', '28px'],
      },
      borderRadius: {
        DEFAULT: '0.5rem',
        lg: '0.75rem',
        xl: '1rem',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/container-queries'),
  ],
};