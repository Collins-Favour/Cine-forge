import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { motion } from 'framer-motion'
import { 
  ArrowLeft, Save, User, Mail, Shield, Calendar, Activity, 
  FolderOpen, MessageSquare, Edit2, Trash2, Lock 
} from 'lucide-react'
import { adminApi } from '@services/apiServices'
import { SuccessModal, ErrorModal, ConfirmModal, PromptModal } from '@components/Modal'

export default function UserDetail() {
  const { userId } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({})
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [showResetPassword, setShowResetPassword] = useState(false)
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [showErrorModal, setShowErrorModal] = useState(false)
  const [modalMessage, setModalMessage] = useState('')

  const { data: userData, isLoading } = useQuery(
    ['admin-user-detail', userId],
    () => adminApi.getUserDetails(userId),
    {
      onSuccess: (data) => {
        setFormData(data.data.user)
      }
    }
  )

  const updateMutation = useMutation(
    (data) => adminApi.updateUser(userId, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['admin-user-detail', userId])
        queryClient.invalidateQueries('admin-users')
        setModalMessage('User updated successfully')
        setShowSuccessModal(true)
        setIsEditing(false)
      },
      onError: () => {
        setModalMessage('Failed to update user')
        setShowErrorModal(true)
      }
    }
  )

  const deleteMutation = useMutation(
    () => adminApi.deleteUser(userId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('admin-users')
        navigate('/admin/users')
      },
      onError: () => {
        setModalMessage('Failed to delete user')
        setShowErrorModal(true)
      }
    }
  )

  const resetPasswordMutation = useMutation(
    (password) => adminApi.resetUserPassword(userId, password),
    {
      onSuccess: () => {
        setModalMessage('Password reset successfully')
        setShowSuccessModal(true)
        setShowResetPassword(false)
      },
      onError: () => {
        setModalMessage('Failed to reset password')
        setShowErrorModal(true)
      }
    }
  )

  const handleSave = () => {
    updateMutation.mutate(formData)
  }

  const handleDelete = () => {
    deleteMutation.mutate()
  }

  const handleResetPassword = (newPassword) => {
    if (newPassword) {
      resetPasswordMutation.mutate(newPassword)
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const user = userData?.data?.user
  const stats = userData?.data?.stats
  const activity = userData?.data?.recent_activity || []

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div className="flex items-start gap-4">
          <button
            onClick={() => navigate('/admin/users')}
            className="p-2 hover:bg-dark-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-3xl font-display font-bold text-dark-900 mb-2">
              User Details
            </h1>
            <p className="text-dark-600">Manage user information and permissions</p>
          </div>
        </div>
        
        <div className="flex gap-2">
          {isEditing ? (
            <>
              <button
                onClick={() => setIsEditing(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={updateMutation.isLoading}
                className="btn-primary flex items-center gap-2"
              >
                <Save className="w-4 h-4" />
                Save Changes
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => setShowResetPassword(true)}
                className="btn-secondary flex items-center gap-2"
              >
                <Lock className="w-4 h-4" />
                Reset Password
              </button>
              <button
                onClick={() => setIsEditing(true)}
                className="btn-primary flex items-center gap-2"
              >
                <Edit2 className="w-4 h-4" />
                Edit User
              </button>
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="btn-secondary text-red-600 hover:bg-red-50 flex items-center gap-2"
              >
                <Trash2 className="w-4 h-4" />
                Delete
              </button>
            </>
          )}
        </div>
      </div>

      {/* User Info Card */}
      <div className="card mb-6">
        <div className="flex items-start gap-6">
          <div className="w-24 h-24 rounded-full bg-primary-500 flex items-center justify-center text-white text-3xl font-bold">
            {user?.first_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
          </div>
          
          <div className="flex-1">
            {isEditing ? (
              <div className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-dark-700 mb-1">
                      First Name
                    </label>
                    <input
                      type="text"
                      value={formData.first_name || ''}
                      onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                      className="input w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-dark-700 mb-1">
                      Last Name
                    </label>
                    <input
                      type="text"
                      value={formData.last_name || ''}
                      onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                      className="input w-full"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-dark-700 mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    value={formData.email || ''}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="input w-full"
                  />
                </div>
                
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-dark-700 mb-1">
                      Role
                    </label>
                    <select
                      value={formData.role || 'filmmaker'}
                      onChange={(e) => setFormData({...formData, role: e.target.value})}
                      className="input w-full"
                    >
                      <option value="student">Student</option>
                      <option value="filmmaker">Filmmaker</option>
                      <option value="professional">Professional</option>
                      <option value="admin">Admin</option>
                    </select>
                  </div>
                  
                  <div className="flex items-end gap-4">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.is_active || false}
                        onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                        className="w-4 h-4 text-primary-600 rounded"
                      />
                      <span className="text-sm font-medium text-dark-700">Active</span>
                    </label>
                    
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.is_verified || false}
                        onChange={(e) => setFormData({...formData, is_verified: e.target.checked})}
                        className="w-4 h-4 text-primary-600 rounded"
                      />
                      <span className="text-sm font-medium text-dark-700">Verified</span>
                    </label>
                  </div>
                </div>
              </div>
            ) : (
              <>
                <h2 className="text-2xl font-bold text-dark-900 mb-2">
                  {user?.first_name} {user?.last_name}
                </h2>
                <p className="text-dark-600 mb-4">@{user?.username}</p>
                
                <div className="flex flex-wrap gap-2 mb-4">
                  <span className={`px-3 py-1 rounded text-sm font-medium ${getRoleBadgeColor(user?.role)}`}>
                    {user?.role}
                  </span>
                  {user?.is_active && (
                    <span className="px-3 py-1 bg-accent-green text-white rounded text-sm font-medium">
                      Active
                    </span>
                  )}
                  {user?.is_verified && (
                    <span className="px-3 py-1 bg-accent-purple text-white rounded text-sm font-medium">
                      Verified
                    </span>
                  )}
                </div>
                
                <div className="grid md:grid-cols-3 gap-4 text-sm">
                  <div className="flex items-center gap-2 text-dark-600">
                    <Mail className="w-4 h-4" />
                    <span>{user?.email}</span>
                  </div>
                  <div className="flex items-center gap-2 text-dark-600">
                    <Calendar className="w-4 h-4" />
                    <span>Joined {new Date(user?.created_at).toLocaleDateString()}</span>
                  </div>
                  {user?.last_login && (
                    <div className="flex items-center gap-2 text-dark-600">
                      <Activity className="w-4 h-4" />
                      <span>Last login {new Date(user?.last_login).toLocaleDateString()}</span>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid md:grid-cols-1 gap-6 mb-6">
        <StatCard
          icon={<Activity className="w-6 h-6" />}
          label="Recent Activities"
          value={stats?.activity_count || 0}
          color="primary-500"
        />
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h3 className="text-xl font-bold text-dark-900 mb-4">Recent Activity</h3>
        {activity.length === 0 ? (
          <p className="text-dark-600 text-center py-8">No recent activity</p>
        ) : (
          <div className="space-y-3">
            {activity.map((item, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-dark-100 rounded-lg">
                <Activity className="w-4 h-4 text-primary-500 mt-1" />
                <div className="flex-1">
                  <p className="text-sm text-dark-900">{item.action}</p>
                  <p className="text-xs text-dark-600 mt-1">{new Date(item.timestamp).toLocaleString()}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modals */}
      <ConfirmModal
        isOpen={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        onConfirm={handleDelete}
        title="Delete User"
        message={`Are you sure you want to delete ${user?.first_name} ${user?.last_name}? This action cannot be undone.`}
      />

      <PromptModal
        isOpen={showResetPassword}
        onClose={() => setShowResetPassword(false)}
        onSubmit={handleResetPassword}
        title="Reset Password"
        message={`Enter new password for ${user?.first_name} ${user?.last_name}`}
        placeholder="New password (min 6 characters)"
        inputType="password"
      />

      <SuccessModal
        isOpen={showSuccessModal}
        onClose={() => setShowSuccessModal(false)}
        message={modalMessage}
      />

      <ErrorModal
        isOpen={showErrorModal}
        onClose={() => setShowErrorModal(false)}
        message={modalMessage}
      />
    </div>
  )
}

function StatCard({ icon, label, value, color }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <div className={`text-${color} mb-4`}>{icon}</div>
      <div className="text-3xl font-bold text-dark-900 mb-1">{value}</div>
      <div className="text-sm text-dark-600">{label}</div>
    </motion.div>
  )
}

function getRoleBadgeColor(role) {
  const colors = {
    admin: 'bg-accent-pink text-white',
    professional: 'bg-accent-purple text-white',
    filmmaker: 'bg-primary-500 text-white',
    student: 'bg-accent-green text-white'
  }
  return colors[role] || 'bg-dark-300 text-dark-700'
}
