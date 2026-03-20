import { useState } from 'react'
import { useQuery } from 'react-query'
import { motion } from 'framer-motion'
import { Shield, AlertTriangle, Activity, User, Clock, MapPin, Filter, Search } from 'lucide-react'
import { adminApi } from '@services/apiServices'

export default function SecurityLogs() {
  const [page, setPage] = useState(1)
  const [filter, setFilter] = useState('')

  const { data: logsData, isLoading } = useQuery(
    ['admin-security-logs', page],
    () => adminApi.getSecurityLogs({ page, per_page: 50 }),
    {
      refetchInterval: 5000, // Refresh every 5 seconds
      refetchIntervalInBackground: true
    }
  )

  const { data: statsData } = useQuery(
    'admin-security-stats',
    () => adminApi.getSecurityStats(),
    {
      refetchInterval: 10000,
      refetchIntervalInBackground: true
    }
  )

  const logs = logsData?.data?.logs || []
  const totalLogs = logsData?.data?.total || 0
  const totalPages = logsData?.data?.pages || 1
  const securityStats = statsData?.data || {}

  const getActionIcon = (action) => {
    if (action.includes('login')) return <User className="w-4 h-4" />
    if (action.includes('delete')) return <AlertTriangle className="w-4 h-4" />
    return <Activity className="w-4 h-4" />
  }

  const getActionColor = (action) => {
    if (action.includes('delete')) return 'text-red-600 bg-red-100'
    if (action.includes('login')) return 'text-accent-green bg-green-100'
    if (action.includes('update')) return 'text-accent-purple bg-purple-100'
    return 'text-primary-600 bg-primary-100'
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-dark-900 mb-2">
              Security & Activity Logs
            </h1>
            <p className="text-dark-600">Monitor system activity and security events</p>
          </div>
          <div className="flex gap-3">
            <button className="btn-secondary flex items-center gap-2">
              <Filter className="w-4 h-4" />
              Filter
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-4 gap-6">
          <StatCard
            icon={<Activity className="w-6 h-6" />}
            label="Total Events"
            value={securityStats.total_events ?? totalLogs}
            color="primary-500"
          />
          <StatCard
            icon={<AlertTriangle className="w-6 h-6" />}
            label="Security Alerts"
            value={securityStats.security_alerts ?? 0}
            color="accent-orange"
          />
          <StatCard
            icon={<User className="w-6 h-6" />}
            label="Active Users Today"
            value={securityStats.active_users_today ?? 0}
            color="accent-green"
          />
          <StatCard
            icon={<Shield className="w-6 h-6" />}
            label="Failed Logins"
            value={securityStats.failed_logins ?? 0}
            color="red-500"
          />
        </div>
      </div>

      {/* Logs Table */}
      <div className="card">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-dark-900">Activity Log</h2>
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
            <input
              type="text"
              placeholder="Search logs..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="input pl-10 w-full"
            />
          </div>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : logs.length === 0 ? (
          <div className="text-center py-12">
            <Shield className="w-16 h-16 text-dark-400 mx-auto mb-4" />
            <p className="text-dark-600">No activity logs found</p>
          </div>
        ) : (
          <>
            <div className="space-y-2">
              {logs.map((log, index) => (
                <motion.div
                  key={log.id || index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.02 }}
                  className="p-4 bg-dark-100 hover:bg-dark-200 rounded-lg transition-colors"
                >
                  <div className="flex items-start gap-4">
                    <div className={`p-2 rounded-lg ${getActionColor(log.action || '')}`}>
                      {getActionIcon(log.action || '')}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4 mb-2">
                        <div>
                          <div className="font-medium text-dark-900 mb-1">
                            {log.action || 'Unknown Action'}
                          </div>
                          <div className="text-sm text-dark-600">
                            {log.description || 'No description available'}
                          </div>
                        </div>
                        <div className="text-xs text-dark-500 whitespace-nowrap">
                          {new Date(log.timestamp).toLocaleString()}
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-4 text-xs text-dark-600">
                        <div className="flex items-center gap-1">
                          <User className="w-3 h-3" />
                          <span>{log.username || 'Unknown'}</span>
                        </div>
                        {log.ip_address && (
                          <div className="flex items-center gap-1">
                            <MapPin className="w-3 h-3" />
                            <span>{log.ip_address}</span>
                          </div>
                        )}
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          <span>ID: {log.id || log.user_id || 'N/A'}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-between items-center mt-6 pt-6 border-t border-dark-200">
                <div className="text-sm text-dark-600">
                  Page {page} of {totalPages} ({totalLogs} total events)
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
