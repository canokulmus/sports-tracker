export const colors = {
  background: {
    primary: '#0a0e1a',      
    secondary: '#141824',    
    tertiary: '#1e2433',     
    quaternary: '#2a3142',   
    overlay: 'rgba(0, 0, 0, 0.7)',
  },

  text: {
    primary: '#e8edf4',      
    secondary: '#8b95a8',    
    muted: '#5a6477',        
    inverse: '#0a0e1a',      
  },

  brand: {
    primary: '#6366f1',      
    primaryHover: '#4f46e5', 
    primaryLight: '#818cf8', 
    primaryDark: '#3730a3',  
    neon: '#a855f7',         
    neonCyan: '#06b6d4',     
  },

  state: {
    success: '#10b981',      
    successLight: '#34d399',
    successNeon: '#22c55e',  
    warning: '#f59e0b',      
    warningLight: '#fbbf24',
    warningNeon: '#fbbf24',  
    danger: '#ef4444',       
    dangerLight: '#f87171',
    dangerNeon: '#ff4d6d',   
    info: '#06b6d4',         
    infoLight: '#22d3ee',
    infoNeon: '#00d9ff',     
  },

  gameStatus: {
    live: '#10b981',         
    scheduled: '#8b95a8',    
    paused: '#fbbf24',       
    ended: '#5a6477',        
    cancelled: '#ff4d6d',    
  },

  tournament: {
    league: '#6366f1',       
    elimination: '#ff4d6d',  
    group: '#10b981',        
    playoff: '#fbbf24',      
  },

  ui: {
    border: '#2a3142',       
    borderLight: '#363d4e',  
    borderDark: '#1e2433',   
    borderSubtle: '#2a3142',
    borderNeon: '#6366f140', 
    divider: '#1e2433',
    shadow: 'rgba(0, 0, 0, 0.5)',
    info: '#06b6d4',
  },

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

  neon: {
    purple: '#a855f7',
    blue: '#6366f1',
    cyan: '#06b6d4',
    green: '#10b981',
    yellow: '#fbbf24',
    red: '#ff4d6d',
    pink: '#ec4899',
  },

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

  connection: {
    online: '#10b981',       
    offline: '#ff4d6d',      
    connecting: '#06b6d4',   
  },
}

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

const quickColors = {
  white: '#ffffff',
  black: '#000000',
  transparent: 'transparent',
}

colors.quickColors = quickColors

export default colors
