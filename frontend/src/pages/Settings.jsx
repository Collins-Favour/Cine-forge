import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Save, User, Lock, Bell, Eye, EyeOff, Camera, ArrowLeft } from 'lucide-react'
import { useAuthStore } from '@store/authStore'
import { usersApi } from '@services/apiServices'
import { SuccessModal, ErrorModal } from '@components/Modal'
import toast from 'react-hot-toast'
import api from '@services/api'

export default function Settings() {
  const { user, updateUser } = useAuthStore()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('profile')
  const [showCurrentPassword, setShowCurrentPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [saving, setSaving] = useState(false)
  const [uploadingImage, setUploadingImage] = useState(false)
  const fileInputRef = useRef(null)
  
  // Modal states
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [showErrorModal, setShowErrorModal] = useState(false)
  const [modalTitle, setModalTitle] = useState('')
  const [modalMessage, setModalMessage] = useState('')

  const [profileData, setProfileData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    bio: '',
    location: '',
    profile_pic_url: '',
  })

  useEffect(() => {
    fetchProfile()
  }, [user])  // Re-fetch when user changes

  const fetchProfile = async () => {
    try {
      const response = await usersApi.getProfile()
      const userData = response.data.user
      setProfileData({
        first_name: userData.first_name || '',
        last_name: userData.last_name || '',
        email: userData.email || '',
        phone: userData.phone || '',
        bio: userData.bio || '',
        location: userData.location || '',
        profile_pic_url: userData.profile_pic_url || '',
      })
    } catch (err) {
      console.error('Error fetching profile:', err)
      // Fallback to user from store
      if (user) {
        setProfileData({
          first_name: user.first_name || '',
          last_name: user.last_name || '',
          email: user.email || '',
          phone: user.phone || '',
          bio: user.bio || '',
          location: user.location || '',
          profile_pic_url: user.profile_pic_url || '',
        })
      }
    }
  }

  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })

  const [notifications, setNotifications] = useState({
    email_messages: true,
    email_updates: true,
    email_marketing: false,
    push_messages: true,
    push_updates: false,
  })

  const handleProfileSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      const response = await usersApi.updateProfile(profileData)
      // Update the user in the store with the full response
      updateUser(response.data.user)
      toast.success('Profile updated successfully!')
      // Also show the modal for consistency
      setModalTitle('Success')
      setModalMessage('Profile updated successfully!')
      setShowSuccessModal(true)
    } catch (err) {
      console.error('Error updating profile:', err)
      const errorMsg = err.response?.data?.error || 'Failed to update profile. Please try again.'
      toast.error(errorMsg)
      setModalTitle('Update Failed')
      setModalMessage(errorMsg)
      setShowErrorModal(true)
    } finally {
      setSaving(false)
    }
  }

  const handlePasswordSubmit = async (e) => {
    e.preventDefault()
    if (passwordData.new_password !== passwordData.confirm_password) {
      toast.error('Passwords do not match! Please try again.')
      setModalTitle('Password Mismatch')
      setModalMessage('Passwords do not match! Please try again.')
      setShowErrorModal(true)
      return
    }
    
    // Validate password strength
    if (passwordData.new_password.length < 8) {
      toast.error('Password must be at least 8 characters long')
      return
    }
    
    setSaving(true)
    try {
      await usersApi.changePassword({
        current_password: passwordData.current_password,
        new_password: passwordData.new_password
      })
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: '',
      })
      toast.success('Password changed successfully!')
      setModalTitle('Success')
      setModalMessage('Password changed successfully!')
      setShowSuccessModal(true)
    } catch (err) {
      console.error('Error changing password:', err)
      const errorMsg = err.response?.data?.error || 'Failed to change password. Please check your current password and try again.'
      toast.error(errorMsg)
      setModalTitle('Password Change Failed')
      setModalMessage(errorMsg)
      setShowErrorModal(true)
    } finally {
      setSaving(false)
    }
  }

  const handleNotificationChange = (key) => {
    setNotifications({ ...notifications, [key]: !notifications[key] })
  }

  const handleSaveNotifications = async () => {
    setSaving(true)
    try {
      await usersApi.updateNotifications(notifications)
      toast.success('Notification preferences saved successfully!')
      setModalTitle('Success')
      setModalMessage('Notification preferences saved successfully!')
      setShowSuccessModal(true)
    } catch (err) {
      console.error('Error saving notifications:', err)
      const errorMsg = 'Failed to save notification preferences. Please try again.'
      toast.error(errorMsg)
      setModalTitle('Save Failed')
      setModalMessage(errorMsg)
      setShowErrorModal(true)
    } finally {
      setSaving(false)
    }
  }

  const handleImageUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if (!validTypes.includes(file.type.toLowerCase())) {
      toast.error('Please select a valid image (JPG, PNG, GIF, or WEBP)')
      return
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Image size must be less than 5MB')
      return
    }

    setUploadingImage(true)
    try {
      // Create FormData for file upload
      const formData = new FormData()
      formData.append('file', file)

      // Upload to backend
      const response = await api.post('/users/upload-avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      // Update profile data with new image URL
      const newProfilePicUrl = response.data.profile_pic_url
      setProfileData(prev => ({ ...prev, profile_pic_url: newProfilePicUrl }))
      
      // Update user in store
      updateUser(response.data.user)
      
      toast.success('Profile picture uploaded successfully!')
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Failed to upload image'
      toast.error(errorMsg)
      console.error('Image upload error:', error)
    } finally {
      setUploadingImage(false)
    }
  }

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'security', label: 'Security', icon: Lock },
    { id: 'notifications', label: 'Notifications', icon: Bell },
  ]

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8 flex items-center gap-4">
        <button
          onClick={() => navigate('/dashboard')}
          className="btn-secondary flex items-center gap-2 px-3 py-2"
          title="Back to Dashboard"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-3xl font-display font-bold text-dark-900 mb-2">Settings</h1>
          <p className="text-dark-600">Manage your account settings and preferences</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar Navigation */}
        <div className="lg:col-span-1">
          <div className="card space-y-1">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-colors flex items-center gap-3 ${
                    activeTab === tab.id
                      ? 'bg-primary-100 text-primary-700'
                      : 'hover:bg-dark-100 text-dark-700'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{tab.label}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <div className="card">
              <h2 className="text-xl font-semibold text-dark-900 mb-6">Profile Information</h2>

              <form onSubmit={handleProfileSubmit} className="space-y-6">
                {/* Avatar */}
                <div className="flex items-center gap-6">
                  <div className="relative">
                    {profileData.profile_pic_url ? (
                      <img 
                        src={profileData.profile_pic_url} 
                        alt="Profile" 
                        className="w-24 h-24 rounded-full object-cover"
                      />
                    ) : (
                      <div className="w-24 h-24 rounded-full bg-primary-500 flex items-center justify-center text-white text-3xl font-semibold">
                        {profileData.first_name?.charAt(0)}{profileData.last_name?.charAt(0)}
                      </div>
                    )}
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="absolute bottom-0 right-0 p-2 bg-white rounded-full shadow-lg hover:bg-dark-50 transition-colors"
                      disabled={uploadingImage}
                    >
                      <Camera className="w-4 h-4 text-dark-600" />
                    </button>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
                      onChange={handleImageUpload}
                      className="hidden"
                    />
                  </div>
                  <div>
                    <button 
                      type="button" 
                      onClick={() => fileInputRef.current?.click()}
                      disabled={uploadingImage}
                      className="btn-secondary mb-2"
                    >
                      {uploadingImage ? 'Uploading...' : 'Upload Photo'}
                    </button>
                    <p className="text-sm text-dark-500">JPG, PNG, GIF or WEBP. Max size 5MB.</p>
                  </div>
                </div>

                {/* Name Fields */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-dark-700 mb-2">
                      First Name
                    </label>
                    <input
                      type="text"
                      value={profileData.first_name}
                      onChange={(e) => setProfileData({ ...profileData, first_name: e.target.value })}
                      className="input w-full"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-dark-700 mb-2">
                      Last Name
                    </label>
                    <input
                      type="text"
                      value={profileData.last_name}
                      onChange={(e) => setProfileData({ ...profileData, last_name: e.target.value })}
                      className="input w-full"
                      required
                    />
                  </div>
                </div>

                {/* Email & Phone */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-dark-700 mb-2">
                      Email Address
                    </label>
                    <input
                      type="email"
                      value={profileData.email}
                      onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                      className="input w-full"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-dark-700 mb-2">
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      value={profileData.phone}
                      onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
                      className="input w-full"
                    />
                  </div>
                </div>

                {/* Location */}
                <div>
                  <label className="block text-sm font-medium text-dark-700 mb-2">
                    Location
                  </label>
                  <input
                    type="text"
                    value={profileData.location}
                    onChange={(e) => setProfileData({ ...profileData, location: e.target.value })}
                    placeholder="City, Country"
                    className="input w-full"
                  />
                </div>

                {/* Bio */}
                <div>
                  <label className="block text-sm font-medium text-dark-700 mb-2">
                    Bio
                  </label>
                  <textarea
                    value={profileData.bio}
                    onChange={(e) => setProfileData({ ...profileData, bio: e.target.value })}
                    placeholder="Tell us about yourself..."
                    className="input w-full"
                    rows="4"
                  />
                </div>

                <div className="flex justify-end gap-3 pt-4 border-t border-dark-200">
                  <button type="button" className="btn-secondary" onClick={fetchProfile}>
                    Cancel
                  </button>
                  <button 
                    type="submit" 
                    disabled={saving}
                    className="btn-primary flex items-center gap-2 disabled:opacity-50"
                  >
                    <Save className="w-5 h-5" />
                    <span>{saving ? 'Saving...' : 'Save Changes'}</span>
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Security Tab */}
          {activeTab === 'security' && (
            <div className="card">
              <h2 className="text-xl font-semibold text-dark-900 mb-6">Security Settings</h2>

              <form onSubmit={handlePasswordSubmit} className="space-y-6">
                {/* Current Password */}
                <div>
                  <label className="block text-sm font-medium text-dark-700 mb-2">
                    Current Password
                  </label>
                  <div className="relative">
                    <input
                      type={showCurrentPassword ? 'text' : 'password'}
                      value={passwordData.current_password}
                      onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                      className="input w-full pr-12"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-dark-400 hover:text-dark-600"
                    >
                      {showCurrentPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                {/* New Password */}
                <div>
                  <label className="block text-sm font-medium text-dark-700 mb-2">
                    New Password
                  </label>
                  <div className="relative">
                    <input
                      type={showNewPassword ? 'text' : 'password'}
                      value={passwordData.new_password}
                      onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                      className="input w-full pr-12"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowNewPassword(!showNewPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-dark-400 hover:text-dark-600"
                    >
                      {showNewPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                  <p className="text-sm text-dark-500 mt-1">
                    Must be at least 8 characters with uppercase, lowercase, and numbers
                  </p>
                </div>

                {/* Confirm Password */}
                <div>
                  <label className="block text-sm font-medium text-dark-700 mb-2">
                    Confirm New Password
                  </label>
                  <input
                    type="password"
                    value={passwordData.confirm_password}
                    onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                    className="input w-full"
                    required
                  />
                </div>

                <div className="flex justify-end gap-3 pt-4 border-t border-dark-200">
                  <button type="button" className="btn-secondary">
                    Cancel
                  </button>
                  <button 
                    type="submit" 
                    disabled={saving}
                    className="btn-primary disabled:opacity-50"
                  >
                    {saving ? 'Updating...' : 'Update Password'}
                  </button>
                </div>
              </form>

              {/* Two-Factor Authentication */}
              <div className="mt-8 pt-8 border-t border-dark-200">
                <h3 className="text-lg font-semibold text-dark-900 mb-4">Two-Factor Authentication</h3>
                <div className="flex items-center justify-between p-4 bg-dark-50 rounded-lg">
                  <div>
                    <div className="font-medium text-dark-900">Enhance your account security</div>
                    <div className="text-sm text-dark-600">Add an extra layer of protection</div>
                  </div>
                  <button className="btn-secondary">Enable</button>
                </div>
              </div>
            </div>
          )}

          {/* Notifications Tab */}
          {activeTab === 'notifications' && (
            <div className="card">
              <h2 className="text-xl font-semibold text-dark-900 mb-6">Notification Preferences</h2>

              <div className="space-y-6">
                {/* Email Notifications */}
                <div>
                  <h3 className="font-semibold text-dark-900 mb-4">Email Notifications</h3>
                  <div className="space-y-3">
                    <label className="flex items-center justify-between p-4 bg-dark-50 rounded-lg cursor-pointer hover:bg-dark-100 transition-colors">
                      <div>
                        <div className="font-medium text-dark-900">Messages</div>
                        <div className="text-sm text-dark-600">Receive emails for new messages</div>
                      </div>
                      <input
                        type="checkbox"
                        checked={notifications.email_messages}
                        onChange={() => handleNotificationChange('email_messages')}
                        className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                      />
                    </label>

                    <label className="flex items-center justify-between p-4 bg-dark-50 rounded-lg cursor-pointer hover:bg-dark-100 transition-colors">
                      <div>
                        <div className="font-medium text-dark-900">Project Updates</div>
                        <div className="text-sm text-dark-600">Get notified about project changes</div>
                      </div>
                      <input
                        type="checkbox"
                        checked={notifications.email_updates}
                        onChange={() => handleNotificationChange('email_updates')}
                        className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                      />
                    </label>

                    <label className="flex items-center justify-between p-4 bg-dark-50 rounded-lg cursor-pointer hover:bg-dark-100 transition-colors">
                      <div>
                        <div className="font-medium text-dark-900">Marketing</div>
                        <div className="text-sm text-dark-600">Receive news and promotional emails</div>
                      </div>
                      <input
                        type="checkbox"
                        checked={notifications.email_marketing}
                        onChange={() => handleNotificationChange('email_marketing')}
                        className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                      />
                    </label>
                  </div>
                </div>

                {/* Push Notifications */}
                <div>
                  <h3 className="font-semibold text-dark-900 mb-4">Push Notifications</h3>
                  <div className="space-y-3">
                    <label className="flex items-center justify-between p-4 bg-dark-50 rounded-lg cursor-pointer hover:bg-dark-100 transition-colors">
                      <div>
                        <div className="font-medium text-dark-900">Messages</div>
                        <div className="text-sm text-dark-600">Get push notifications for messages</div>
                      </div>
                      <input
                        type="checkbox"
                        checked={notifications.push_messages}
                        onChange={() => handleNotificationChange('push_messages')}
                        className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                      />
                    </label>

                    <label className="flex items-center justify-between p-4 bg-dark-50 rounded-lg cursor-pointer hover:bg-dark-100 transition-colors">
                      <div>
                        <div className="font-medium text-dark-900">Project Updates</div>
                        <div className="text-sm text-dark-600">Push alerts for project activity</div>
                      </div>
                      <input
                        type="checkbox"
                        checked={notifications.push_updates}
                        onChange={() => handleNotificationChange('push_updates')}
                        className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                      />
                    </label>
                  </div>
                </div>

                <div className="flex justify-end gap-3 pt-4 border-t border-dark-200">
                  <button type="button" className="btn-secondary">
                    Reset to Defaults
                  </button>
                  <button 
                    type="button" 
                    onClick={handleSaveNotifications}
                    disabled={saving}
                    className="btn-primary flex items-center gap-2 disabled:opacity-50"
                  >
                    <Save className="w-5 h-5" />
                    <span>{saving ? 'Saving...' : 'Save Preferences'}</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      <SuccessModal
        isOpen={showSuccessModal}
        onClose={() => setShowSuccessModal(false)}
        title={modalTitle}
        message={modalMessage}
      />

      <ErrorModal
        isOpen={showErrorModal}
        onClose={() => setShowErrorModal(false)}
        title={modalTitle}
        message={modalMessage}
      />
    </div>
  )
}
