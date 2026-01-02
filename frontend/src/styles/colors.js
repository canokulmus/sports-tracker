// src/styles/colors.js
// Merkezi renk sistemi - Tüm renkler buradan import edilir

/**
 * Ana renk paleti
 * Dark theme tasarımı için optimize edilmiş
 */
export const colors = {
  // Background Colors (Arkaplan renkleri)
  background: {
    primary: '#0f172a',      // Ana sayfa arka planı (slate-950)
    secondary: '#1e293b',    // Card ve sidebar arka planı (slate-800)
    tertiary: '#334155',     // Hover ve secondary card (slate-700)
    overlay: 'rgba(0, 0, 0, 0.5)', // Modal overlay
  },

  // Text Colors (Metin renkleri)
  text: {
    primary: '#f1f5f9',      // Ana metin rengi (slate-100)
    secondary: '#94a3b8',    // İkincil metin, açıklamalar (slate-400)
    muted: '#64748b',        // Çok soluk metin (slate-500)
    inverse: '#0f172a',      // Açık arka plan için koyu metin
  },

  // Brand Colors (Marka renkleri)
  brand: {
    primary: '#3b82f6',      // Ana mavi (blue-500)
    primaryHover: '#2563eb', // Hover mavi (blue-600)
    primaryLight: '#60a5fa', // Açık mavi (blue-400)
    primaryDark: '#1e40af',  // Koyu mavi (blue-800)
  },

  // State Colors (Durum renkleri)
  state: {
    success: '#22c55e',      // Başarılı, aktif (green-500)
    successLight: '#86efac', // Açık yeşil (green-300)
    warning: '#f59e0b',      // Uyarı, beklemede (amber-500)
    warningLight: '#fbbf24', // Açık sarı (amber-400)
    danger: '#ef4444',       // Hata, iptal (red-500)
    dangerLight: '#fca5a5',  // Açık kırmızı (red-300)
    info: '#06b6d4',         // Bilgi (cyan-500)
    infoLight: '#67e8f9',    // Açık mavi-yeşil (cyan-300)
  },

  // Game Status Colors (Oyun durum renkleri)
  gameStatus: {
    live: '#22c55e',         // Canlı maç (yeşil)
    scheduled: '#94a3b8',    // Planlanmış (gri)
    paused: '#f59e0b',       // Duraklatılmış (sarı)
    ended: '#64748b',        // Bitmiş (koyu gri)
    cancelled: '#ef4444',    // İptal (kırmızı)
  },

  // Tournament Type Colors (Turnuva tipi renkleri)
  tournament: {
    league: '#3b82f6',       // Lig formatı (mavi)
    elimination: '#ef4444',  // Eleme formatı (kırmızı)
    group: '#22c55e',        // Grup formatı (yeşil)
    playoff: '#f59e0b',      // Playoff formatı (sarı)
  },

  // UI Elements (UI elementleri)
  ui: {
    border: '#475569',       // Border rengi (slate-600)
    borderLight: '#64748b',  // Açık border (slate-500)
    borderDark: '#334155',   // Koyu border (slate-700)
    divider: '#334155',      // Ayırıcı çizgi
    shadow: 'rgba(0, 0, 0, 0.3)', // Gölge
  },

  // Gradients (Degradeler)
  gradients: {
    primary: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
    dark: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
    success: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
    danger: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
    card: 'linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%)',
  },

  // Team/Player Badge Colors (Takım/Oyuncu rozet renkleri)
  badge: {
    blue: '#3b82f6',
    green: '#22c55e',
    yellow: '#f59e0b',
    red: '#ef4444',
    purple: '#a855f7',
    pink: '#ec4899',
    orange: '#f97316',
    cyan: '#06b6d4',
  },

  // Connection Status (Bağlantı durumu)
  connection: {
    online: '#22c55e',       // Çevrimiçi (yeşil)
    offline: '#ef4444',      // Çevrimdışı (kırmızı)
    mock: '#f59e0b',         // Mock mode (sarı)
    connecting: '#06b6d4',   // Bağlanıyor (mavi)
  },
}

/**
 * CSS Variable olarak kullanım için
 * Örnek: const style = { color: cssVars.text.primary }
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
 * Örnek: withOpacity(colors.brand.primary, 0.5)
 */
export const withOpacity = (color, opacity) => {
  // Hex to RGBA conversion
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

// Ana colors objesine ekle
colors.quickColors = quickColors

export default colors
