import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Camera, Save, Eye, EyeOff, Upload, X } from 'lucide-react'
import { useAuthStore } from '@store/authStore'
import api from '@services/api'
import toast from 'react-hot-toast'

export default function ProfileSettings({ onClose }) {
  const { user, updateUser } = useAuthStore()
  const [activeTab, setActiveTab] = useState('profile')
  const [saving, setSaving] = useState(false)
  const [uploadingImage, setUploadingImage] = useState(false)
  const fileInputRef = useRef(null)

  const [profileData, setProfileData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    bio: user?.bio || '',
    profile_pic_url: user?.profile_pic_url || '',
  })

  // Sync profileData when user changes in store - but prevent overwriting during upload
  useEffect(() => {
    if (user && !uploadingImage) {
      console.log('🔄 useEffect syncing profileData from user store:', {
        userProfilePicUrl: user.profile_pic_url?.substring(0, 50),
        currentProfilePicUrl: profileData.profile_pic_url?.substring(0, 50)
      })
      setProfileData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        bio: user.bio || '',
        profile_pic_url: user.profile_pic_url || '',
      })
    }
  }, [user.profile_pic_url, user.first_name, user.last_name, user.email, user.bio])

  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })

  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  })

  const handleProfileChange = (e) => {
    const { name, value } = e.target
    setProfileData(prev => ({ ...prev, [name]: value }))
  }

  const handlePasswordChange = (e) => {
    const { name, value } = e.target
    setPasswordData(prev => ({ ...prev, [name]: value }))
  }

  const handleImageUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    console.log('🖼️ Starting image upload:', {
      name: file.name,
      type: file.type,
      size: file.size
    })

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

      console.log('📤 Uploading to backend...')

      // Upload to backend
      const response = await api.post('/users/upload-avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      console.log('✅ Upload response:', {
        hasProfilePicUrl: !!response.data.profile_pic_url,
        urlLength: response.data.profile_pic_url?.length,
        urlPrefix: response.data.profile_pic_url?.substring(0, 30),
        hasUser: !!response.data.user,
        userProfilePicUrl: response.data.user?.profile_pic_url?.substring(0, 30)
      })

      // Update profile data with new image URL from response
      // Backend returns both profile_pic_url at root AND in user object
      const newProfilePicUrl = response.data.user?.profile_pic_url || response.data.profile_pic_url
      
      console.log('🔄 Updating user store FIRST with:', response.data.user)
      // Update user in store FIRST - this will have the profile_pic_url
      updateUser(response.data.user)
      
      // Then update local state - the useEffect won't fire because uploadingImage is true
      console.log('🔄 Then updating local profileData')
      setProfileData(prev => {
        const updated = { ...prev, profile_pic_url: newProfilePicUrl }
        console.log('🔄 Local state updated:', {
          hasUrl: !!updated.profile_pic_url,
          urlLength: updated.profile_pic_url?.length,
          urlPrefix: updated.profile_pic_url?.substring(0, 50)
        })
        return updated
      })

      console.log('✅ User store updated')
      
      toast.success('Profile picture uploaded successfully!')
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Failed to upload image'
      toast.error(errorMsg)
      console.error('❌ Image upload error:', error)
    } finally {
      setUploadingImage(false)
    }
  }

  const handleProfileSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      const response = await api.put('/users/profile', profileData)
      updateUser(response.data.user)
      toast.success('Profile updated successfully!')
      if (onClose) onClose()
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  const handlePasswordSubmit = async (e) => {
    e.preventDefault()

    // Validate passwords match
    if (passwordData.new_password !== passwordData.confirm_password) {
      toast.error('New passwords do not match')
      return
    }

    // Validate password strength
    if (passwordData.new_password.length < 8) {
      toast.error('Password must be at least 8 characters long')
      return
    }

    setSaving(true)
    try {
      await api.post('/users/change-password', {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password,
      })
      toast.success('Password changed successfully!')
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: '',
      })
      if (onClose) onClose()
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to change password')
    } finally {
      setSaving(false)
    }
  }

  // Debug: Log profileData whenever it changes
  useEffect(() => {
    console.log('🔍 ProfileData changed:', {
      hasProfilePicUrl: !!profileData.profile_pic_url,
      urlLength: profileData.profile_pic_url?.length,
      urlPrefix: profileData.profile_pic_url?.substring(0, 50),
      fullData: profileData
    })
  }, [profileData])

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-dark-200">
          <h2 className="text-2xl font-display font-bold text-dark-900">Profile Settings</h2>
          <button onClick={onClose} className="text-dark-400 hover:text-dark-600 transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-dark-200">
          <button
            onClick={() => setActiveTab('profile')}
            className={`px-6 py-3 font-medium transition-colors relative ${
              activeTab === 'profile'
                ? 'text-primary-600'
                : 'text-dark-600 hover:text-dark-900'
            }`}
          >
            Profile
            {activeTab === 'profile' && (
              <motion.div
                layoutId="activeTab"
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-600"
              />
            )}
          </button>
          <button
            onClick={() => setActiveTab('password')}
            className={`px-6 py-3 font-medium transition-colors relative ${
              activeTab === 'password'
                ? 'text-primary-600'
                : 'text-dark-600 hover:text-dark-900'
            }`}
          >
            Change Password
            {activeTab === 'password' && (
              <motion.div
                layoutId="activeTab"
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-600"
              />
            )}
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-180px)]">
          <AnimatePresence mode="wait">
            {activeTab === 'profile' ? (
              <motion.form
                key="profile"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                onSubmit={handleProfileSubmit}
                className="space-y-6"
              >
                {/* Profile Picture */}
                <div className="flex items-center gap-6">
                  <div className="relative">
                    {profileData.profile_pic_url ? (
                      <img
                        src={profileData.profile_pic_url}
                        alt="Profile"
                        className="w-24 h-24 rounded-full object-cover"
                        onLoad={() => console.log('✅ Image loaded successfully')}
                        onError={(e) => {
                          console.error('❌ Image failed to load:', {
                            src: e.target.src?.substring(0, 100),
                            error: e
                          })
                        }}
                      />
                    ) : (
                      <div className="w-24 h-24 rounded-full bg-gradient-to-br from-primary-500 to-accent-purple flex items-center justify-center">
                        <span className="text-3xl font-bold text-white">
                          {user?.first_name?.[0]}{user?.last_name?.[0]}
                        </span>
                      </div>
                    )}
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      disabled={uploadingImage}
                      className="absolute bottom-0 right-0 p-2 bg-primary-600 text-white rounded-full hover:bg-primary-700 transition-colors shadow-lg"
                    >
                      {uploadingImage ? (
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <Camera className="w-4 h-4" />
                      )}
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
                    <h3 className="font-semibold text-dark-900">Profile Photo</h3>
                    <p className="text-sm text-dark-600">JPG, PNG or GIF, max 5MB</p>
                  </div>
                </div>

                {/* Name Fields */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-dark-800 mb-2">
                      First Name
                    </label>
                    <input
                      type="text"
                      name="first_name"
                      value={profileData.first_name}
                      onChange={handleProfileChange}
                      className="input"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-dark-800 mb-2">
                      Last Name
                    </label>
                    <input
                      type="text"
                      name="last_name"
                      value={profileData.last_name}
                      onChange={handleProfileChange}
                      className="input"
                      required
                    />
                  </div>
                </div>

                {/* Email */}
                <div>
                  <label className="block text-sm font-medium text-dark-800 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={profileData.email}
                    onChange={handleProfileChange}
                    className="input"
                    required
                  />
                </div>

                {/* Bio */}
                <div>
                  <label className="block text-sm font-medium text-dark-800 mb-2">
                    Bio
                  </label>
                  <textarea
                    name="bio"
                    value={profileData.bio}
                    onChange={handleProfileChange}
                    rows={4}
                    className="input resize-none"
                    placeholder="Tell us about yourself..."
                  />
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={saving}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  {saving ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="w-5 h-5" />
                      Save Changes
                    </>
                  )}
                </button>
              </motion.form>
            ) : (
              <motion.form
                key="password"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                onSubmit={handlePasswordSubmit}
                className="space-y-6"
              >
                {/* Current Password */}
                <div>
                  <label className="block text-sm font-medium text-dark-800 mb-2">
                    Current Password
                  </label>
                  <div className="relative">
                    <input
                      type={showPasswords.current ? 'text' : 'password'}
                      name="current_password"
                      value={passwordData.current_password}
                      onChange={handlePasswordChange}
                      className="input pr-10"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPasswords(prev => ({ ...prev, current: !prev.current }))}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-dark-400 hover:text-dark-600"
                    >
                      {showPasswords.current ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                {/* New Password */}
                <div>
                  <label className="block text-sm font-medium text-dark-800 mb-2">
                    New Password
                  </label>
                  <div className="relative">
                    <input
                      type={showPasswords.new ? 'text' : 'password'}
                      name="new_password"
                      value={passwordData.new_password}
                      onChange={handlePasswordChange}
                      className="input pr-10"
                      required
                      minLength={8}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPasswords(prev => ({ ...prev, new: !prev.new }))}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-dark-400 hover:text-dark-600"
                    >
                      {showPasswords.new ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                  <p className="text-sm text-dark-600 mt-1">Must be at least 8 characters long</p>
                </div>

                {/* Confirm Password */}
                <div>
                  <label className="block text-sm font-medium text-dark-800 mb-2">
                    Confirm New Password
                  </label>
                  <div className="relative">
                    <input
                      type={showPasswords.confirm ? 'text' : 'password'}
                      name="confirm_password"
                      value={passwordData.confirm_password}
                      onChange={handlePasswordChange}
                      className="input pr-10"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPasswords(prev => ({ ...prev, confirm: !prev.confirm }))}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-dark-400 hover:text-dark-600"
                    >
                      {showPasswords.confirm ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={saving}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  {saving ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Changing Password...
                    </>
                  ) : (
                    <>
                      <Save className="w-5 h-5" />
                      Change Password
                    </>
                  )}
                </button>
              </motion.form>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </motion.div>
  )
}
