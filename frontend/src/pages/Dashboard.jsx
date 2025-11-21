import { useState } from 'react'
import { useQuery } from 'react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, Film, Clock, Users, TrendingUp, DollarSign, Video, Clapperboard, Settings, ArrowLeft } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import api from '@services/api'
import { useAuthStore } from '@store/authStore'
import ProfileSettings from '@components/ProfileSettings'

export default function Dashboard() {
  const { user } = useAuthStore()
  const navigate = useNavigate()
  const [showProfileSettings, setShowProfileSettings] = useState(false)

  const { data: stats } = useQuery('user-stats', async () => {
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
              Dashboard
            </h1>
            <p className="text-dark-600">Manage your projects, scripts, and collaborations</p>
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
          icon={<Film className="w-6 h-6" />}
          label="Total Projects"
          value={stats?.total_projects || 0}
          color="primary-500"
        />
        <StatCard
          icon={<Clock className="w-6 h-6" />}
          label="Active Projects"
          value={stats?.active_projects || 0}
          color="accent-purple"
        />
        <StatCard
          icon={<Users className="w-6 h-6" />}
          label="Collaborations"
          value={stats?.collaborations || 0}
          color="accent-pink"
        />
        <StatCard
          icon={<Clapperboard className="w-6 h-6" />}
          label="Storyboards"
          value={stats?.total_storyboards || 0}
          color="accent-green"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <QuickActionCard
          title="New Project"
          description="Start a new film project"
          icon={<Film className="w-8 h-8" />}
          color="primary-500"
          link="/projects/new"
        />
        <QuickActionCard
          title="My Projects"
          description="View and manage your projects"
          icon={<Video className="w-8 h-8" />}
          color="accent-purple"
          link="/projects"
        />
        <QuickActionCard
          title="Collaborations"
          description="Projects you're working on"
          icon={<Users className="w-8 h-8" />}
          color="accent-pink"
          link="/projects"
        />
      </div>

      {/* Recent Projects */}
      <div className="card">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-dark-900">Recent Projects</h2>
          <Link to="/projects" className="text-primary-600 hover:text-primary-700 font-medium">
            View All →
          </Link>
        </div>

        {stats?.recent_projects?.length > 0 ? (
          <div className="space-y-4">
            {stats.recent_projects.map((project) => (
              <ProjectCard key={project.project_id} project={project} />
            ))}
          </div>
        ) : (
          <EmptyState />
        )}
      </div>
    </div>
  )
}

// Stat Card Component
function StatCard({ icon, label, value, color }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <div className="flex items-center gap-4">
        <div className={`p-3 bg-${color}/10 text-${color} rounded-xl`}>
          {icon}
        </div>
        <div>
          <p className="text-sm text-dark-600">{label}</p>
          <p className="text-2xl font-bold text-dark-900">{value}</p>
        </div>
      </div>
    </motion.div>
  )
}

// Quick Action Card Component
function QuickActionCard({ title, description, icon, color, link }) {
  return (
    <Link to={link}>
      <motion.div
        whileHover={{ y: -4 }}
        className="card hover:shadow-lg transition-all cursor-pointer"
      >
        <div className={`w-16 h-16 bg-${color}/10 text-${color} rounded-2xl flex items-center justify-center mb-4`}>
          {icon}
        </div>
        <h3 className="text-lg font-bold text-dark-900 mb-2">{title}</h3>
        <p className="text-dark-600 text-sm">{description}</p>
      </motion.div>
    </Link>
  )
}

// Project Card Component
function ProjectCard({ project }) {
  const getStageColor = (stage) => {
    const colors = {
      'concept': 'bg-dark-200 text-dark-700',
      'pre-production': 'bg-primary-100 text-primary-700',
      'production': 'bg-accent-green/20 text-accent-green',
      'post-production': 'bg-accent-purple/20 text-accent-purple',
      'completed': 'bg-accent-pink/20 text-accent-pink'
    }
    return colors[stage] || colors.concept
  }

  return (
    <Link to={`/projects/${project.project_id}`}>
      <motion.div
        whileHover={{ x: 4 }}
        className="flex items-center justify-between p-4 rounded-xl border border-dark-200 hover:border-primary-300 hover:shadow-md transition-all"
      >
        <div className="flex items-center gap-4">
          {project.thumbnail_url ? (
            <img
              src={project.thumbnail_url}
              alt={project.title}
              className="w-16 h-16 rounded-lg object-cover"
            />
          ) : (
            <div className="w-16 h-16 rounded-lg bg-gradient-to-br from-primary-500 to-accent-purple flex items-center justify-center">
              <Film className="w-8 h-8 text-white" />
            </div>
          )}
          <div>
            <h3 className="font-semibold text-dark-900">{project.title}</h3>
            <p className="text-sm text-dark-600">{project.logline || 'No logline yet'}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStageColor(project.production_stage)}`}>
            {project.production_stage?.replace('-', ' ') || 'Concept'}
          </span>
          <span className="text-sm text-dark-500">
            {new Date(project.updated_at).toLocaleDateString()}
          </span>
        </div>
      </motion.div>
    </Link>
  )
}

// Empty State Component
function EmptyState() {
  return (
    <div className="text-center py-12">
      <div className="w-24 h-24 bg-dark-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <Film className="w-12 h-12 text-dark-400" />
      </div>
      <h3 className="text-lg font-semibold text-dark-900 mb-2">No projects yet</h3>
      <p className="text-dark-600 mb-6">Create your first project to get started</p>
      <Link to="/projects/new" className="btn-primary inline-flex items-center gap-2">
        <Plus className="w-5 h-5" />
        Create Project
      </Link>
    </div>
  )
}
