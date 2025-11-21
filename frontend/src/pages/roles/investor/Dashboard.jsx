import { useState } from 'react'
import { useQuery } from 'react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { DollarSign, TrendingUp, FileText, CheckCircle, AlertCircle, Settings, ArrowLeft } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import api from '@services/api'
import { useAuthStore } from '@store/authStore'
import ProfileSettings from '@components/ProfileSettings'

export default function InvestorDashboard() {
  const { user } = useAuthStore()
  const navigate = useNavigate()
  const [showProfileSettings, setShowProfileSettings] = useState(false)

  const { data: stats } = useQuery('investor-stats', async () => {
    const response = await api.get(`/users/${user.user_id}/dashboard`)
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
              Investor Dashboard
            </h1>
            <p className="text-dark-600">Monitor investments and project opportunities</p>
          </div>
        </div>
        <button
          onClick={() => setShowProfileSettings(true)}
          className="btn-secondary flex items-center gap-2"
        >
          <Settings className="w-5 h-5" />
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
          icon={<DollarSign className="w-6 h-6" />}
          label="Total Projects"
          value={stats?.total_projects || 0}
          color="accent-green"
        />
        <StatCard
          icon={<TrendingUp className="w-6 h-6" />}
          label="Active Projects"
          value={stats?.active_projects || 0}
          color="primary-500"
        />
        <StatCard
          icon={<CheckCircle className="w-6 h-6" />}
          label="Collaborations"
          value={stats?.collaborations || 0}
          color="accent-purple"
        />
        <StatCard
          icon={<AlertCircle className="w-6 h-6" />}
          label="Storyboards"
          value={stats?.total_storyboards || 0}
          color="accent-orange"
        />
      </div>

      {/* Investment Opportunities */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="card">
          <h2 className="text-xl font-bold text-dark-900 mb-4">Investment Opportunities</h2>
          <div className="space-y-4">
            {stats?.opportunities?.length > 0 ? (
              stats.opportunities.map((opp) => (
                <OpportunityCard key={opp.id} opportunity={opp} />
              ))
            ) : (
              <p className="text-dark-600 text-center py-8">No opportunities available</p>
            )}
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-bold text-dark-900 mb-4">Portfolio Performance</h2>
          <div className="space-y-4">
            <PerformanceMetric label="ROI" value="+15.3%" positive />
            <PerformanceMetric label="Projects Funded" value={stats?.projects_funded || 0} />
            <PerformanceMetric label="Avg. Investment" value={`$${stats?.avg_investment || 0}`} />
          </div>
        </div>
      </div>

      {/* Active Investments */}
      <div className="card">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-dark-900">Active Investments</h2>
          <Link to="/investments" className="text-primary-600 hover:text-primary-700 font-medium">
            View All →
          </Link>
        </div>

        {stats?.recent_projects?.length > 0 ? (
          <div className="space-y-4">
            {stats.recent_projects.map((project) => (
              <InvestmentCard key={project.project_id} project={project} />
            ))}
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

function OpportunityCard({ opportunity }) {
  return (
    <div className="p-4 bg-dark-200 rounded-lg">
      <h3 className="font-medium text-dark-900 mb-1">{opportunity.title}</h3>
      <p className="text-sm text-dark-600 mb-2">{opportunity.description}</p>
      <div className="flex justify-between items-center">
        <span className="text-accent-green font-bold">${opportunity.amount_needed}</span>
        <button className="btn-primary text-sm py-2">Review</button>
      </div>
    </div>
  )
}

function PerformanceMetric({ label, value, positive }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-dark-200">
      <span className="text-dark-600">{label}</span>
      <span className={`font-bold ${positive ? 'text-accent-green' : 'text-dark-900'}`}>
        {value}
      </span>
    </div>
  )
}

function InvestmentCard({ project }) {
  return (
    <div className="flex items-center justify-between p-4 bg-dark-200 rounded-lg">
      <div className="flex-1">
        <h3 className="font-medium text-dark-900">{project.title}</h3>
        <p className="text-sm text-dark-600">Investment: ${project.invested_amount}</p>
        <div className="mt-2">
          <div className="flex items-center gap-2">
            <div className="flex-1 h-2 bg-dark-300 rounded-full overflow-hidden">
              <div 
                className="h-full bg-primary-500"
                style={{ width: `${project.progress}%` }}
              />
            </div>
            <span className="text-xs text-dark-600">{project.progress}%</span>
          </div>
        </div>
      </div>
      <Link to={`/projects/${project.project_id}`} className="btn-ghost">
        View
      </Link>
    </div>
  )
}

function EmptyState() {
  return (
    <div className="text-center py-12">
      <DollarSign className="w-16 h-16 text-dark-400 mx-auto mb-4" />
      <p className="text-dark-600 mb-4">No active investments</p>
      <Link to="/opportunities" className="btn-primary">
        Explore Opportunities
      </Link>
    </div>
  )
}
