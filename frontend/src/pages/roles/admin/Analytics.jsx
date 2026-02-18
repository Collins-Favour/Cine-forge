import { useState } from 'react'
import { useQuery } from 'react-query'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { TrendingUp, Users, FolderOpen, MessageSquare, Calendar, BarChart3, Activity, Download, ArrowLeft } from 'lucide-react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { adminApi } from '@services/apiServices'

export default function Analytics() {
  const navigate = useNavigate()
  const [timeRange, setTimeRange] = useState(30)

  const { data: analyticsData, isLoading } = useQuery(
    ['admin-analytics', timeRange],
    () => adminApi.getAnalytics(timeRange)
  )

  const analytics = analyticsData?.data || {}
  const newUsers = analytics.new_users || []
  const messages = analytics.messages || []

  const COLORS = ['#8B5CF6', '#EC4899', '#10B981', '#F59E0B', '#3B82F6']

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
              Platform Analytics
            </h1>
            <p className="text-dark-600">Comprehensive platform insights and metrics</p>
          </div>
        </div>
        <div className="flex gap-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(parseInt(e.target.value))}
            className="input"
          >
            <option value={7}>Last 7 Days</option>
            <option value={30}>Last 30 Days</option>
            <option value={90}>Last 90 Days</option>
            <option value={365}>Last Year</option>
          </select>
          <button className="btn-primary flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export Report
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <>
          {/* Key Metrics */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <MetricCard
              icon={<Users className="w-6 h-6" />}
              label="Total New Users"
              value={newUsers.reduce((sum, item) => sum + item.count, 0)}
              change="+12%"
              color="primary-500"
            />
            <MetricCard
              icon={<MessageSquare className="w-6 h-6" />}
              label="Total Messages"
              value={messages.reduce((sum, item) => sum + item.count, 0)}
              change="+24%"
              color="accent-green"
            />
            <MetricCard
              icon={<Activity className="w-6 h-6" />}
              label="Engagement Rate"
              value="78%"
              change="+5%"
              color="accent-pink"
            />
          </div>

          {/* Charts */}
          <div className="grid md:grid-cols-2 gap-6 mb-6">
            {/* New Users Chart */}
            <ChartCard title="New Users" icon={<Users className="w-5 h-5" />}>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={newUsers}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="date" stroke="#6B7280" fontSize={12} />
                  <YAxis stroke="#6B7280" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#FFFFFF', border: '1px solid #E5E7EB' }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="count" 
                    stroke="#8B5CF6" 
                    strokeWidth={2}
                    dot={{ fill: '#8B5CF6' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </ChartCard>

            {/* Messages Chart */}
            <ChartCard title="Message Activity" icon={<MessageSquare className="w-5 h-5" />}>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={messages}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="date" stroke="#6B7280" fontSize={12} />
                  <YAxis stroke="#6B7280" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#FFFFFF', border: '1px solid #E5E7EB' }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="count" 
                    stroke="#10B981" 
                    strokeWidth={2}
                    dot={{ fill: '#10B981' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </ChartCard>
          </div>

          {/* Activity Stats */}
          <div className="grid md:grid-cols-3 gap-6">
            <ActivityCard
              title="Peak Activity Time"
              value="2:00 PM - 4:00 PM"
              description="Most active hours"
              icon={<Calendar className="w-5 h-5" />}
            />
            <ActivityCard
              title="Avg Session Duration"
              value="42 minutes"
              description="Per user session"
              icon={<Activity className="w-5 h-5" />}
            />
            <ActivityCard
              title="User Retention"
              value="68%"
              description="30-day retention rate"
              icon={<TrendingUp className="w-5 h-5" />}
            />
          </div>
        </>
      )}
    </div>
  )
}

function MetricCard({ icon, label, value, change, color }) {
  const isPositive = change.startsWith('+')
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <div className="flex items-start justify-between mb-4">
        <div className={`p-3 bg-${color} bg-opacity-10 rounded-lg text-${color}`}>
          {icon}
        </div>
        <span className={`text-sm font-medium ${isPositive ? 'text-accent-green' : 'text-red-500'}`}>
          {change}
        </span>
      </div>
      <div className="text-3xl font-bold text-dark-900 mb-1">{value}</div>
      <div className="text-sm text-dark-600">{label}</div>
    </motion.div>
  )
}

function ChartCard({ title, icon, children }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <div className="flex items-center gap-2 mb-4">
        <div className="text-primary-600">{icon}</div>
        <h3 className="text-lg font-bold text-dark-900">{title}</h3>
      </div>
      {children}
    </motion.div>
  )
}

function ActivityCard({ title, value, description, icon }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <div className="flex items-start gap-4">
        <div className="p-3 bg-primary-100 rounded-lg text-primary-600">
          {icon}
        </div>
        <div>
          <div className="text-sm text-dark-600 mb-1">{title}</div>
          <div className="text-2xl font-bold text-dark-900 mb-1">{value}</div>
          <div className="text-xs text-dark-500">{description}</div>
        </div>
      </div>
    </motion.div>
  )
}
