import { describe, it, expect } from 'vitest'
import { 
  formatDate, 
  formatRelativeTime, 
  truncate, 
  capitalizeFirst, 
  getInitials 
} from '@utils/helpers'

describe('Helper Functions', () => {
  describe('formatDate', () => {
    it('formats date correctly', () => {
      const date = new Date('2024-01-15')
      const formatted = formatDate(date)
      expect(formatted).toContain('January')
      expect(formatted).toContain('15')
      expect(formatted).toContain('2024')
    })
  })

  describe('truncate', () => {
    it('truncates long strings', () => {
      const longString = 'This is a very long string that should be truncated'
      const truncated = truncate(longString, 20)
      expect(truncated.length).toBeLessThanOrEqual(23) // 20 + '...'
      expect(truncated).toContain('...')
    })

    it('does not truncate short strings', () => {
      const shortString = 'Short'
      const result = truncate(shortString, 20)
      expect(result).toBe('Short')
    })
  })

  describe('capitalizeFirst', () => {
    it('capitalizes first letter', () => {
      expect(capitalizeFirst('hello')).toBe('Hello')
      expect(capitalizeFirst('world')).toBe('World')
    })

    it('handles empty strings', () => {
      expect(capitalizeFirst('')).toBe('')
    })
  })

  describe('getInitials', () => {
    it('gets initials from full name', () => {
      expect(getInitials('John Doe')).toBe('JD')
      expect(getInitials('Jane Mary Smith')).toBe('JM')
    })

    it('handles single names', () => {
      expect(getInitials('John')).toBe('J')
    })

    it('handles empty names', () => {
      expect(getInitials('')).toBe('U')
    })
  })
})
