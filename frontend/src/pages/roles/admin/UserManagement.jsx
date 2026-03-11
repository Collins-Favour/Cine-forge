import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { motion } from 'framer-motion'
import { Users, Search, Filter, Edit2, Trash2, Shield, Lock, Mail, MoreVertical, UserPlus, Download, RefreshCw, ArrowLeft } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { adminApi } from '@services/apiServices'
import Modal, { SuccessModal, ErrorModal, ConfirmModal, PromptModal } from '@components/Modal'

export default function UserManagement() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [selectedUser, setSelectedUser] = useState(null)
  const [showDeleteChoice, setShowDeleteChoice] = useState(false)
  const [showFinalConfirm, setShowFinalConfirm] = useState(false)
  const [actionType, setActionType] = useState('') // 'deactivate' or 'delete'
  const [showResetPassword, setShowResetPassword] = useState(false)
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [showErrorModal, setShowErrorModal] = useState(false)
  const [modalMessage, setModalMessage] = useState('')
  const [isExporting, setIsExporting] = useState(false)

  const { data: usersData, isLoading, refetch } = useQuery(
    ['admin-users', page, search, roleFilter, statusFilter],
    () => adminApi.getUsers({ page, search, role: roleFilter, status: statusFilter }),
    { keepPreviousData: true }
  )

  const deactivateMutation = useMutation(
    (userId) => adminApi.deactivateUser(userId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('admin-users')
        setModalMessage('User deactivated successfully')
        setShowSuccessModal(true)
        setShowFinalConfirm(false)
      },
      onError: () => {
        setModalMessage('Failed to deactivate user')
        setShowErrorModal(true)
      }
    }
  )

  const activateMutation = useMutation(
    (userId) => adminApi.activateUser(userId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('admin-users')
        setModalMessage('User activated successfully')
        setShowSuccessModal(true)
      },
      onError: () => {
        setModalMessage('Failed to activate user')
        setShowErrorModal(true)
      }
    }
  )

  const deleteMutation = useMutation(
    (userId) => adminApi.deleteUser(userId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('admin-users')
        setModalMessage('User permanently deleted from database')
        setShowSuccessModal(true)
        setShowFinalConfirm(false)
      },
      onError: () => {
        setModalMessage('Failed to delete user')
        setShowErrorModal(true)
      }
    }
  )

  const resetPasswordMutation = useMutation(
    ({ userId, password }) => adminApi.resetUserPassword(userId, password),
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

  const handleActionChoice = (action) => {
    setActionType(action)
    setShowDeleteChoice(false)
    setShowFinalConfirm(true)
  }

  const handleFinalConfirm = () => {
    if (selectedUser) {
      if (actionType === 'deactivate') {
        deactivateMutation.mutate(selectedUser.user_id)
      } else if (actionType === 'delete') {
        deleteMutation.mutate(selectedUser.user_id)
      }
    }
  }

  const handleResetPassword = (newPassword) => {
    if (selectedUser && newPassword) {
      resetPasswordMutation.mutate({
        userId: selectedUser.user_id,
        password: newPassword
      })
    }
  }

  const handleExportUsers = async () => {
    try {
      setIsExporting(true)
      const response = await adminApi.exportUsers()
      
      // Create blob and download
      const blob = new Blob([response.data], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `users_export_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Export failed:', error)
      setModalMessage('Failed to export users. Please try again.')
      setShowErrorModal(true)
    } finally {
      setIsExporting(false)
    }
  }

  const users = usersData?.data?.users || []
  const totalUsers = usersData?.data?.total || 0
  const totalPages = usersData?.data?.pages || 1

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-start mb-8">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate(-1)}
            className="btn-secondary flex items-center gap-2 px-3 py-2"
            title="Go back"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-3xl font-display font-bold text-dark-900 mb-2">
              User Management
            </h1>
            <p className="text-dark-600">Manage all platform users and permissions</p>
          </div>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => refetch()}
            className="btn-secondary flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button
            onClick={handleExportUsers}
            disabled={isExporting}
            className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download className="w-4 h-4" />
            {isExporting ? 'Exporting...' : 'Export CSV'}
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid md:grid-cols-4 gap-6 mb-8">
        <StatCard label="Total Users" value={totalUsers} color="primary-500" />
        <StatCard label="Active Users" value={users.filter(u => u.is_active).length} color="accent-green" />
        <StatCard label="Verified Users" value={users.filter(u => u.is_verified).length} color="accent-purple" />
        <StatCard label="Admin Users" value={users.filter(u => u.role === 'admin').length} color="accent-pink" />
      </div>

      {/* Filters */}
      <div className="card mb-6">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-500" />
              <input
                type="text"
                placeholder="Search users..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="input pl-10 w-full"
              />
            </div>
          </div>
          
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="input min-w-[150px]"
          >
            <option value="">All Roles</option>
            <option value="student">Student</option>
            <option value="filmmaker">Filmmaker</option>
            <option value="professional">Professional</option>
            <option value="admin">Admin</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input min-w-[150px]"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="verified">Verified</option>
            <option value="unverified">Unverified</option>
          </select>
        </div>
      </div>

      {/* Users Table */}
      <div className="card">
        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : users.length === 0 ? (
          <div className="text-center py-12">
            <Users className="w-16 h-16 text-dark-400 mx-auto mb-4" />
            <p className="text-dark-600">No users found</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-dark-200">
                    <th className="text-left py-3 px-4 text-sm font-medium text-dark-700">User</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-dark-700">Email</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-dark-700">Role</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-dark-700">Status</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-dark-700">Last Login</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-dark-700">Joined</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-dark-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.user_id} className="border-b border-dark-200 hover:bg-dark-100">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-primary-500 flex items-center justify-center text-white font-semibold">
                            {user.full_name?.charAt(0) || 'U'}
                          </div>
                          <div>
                            <div className="font-medium text-dark-900">{user.full_name}</div>
                            <div className="text-sm text-dark-600">@{user.username}</div>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-sm text-dark-700">{user.email}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 text-xs rounded font-medium ${getRoleBadgeColor(user.role)}`}>
                          {user.role}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex flex-col gap-1">
                          <span className={`px-2 py-1 text-xs rounded inline-block ${
                            user.is_active ? 'bg-accent-green text-white' : 'bg-dark-300 text-dark-700'
                          }`}>
                            {user.is_active ? 'Active' : 'Inactive'}
                          </span>
                          {user.is_verified && (
                            <span className="px-2 py-1 bg-accent-purple text-white text-xs rounded inline-block">
                              Verified
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-sm text-dark-700">
                        {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                      </td>
                      <td className="py-3 px-4 text-sm text-dark-700">
                        {new Date(user.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center justify-end gap-2">
                          <Link
                            to={`/admin/users/${user.user_id}`}
                            className="p-2 hover:bg-dark-200 rounded-lg transition-colors"
                            title="View Details"
                          >
                            <Edit2 className="w-4 h-4 text-dark-600" />
                          </Link>
                          <button
                            onClick={() => {
                              setSelectedUser(user)
                              setShowResetPassword(true)
                            }}
                            className="p-2 hover:bg-dark-200 rounded-lg transition-colors"
                            title="Reset Password"
                          >
                            <Lock className="w-4 h-4 text-dark-600" />
                          </button>
                          {!user.is_active ? (
                            <button
                              onClick={() => activateMutation.mutate(user.user_id)}
                              className="p-2 hover:bg-green-100 rounded-lg transition-colors"
                              title="Activate User"
                            >
                              <Shield className="w-4 h-4 text-green-600" />
                            </button>
                          ) : (
                            <button
                              onClick={() => {
                                setSelectedUser(user)
                                setShowDeleteChoice(true)
                              }}
                              className="p-2 hover:bg-red-100 rounded-lg transition-colors"
                              title="Manage User"
                            >
                              <Trash2 className="w-4 h-4 text-red-600" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-between items-center mt-6 pt-6 border-t border-dark-200">
                <div className="text-sm text-dark-600">
                  Showing page {page} of {totalPages}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Modals */}
      {/* Action Choice Modal */}
      <Modal
        isOpen={showDeleteChoice}
        onClose={() => setShowDeleteChoice(false)}
        title="User Action"
        size="md"
      >
        <div className="p-6">
          <p className="text-dark-700 mb-6">
            Choose an action for <strong>{selectedUser?.full_name || selectedUser?.username}</strong>:
          </p>
          <div className="space-y-4">
            <button
              onClick={() => handleActionChoice('deactivate')}
              className="w-full p-4 border-2 border-dark-200 rounded-lg hover:border-yellow-500 hover:bg-yellow-50 transition-all text-left"
            >
              <div className="flex items-start gap-3">
                <div className="p-2 bg-yellow-100 rounded-lg">
                  <Shield className="w-5 h-5 text-yellow-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-dark-900 mb-1">Deactivate Account</h4>
                  <p className="text-sm text-dark-600">
                    Temporarily disable the account. The user won't be able to log in, but all data remains in the database.
                  </p>
                </div>
              </div>
            </button>
            <button
              onClick={() => handleActionChoice('delete')}
              className="w-full p-4 border-2 border-dark-200 rounded-lg hover:border-red-500 hover:bg-red-50 transition-all text-left"
            >
              <div className="flex items-start gap-3">
                <div className="p-2 bg-red-100 rounded-lg">
                  <Trash2 className="w-5 h-5 text-red-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-dark-900 mb-1">Permanently Delete</h4>
                  <p className="text-sm text-dark-600">
                    Remove user and all associated data from the database. This action cannot be undone.
                  </p>
                </div>
              </div>
            </button>
          </div>
          <div className="flex justify-end mt-6">
            <button onClick={() => setShowDeleteChoice(false)} className="btn-secondary">
              Cancel
            </button>
          </div>
        </div>
      </Modal>

      {/* Final Confirmation Modal */}
      <ConfirmModal
        isOpen={showFinalConfirm}
        onClose={() => setShowFinalConfirm(false)}
        onConfirm={handleFinalConfirm}
        title={actionType === 'deactivate' ? 'Confirm Deactivation' : 'Confirm Deletion'}
        message={
          actionType === 'deactivate'
            ? `Are you sure you want to deactivate ${selectedUser?.full_name || selectedUser?.username}? They will not be able to log in until reactivated.`
            : `Are you sure you want to permanently delete ${selectedUser?.full_name || selectedUser?.username}? This will remove all their data from the database and cannot be undone.`
        }
        confirmText={actionType === 'deactivate' ? 'Deactivate' : 'Delete Permanently'}
        variant="danger"
      />

      <PromptModal
        isOpen={showResetPassword}
        onClose={() => setShowResetPassword(false)}
        onSubmit={handleResetPassword}
        title="Reset Password"
        message={`Enter new password for ${selectedUser?.full_name}`}
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

function StatCard({ label, value, color }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
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
