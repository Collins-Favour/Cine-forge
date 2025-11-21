import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { motion } from 'framer-motion'
import { Settings, Save, RefreshCw, Database, Mail, Shield, Zap, Globe } from 'lucide-react'
import { adminApi } from '@services/apiServices'
import { SuccessModal, ErrorModal } from '@components/Modal'

export default function SystemSettings() {
  const queryClient = useQueryClient()
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [showErrorModal, setShowErrorModal] = useState(false)
  const [modalMessage, setModalMessage] = useState('')

  const { data: settingsData, isLoading } = useQuery(
    'admin-settings',
    () => adminApi.getSettings()
  )

  const [settings, setSettings] = useState(settingsData?.data?.settings || {
    site_name: 'CineForge AI',
    maintenance_mode: false,
    allow_registration: true,
    require_email_verification: true,
    max_file_size: 100,
    max_storage_per_user: 5000,
    ai_features_enabled: true,
    collaboration_enabled: true
  })

  const updateMutation = useMutation(
    (data) => adminApi.updateSettings(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('admin-settings')
        setModalMessage('Settings updated successfully')
        setShowSuccessModal(true)
      },
      onError: () => {
        setModalMessage('Failed to update settings')
        setShowErrorModal(true)
      }
    }
  )

  const handleSave = () => {
    updateMutation.mutate(settings)
  }

  const handleChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }))
  }

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-display font-bold text-dark-900 mb-2">
            System Settings
          </h1>
          <p className="text-dark-600">Configure platform-wide settings and features</p>
        </div>
        <button
          onClick={handleSave}
          disabled={updateMutation.isLoading}
          className="btn-primary flex items-center gap-2"
        >
          <Save className="w-4 h-4" />
          {updateMutation.isLoading ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      {/* Settings Sections */}
      <div className="space-y-6">
        {/* General Settings */}
        <SettingSection
          icon={<Globe className="w-6 h-6" />}
          title="General Settings"
          description="Basic platform configuration"
        >
          <SettingInput
            label="Site Name"
            value={settings.site_name}
            onChange={(val) => handleChange('site_name', val)}
            placeholder="CineForge AI"
          />
          <SettingToggle
            label="Maintenance Mode"
            description="Put the platform in maintenance mode"
            checked={settings.maintenance_mode}
            onChange={(val) => handleChange('maintenance_mode', val)}
          />
        </SettingSection>

        {/* User Registration */}
        <SettingSection
          icon={<Shield className="w-6 h-6" />}
          title="User Registration"
          description="Control user registration and verification"
        >
          <SettingToggle
            label="Allow Registration"
            description="Allow new users to register"
            checked={settings.allow_registration}
            onChange={(val) => handleChange('allow_registration', val)}
          />
          <SettingToggle
            label="Require Email Verification"
            description="New users must verify their email"
            checked={settings.require_email_verification}
            onChange={(val) => handleChange('require_email_verification', val)}
          />
        </SettingSection>

        {/* Storage & Files */}
        <SettingSection
          icon={<Database className="w-6 h-6" />}
          title="Storage & Files"
          description="Manage file upload limits and storage"
        >
          <SettingInput
            label="Max File Size (MB)"
            type="number"
            value={settings.max_file_size}
            onChange={(val) => handleChange('max_file_size', parseInt(val))}
            placeholder="100"
          />
          <SettingInput
            label="Max Storage Per User (MB)"
            type="number"
            value={settings.max_storage_per_user}
            onChange={(val) => handleChange('max_storage_per_user', parseInt(val))}
            placeholder="5000"
          />
        </SettingSection>

        {/* Features */}
        <SettingSection
          icon={<Zap className="w-6 h-6" />}
          title="Platform Features"
          description="Enable or disable platform features"
        >
          <SettingToggle
            label="AI Features"
            description="Enable AI-powered script analysis and generation"
            checked={settings.ai_features_enabled}
            onChange={(val) => handleChange('ai_features_enabled', val)}
          />
          <SettingToggle
            label="Collaboration Features"
            description="Enable real-time collaboration and messaging"
            checked={settings.collaboration_enabled}
            onChange={(val) => handleChange('collaboration_enabled', val)}
          />
        </SettingSection>
      </div>

      {/* Modals */}
      <SuccessModal
        isOpen={showSuccessModal}
        onClose={() => setShowSuccessModal(false)}
        title="Settings Saved"
        message={modalMessage}
      />

      <ErrorModal
        isOpen={showErrorModal}
        onClose={() => setShowErrorModal(false)}
        title="Error"
        message={modalMessage}
      />
    </div>
  )
}

function SettingSection({ icon, title, description, children }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <div className="flex items-start gap-4 mb-6 pb-6 border-b border-dark-200">
        <div className="p-3 bg-primary-100 rounded-lg text-primary-600">
          {icon}
        </div>
        <div>
          <h2 className="text-xl font-bold text-dark-900 mb-1">{title}</h2>
          <p className="text-dark-600">{description}</p>
        </div>
      </div>
      <div className="space-y-6">
        {children}
      </div>
    </motion.div>
  )
}

function SettingInput({ label, value, onChange, type = 'text', placeholder }) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex-1">
        <label className="block text-sm font-medium text-dark-900 mb-1">
          {label}
        </label>
      </div>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="input w-64"
      />
    </div>
  )
}

function SettingToggle({ label, description, checked, onChange }) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex-1">
        <label className="block text-sm font-medium text-dark-900 mb-1">
          {label}
        </label>
        <p className="text-sm text-dark-600">{description}</p>
      </div>
      <button
        onClick={() => onChange(!checked)}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
          checked ? 'bg-primary-600' : 'bg-dark-300'
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            checked ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  )
}
