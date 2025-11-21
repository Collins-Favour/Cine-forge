import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import Login from '@pages/auth/Login'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false }
  }
})

const MockedLogin = () => (
  <QueryClientProvider client={queryClient}>
    <BrowserRouter>
      <Login />
    </BrowserRouter>
  </QueryClientProvider>
)

describe('Login Page', () => {
  it('renders login form', () => {
    render(<MockedLogin />)
    
    expect(screen.getByText('Welcome Back')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('you@example.com')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('••••••••')).toBeInTheDocument()
  })

  it('shows validation errors for empty fields', async () => {
    render(<MockedLogin />)
    
    const submitButton = screen.getByRole('button', { name: /sign in/i })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument()
    })
  })

  it('toggles password visibility', () => {
    render(<MockedLogin />)
    
    const passwordInput = screen.getByPlaceholderText('••••••••')
    const toggleButton = passwordInput.parentElement.querySelector('button')
    
    expect(passwordInput.type).toBe('password')
    
    fireEvent.click(toggleButton)
    expect(passwordInput.type).toBe('text')
    
    fireEvent.click(toggleButton)
    expect(passwordInput.type).toBe('password')
  })

  it('has link to registration page', () => {
    render(<MockedLogin />)
    
    const registerLink = screen.getByText('Create Account')
    expect(registerLink).toBeInTheDocument()
    expect(registerLink.closest('a')).toHaveAttribute('href', '/register')
  })
})
