import React from 'react'
import { X } from 'lucide-react'

export default function Modal({ isOpen, onClose, title, children, size = 'md' }) {
  if (!isOpen) return null

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl'
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className={`relative bg-white rounded-xl shadow-2xl ${sizeClasses[size]} w-full mx-4 max-h-[90vh] overflow-hidden`}>
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-dark-200">
          <h2 className="text-xl font-semibold text-dark-900">{title}</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-dark-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-dark-600" />
          </button>
        </div>
        
        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-140px)]">
          {children}
        </div>
      </div>
    </div>
  )
}

export function ConfirmModal({ isOpen, onClose, onConfirm, title, message, confirmText = 'Confirm', cancelText = 'Cancel', variant = 'primary' }) {
  if (!isOpen) return null

  const variantClasses = {
    primary: 'btn-primary',
    danger: 'bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors',
    success: 'bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors'
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="sm">
      <div className="p-6">
        <p className="text-dark-700 mb-6">{message}</p>
        <div className="flex justify-end gap-3">
          <button onClick={onClose} className="btn-secondary">
            {cancelText}
          </button>
          <button onClick={onConfirm} className={variantClasses[variant]}>
            {confirmText}
          </button>
        </div>
      </div>
    </Modal>
  )
}

export function PromptModal({ isOpen, onClose, onSubmit, title, message, placeholder, defaultValue = '', submitText = 'Submit', cancelText = 'Cancel' }) {
  const [value, setValue] = React.useState(defaultValue)

  React.useEffect(() => {
    if (isOpen) {
      setValue(defaultValue)
    }
  }, [isOpen, defaultValue])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (value.trim()) {
      onSubmit(value)
      onClose()
    }
  }

  if (!isOpen) return null

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="sm">
      <form onSubmit={handleSubmit} className="p-6">
        {message && <p className="text-dark-700 mb-4">{message}</p>}
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={placeholder}
          className="input w-full mb-6"
          autoFocus
        />
        <div className="flex justify-end gap-3">
          <button type="button" onClick={onClose} className="btn-secondary">
            {cancelText}
          </button>
          <button type="submit" className="btn-primary" disabled={!value.trim()}>
            {submitText}
          </button>
        </div>
      </form>
    </Modal>
  )
}

export function SuccessModal({ isOpen, onClose, title, message }) {
  if (!isOpen) return null

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="sm">
      <div className="p-6">
        <div className="flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mx-auto mb-4">
          <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <p className="text-dark-700 text-center mb-6">{message}</p>
        <div className="flex justify-center">
          <button onClick={onClose} className="btn-primary">
            OK
          </button>
        </div>
      </div>
    </Modal>
  )
}

export function ErrorModal({ isOpen, onClose, title, message }) {
  if (!isOpen) return null

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="sm">
      <div className="p-6">
        <div className="flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mx-auto mb-4">
          <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <p className="text-dark-700 text-center mb-6">{message}</p>
        <div className="flex justify-center">
          <button onClick={onClose} className="btn-primary">
            OK
          </button>
        </div>
      </div>
    </Modal>
  )
}
