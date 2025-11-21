import { useState } from 'react'
import { useQuery } from 'react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { Shield, Users, Activity, Settings, AlertTriangle, TrendingUp, Database, Lock, User, ArrowLeft } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import api from '@services/api'
import { useAuthStore } from '@store/authStore'
import ProfileSettings from '@components/ProfileSettings'

export default function AdminDashboard() {
  const { user } = useAuthStore()
  const navigate = useNavigate()
  const [showProfileSettings, setShowProfileSettings] = useState(false)

  const { data: stats } = useQuery('admin-stats', async () => {
    const response = await api.get('/admin/dashboard')
    return response.data
  })

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
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
              Admin Dashboard
            </h1>
            <p className="text-dark-600">System overview and management</p>
          </div>
        </div>
        <button
          onClick={() => setShowProfileSettings(true)}
          className="btn-secondary flex items-center gap-2"
        >
          <User className="w-5 h-5" />
          Profile Settings
        </button>
      </div>

      {/* Profile Settings Modal */}
      <AnimatePresence>
        {showProfileSettings && (
          <ProfileSettings onClose={() => setShowProfileSettings(false)} />
        )}
      </AnimatePresence>

      {/* Stats Grid */}
      <div className="grid md:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={<Users className="w-6 h-6" />}
          label="Total Users"
          value={stats?.total_users || 0}
          color="primary-500"
        />
        <StatCard
          icon={<Activity className="w-6 h-6" />}
          label="Active Projects"
          value={stats?.active_projects || 0}
          color="accent-green"
        />
        <StatCard
          icon={<Database className="w-6 h-6" />}
          label="Storage Used"
          value={`${stats?.storage_used || 0} GB`}
          color="accent-purple"
        />
        <StatCard
          icon={<AlertTriangle className="w-6 h-6" />}
          label="System Alerts"
          value={stats?.system_alerts || 0}
          color="accent-orange"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-4 gap-6 mb-8">
        <QuickActionCard
          title="User Management"
          description="Manage users & roles"
          icon={<Users className="w-8 h-8" />}
          color="primary-500"
          link="/admin/users"
        />
        <QuickActionCard
          title="System Settings"
          description="Configure system"
          icon={<Settings className="w-8 h-8" />}
          color="accent-purple"
          link="/admin/settings"
        />
        <QuickActionCard
          title="Security"
          description="Security & logs"
          icon={<Lock className="w-8 h-8" />}
          color="accent-pink"
          link="/admin/security"
        />
        <QuickActionCard
          title="Analytics"
          description="Platform analytics"
          icon={<TrendingUp className="w-8 h-8" />}
          color="accent-green"
          link="/admin/analytics"
        />
      </div>

      {/* System Overview */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="card">
          <h2 className="text-xl font-bold text-dark-900 mb-4">System Health</h2>
          <div className="space-y-4">
            <HealthMetric label="API Response Time" value="45ms" status="good" />
            <HealthMetric label="Database" value="Operational" status="good" />
            <HealthMetric label="AI Services" value="Operational" status="good" />
            <HealthMetric label="Storage" value="78% Used" status="warning" />
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-bold text-dark-900 mb-4">Recent Activity</h2>
          {stats?.recent_activity?.length > 0 ? (
            <div className="space-y-3">
              {stats.recent_activity.map((activity, index) => (
                <ActivityItem key={index} activity={activity} />
              ))}
            </div>
          ) : (
            <p className="text-dark-600 text-center py-8">No recent activity</p>
          )}
        </div>
      </div>

      {/* User Statistics */}
      <div className="card mb-8">
        <h2 className="text-xl font-bold text-dark-900 mb-4">User Statistics</h2>
        <div className="grid md:grid-cols-5 gap-4">
          <UserStatCard role="Filmmakers" count={stats?.users_by_role?.filmmaker || 0} />
          <UserStatCard role="Investors" count={stats?.users_by_role?.investor || 0} />
          <UserStatCard role="Actors" count={stats?.users_by_role?.actor || 0} />
          <UserStatCard role="Crew" count={stats?.users_by_role?.crew_member || 0} />
          <UserStatCard role="Admins" count={stats?.users_by_role?.admin || 0} />
        </div>
      </div>

      {/* Recent Users */}
      <div className="card">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-dark-900">Recent Users</h2>
          <Link to="/admin/users" className="text-primary-600 hover:text-primary-700 font-medium">
            View All →
          </Link>
        </div>

        {stats?.recent_users?.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-dark-200">
                  <th className="text-left py-3 px-4 text-sm font-medium text-dark-700">User</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-dark-700">Email</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-dark-700">Role</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-dark-700">Status</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-dark-700">Joined</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-dark-700">Actions</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent_users.map((user) => (
                  <UserRow key={user.id} user={user} />
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState />
        )}
      </div>
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

function QuickActionCard({ title, description, icon, color, link }) {
  return (
    <Link to={link}>
      <motion.div
        whileHover={{ scale: 1.02 }}
        className="card cursor-pointer group"
      >
        <div className={`text-${color} mb-4 group-hover:scale-110 transition-transform`}>
          {icon}
        </div>
        <h3 className="font-bold text-dark-900 mb-2">{title}</h3>
        <p className="text-sm text-dark-600">{description}</p>
      </motion.div>
    </Link>
  )
}

function HealthMetric({ label, value, status }) {
  const statusColors = {
    good: 'text-accent-green',
    warning: 'text-accent-orange',
    error: 'text-red-500'
  }

  return (
    <div className="flex justify-between items-center py-2 border-b border-dark-200">
      <span className="text-dark-700">{label}</span>
      <span className={`font-medium ${statusColors[status]}`}>{value}</span>
    </div>
  )
}

function ActivityItem({ activity }) {
  return (
    <div className="flex items-start gap-3 p-3 bg-dark-200 rounded-lg">
      <Activity className="w-4 h-4 text-primary-500 mt-1" />
      <div className="flex-1">
        <p className="text-sm text-dark-900">{activity.description}</p>
        <p className="text-xs text-dark-600 mt-1">{activity.timestamp}</p>
      </div>
    </div>
  )
}

function UserStatCard({ role, count }) {
  return (
    <div className="p-4 bg-dark-200 rounded-lg text-center">
      <div className="text-2xl font-bold text-dark-900 mb-1">{count}</div>
      <div className="text-sm text-dark-600">{role}</div>
    </div>
  )
}

function UserRow({ user }) {
  return (
    <tr className="border-b border-dark-200 hover:bg-dark-200">
      <td className="py-3 px-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-primary-500 flex items-center justify-center text-white text-sm font-bold">
            {user.full_name?.charAt(0) || 'U'}
          </div>
          <span className="text-sm text-dark-900">{user.full_name}</span>
        </div>
      </td>
      <td className="py-3 px-4 text-sm text-dark-700">{user.email}</td>
      <td className="py-3 px-4">
        <span className="px-2 py-1 bg-primary-500 text-white text-xs rounded">
          {user.role}
        </span>
      </td>
      <td className="py-3 px-4">
        <span className={`px-2 py-1 text-xs rounded ${
          user.is_active ? 'bg-accent-green text-white' : 'bg-dark-300 text-dark-700'
        }`}>
          {user.is_active ? 'Active' : 'Inactive'}
        </span>
      </td>
      <td className="py-3 px-4 text-sm text-dark-700">
        {new Date(user.created_at).toLocaleDateString()}
      </td>
      <td className="py-3 px-4 text-right">
        <Link to={`/admin/users/${user.id}`} className="text-primary-600 hover:underline text-sm">
          View
        </Link>
      </td>
    </tr>
  )
}

function EmptyState() {
  return (
    <div className="text-center py-12">
      <Shield className="w-16 h-16 text-dark-400 mx-auto mb-4" />
      <p className="text-dark-600 mb-4">No data available</p>
    </div>
  )
}
