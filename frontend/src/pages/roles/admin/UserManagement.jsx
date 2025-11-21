import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { motion } from 'framer-motion'
import { Users, Search, Filter, Edit2, Trash2, Shield, Lock, Mail, MoreVertical, UserPlus, Download, RefreshCw } from 'lucide-react'
import { Link } from 'react-router-dom'
import { adminApi } from '@services/apiServices'
import { SuccessModal, ErrorModal, ConfirmModal, PromptModal } from '@components/Modal'

export default function UserManagement() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [selectedUser, setSelectedUser] = useState(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [showResetPassword, setShowResetPassword] = useState(false)
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [showErrorModal, setShowErrorModal] = useState(false)
  const [modalMessage, setModalMessage] = useState('')

  const { data: usersData, isLoading, refetch } = useQuery(
    ['admin-users', page, search, roleFilter, statusFilter],
    () => adminApi.getUsers({ page, search, role: roleFilter, status: statusFilter }),
    { keepPreviousData: true }
  )

  const deleteMutation = useMutation(
    (userId) => adminApi.deleteUser(userId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('admin-users')
        setModalMessage('User deleted successfully')
        setShowSuccessModal(true)
        setShowDeleteConfirm(false)
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

  const handleDeleteUser = () => {
    if (selectedUser) {
      deleteMutation.mutate(selectedUser.user_id)
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
          <button className="btn-primary flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export CSV
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
                          <button
                            onClick={() => {
                              setSelectedUser(user)
                              setShowDeleteConfirm(true)
                            }}
                            className="p-2 hover:bg-red-100 rounded-lg transition-colors"
                            title="Delete User"
                          >
                            <Trash2 className="w-4 h-4 text-red-600" />
                          </button>
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
      <ConfirmModal
        isOpen={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        onConfirm={handleDeleteUser}
        title="Delete User"
        message={`Are you sure you want to delete ${selectedUser?.full_name}? This action cannot be undone.`}
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
