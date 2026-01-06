// src/styles/colors.js
// Merkezi renk sistemi - Modern Dark Theme with Neon Accents

/**
 * Ana renk paleti
 * Modern dark theme - Neon vibe
 */
export const colors = {
  // Background Colors (Arkaplan renkleri) - Daha koyu ve modern
  background: {
    primary: '#0a0e1a',      // Çok koyu navy-black
    secondary: '#141824',    // Koyu card background
    tertiary: '#1e2433',     // Hover ve tertiary
    quaternary: '#2a3142',   // Daha açık seviye
    overlay: 'rgba(0, 0, 0, 0.7)',
  },

  // Text Colors (Metin renkleri)
  text: {
    primary: '#e8edf4',      // Parlak beyaz-mavi
    secondary: '#8b95a8',    // Orta ton gri
    muted: '#5a6477',        // Soluk gri
    inverse: '#0a0e1a',      // Koyu
  },

  // Brand Colors (Marka renkleri) - Neon mavi/mor tonları
  brand: {
    primary: '#6366f1',      // Neon indigo
    primaryHover: '#4f46e5', // Koyu indigo
    primaryLight: '#818cf8', // Açık indigo
    primaryDark: '#3730a3',  // Çok koyu indigo
    neon: '#a855f7',         // Neon mor
    neonCyan: '#06b6d4',     // Neon cyan
  },

  // State Colors (Durum renkleri) - Neon vibe
  state: {
    success: '#10b981',      // Neon yeşil
    successLight: '#34d399',
    successNeon: '#22c55e',  // Parlak neon yeşil
    warning: '#f59e0b',      // Neon amber
    warningLight: '#fbbf24',
    warningNeon: '#fbbf24',  // Parlak neon sarı
    danger: '#ef4444',       // Neon kırmızı
    dangerLight: '#f87171',
    dangerNeon: '#ff4d6d',   // Parlak neon kırmızı
    info: '#06b6d4',         // Neon cyan
    infoLight: '#22d3ee',
    infoNeon: '#00d9ff',     // Parlak neon cyan
  },

  // Game Status Colors (Oyun durum renkleri) - Neon
  gameStatus: {
    live: '#10b981',         // Neon yeşil
    scheduled: '#8b95a8',    // Gri
    paused: '#fbbf24',       // Neon sarı
    ended: '#5a6477',        // Koyu gri
    cancelled: '#ff4d6d',    // Neon kırmızı
  },

  // Tournament Type Colors (Turnuva tipi renkleri)
  tournament: {
    league: '#6366f1',       // Neon indigo
    elimination: '#ff4d6d',  // Neon kırmızı
    group: '#10b981',        // Neon yeşil
    playoff: '#fbbf24',      // Neon sarı
  },

  // UI Elements (UI elementleri)
  ui: {
    border: '#2a3142',       // Subtle border
    borderLight: '#363d4e',  // Açık border
    borderDark: '#1e2433',   // Koyu border
    borderSubtle: '#2a3142',
    borderNeon: '#6366f140', // Neon border (transparent)
    divider: '#1e2433',
    shadow: 'rgba(0, 0, 0, 0.5)',
    info: '#06b6d4',
  },

  // Gradients (Degradeler) - Neon gradients
  gradients: {
    primary: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
    dark: 'linear-gradient(135deg, #1e2433 0%, #0a0e1a 100%)',
    success: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    danger: 'linear-gradient(135deg, #ff4d6d 0%, #ef4444 100%)',
    card: 'linear-gradient(135deg, #1e2433 0%, #141824 100%)',
    neon: 'linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #06b6d4 100%)',
    neonGreen: 'linear-gradient(135deg, #10b981 0%, #22c55e 100%)',
    neonPurple: 'linear-gradient(135deg, #a855f7 0%, #6366f1 100%)',
  },

  // Neon Glow Colors (Işıltılı efektler için)
  neon: {
    purple: '#a855f7',
    blue: '#6366f1',
    cyan: '#06b6d4',
    green: '#10b981',
    yellow: '#fbbf24',
    red: '#ff4d6d',
    pink: '#ec4899',
  },

  // Team/Player Badge Colors (Takım/Oyuncu rozet renkleri)
  badge: {
    blue: '#6366f1',
    green: '#10b981',
    yellow: '#fbbf24',
    red: '#ff4d6d',
    purple: '#a855f7',
    pink: '#ec4899',
    orange: '#f97316',
    cyan: '#06b6d4',
  },

  // Connection Status (Bağlantı durumu)
  connection: {
    online: '#10b981',       // Neon yeşil - WebSocket connected
    offline: '#ff4d6d',      // Neon kırmızı - WebSocket disconnected
    connecting: '#06b6d4',   // Neon cyan - WebSocket connecting
  },
}

/**
 * CSS Variable olarak kullanım için
 */
export const cssVars = {
  background: {
    primary: 'var(--bg-primary)',
    secondary: 'var(--bg-secondary)',
    tertiary: 'var(--bg-card)',
  },
  text: {
    primary: 'var(--text-primary)',
    secondary: 'var(--text-secondary)',
  },
  brand: {
    primary: 'var(--accent)',
    primaryHover: 'var(--accent-hover)',
  },
  state: {
    success: 'var(--success)',
    warning: 'var(--warning)',
    danger: 'var(--danger)',
  },
  ui: {
    border: 'var(--border)',
  },
}

/**
 * Opacity helpers
 */
export const withOpacity = (color, opacity) => {
  const hex = color.replace('#', '')
  const r = parseInt(hex.substring(0, 2), 16)
  const g = parseInt(hex.substring(2, 4), 16)
  const b = parseInt(hex.substring(4, 6), 16)
  return `rgba(${r}, ${g}, ${b}, ${opacity})`
}

/**
 * Hızlı erişim için sık kullanılan renkler
 */
const quickColors = {
  white: '#ffffff',
  black: '#000000',
  transparent: 'transparent',
}

colors.quickColors = quickColors

export default colors
