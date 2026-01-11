import { useState, useEffect } from 'react'

export const breakpoints = {
  mobile: 480,
  tablet: 768,
  desktop: 1024,
  wide: 1280,
}

export const mediaQueries = {
  mobile: `(max-width: ${breakpoints.mobile}px)`,
  tablet: `(max-width: ${breakpoints.tablet}px)`,
  desktop: `(max-width: ${breakpoints.desktop}px)`,
  wide: `(min-width: ${breakpoints.wide}px)`,

  fromTablet: `(min-width: ${breakpoints.tablet + 1}px)`,
  fromDesktop: `(min-width: ${breakpoints.desktop + 1}px)`,
}

export const media = {
  mobile: `@media ${mediaQueries.mobile}`,
  tablet: `@media ${mediaQueries.tablet}`,
  desktop: `@media ${mediaQueries.desktop}`,
  wide: `@media ${mediaQueries.wide}`,
  fromTablet: `@media ${mediaQueries.fromTablet}`,
  fromDesktop: `@media ${mediaQueries.fromDesktop}`,
}

export const useMediaQuery = (query) => {
  const [matches, setMatches] = useState(() => {
    if (typeof window === 'undefined') return false
    return window.matchMedia(query).matches
  })

  useEffect(() => {
    const media = window.matchMedia(query)
    const listener = () => setMatches(media.matches)

    media.addEventListener('change', listener)

    return () => media.removeEventListener('change', listener)
  }, [query])

  return matches
}

export const isMobile = () => {
  if (typeof window === 'undefined') return false
  return window.matchMedia(mediaQueries.mobile).matches
}

export const isTablet = () => {
  if (typeof window === 'undefined') return false
  return window.matchMedia(mediaQueries.tablet).matches
}

export const getCurrentBreakpoint = () => {
  if (typeof window === 'undefined') return 'desktop'

  const width = window.innerWidth
  if (width <= breakpoints.mobile) return 'mobile'
  if (width <= breakpoints.tablet) return 'tablet'
  if (width <= breakpoints.desktop) return 'desktop'
  return 'wide'
}
