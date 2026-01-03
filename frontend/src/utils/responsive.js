import { useState, useEffect } from 'react'

// Centralized breakpoint system
export const breakpoints = {
  mobile: 480,
  tablet: 768,
  desktop: 1024,
  wide: 1280,
}

// Media query strings
export const mediaQueries = {
  mobile: `(max-width: ${breakpoints.mobile}px)`,
  tablet: `(max-width: ${breakpoints.tablet}px)`,
  desktop: `(max-width: ${breakpoints.desktop}px)`,
  wide: `(min-width: ${breakpoints.wide}px)`,

  // Min-width queries
  fromTablet: `(min-width: ${breakpoints.tablet + 1}px)`,
  fromDesktop: `(min-width: ${breakpoints.desktop + 1}px)`,
}

// CSS media query helpers
export const media = {
  mobile: `@media ${mediaQueries.mobile}`,
  tablet: `@media ${mediaQueries.tablet}`,
  desktop: `@media ${mediaQueries.desktop}`,
  wide: `@media ${mediaQueries.wide}`,
  fromTablet: `@media ${mediaQueries.fromTablet}`,
  fromDesktop: `@media ${mediaQueries.fromDesktop}`,
}

// Hook to detect screen size
export const useMediaQuery = (query) => {
  const [matches, setMatches] = useState(() => {
    if (typeof window === 'undefined') return false
    return window.matchMedia(query).matches
  })

  useEffect(() => {
    const media = window.matchMedia(query)
    const listener = () => setMatches(media.matches)

    // Listen for changes
    media.addEventListener('change', listener)

    return () => media.removeEventListener('change', listener)
  }, [query])

  return matches
}

// Helper to check if mobile
export const isMobile = () => {
  if (typeof window === 'undefined') return false
  return window.matchMedia(mediaQueries.mobile).matches
}

// Helper to check if tablet
export const isTablet = () => {
  if (typeof window === 'undefined') return false
  return window.matchMedia(mediaQueries.tablet).matches
}

// Helper to get current breakpoint
export const getCurrentBreakpoint = () => {
  if (typeof window === 'undefined') return 'desktop'

  const width = window.innerWidth
  if (width <= breakpoints.mobile) return 'mobile'
  if (width <= breakpoints.tablet) return 'tablet'
  if (width <= breakpoints.desktop) return 'desktop'
  return 'wide'
}
