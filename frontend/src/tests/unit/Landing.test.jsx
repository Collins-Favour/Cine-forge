import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import LandingPage from '@pages/Landing'

describe('Landing Page', () => {
  it('renders the landing page', () => {
    render(
      <BrowserRouter>
        <LandingPage />
      </BrowserRouter>
    )
    
    expect(screen.getByText(/CineForge AI/i)).toBeInTheDocument()
    expect(screen.getByText(/Transform Scripts into/i)).toBeInTheDocument()
  })

  it('has navigation links', () => {
    render(
      <BrowserRouter>
        <LandingPage />
      </BrowserRouter>
    )
    
    expect(screen.getByText('Sign In')).toBeInTheDocument()
    expect(screen.getByText('Get Started')).toBeInTheDocument()
  })

  it('displays feature sections', () => {
    render(
      <BrowserRouter>
        <LandingPage />
      </BrowserRouter>
    )
    
    expect(screen.getByText('AI-Powered Analysis')).toBeInTheDocument()
    expect(screen.getByText('Visual Storyboards')).toBeInTheDocument()
    expect(screen.getByText('Real-time Collaboration')).toBeInTheDocument()
  })
})
