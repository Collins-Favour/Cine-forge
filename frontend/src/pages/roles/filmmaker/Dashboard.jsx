import { useState } from 'react'
import { useQuery } from 'react-query'
import { motion } from 'framer-motion'
import { Plus, Film, Clock, Users, TrendingUp, DollarSign } from 'lucide-react'
import { Link } from 'react-router-dom'
import api from '@services/api'
import { useAuthStore } from '@store/authStore'

export default function FilmmakerDashboard() {
  const { user } = useAuthStore()

  const { data: stats } = useQuery('filmmaker-stats', async () => {
    const response = await api.get(`/users/${user.user_id}/dashboard`)
    return response.data
  })

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-display font-bold text-dark-900 mb-2">
          Filmmaker Dashboard
        </h1>
        <p className="text-dark-600">Manage your projects, scripts, and storyboards</p>
      </div>

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
          label="Collaborators"
          value={stats?.collaborations || 0}
          color="accent-pink"
        />
        <StatCard
          icon={<TrendingUp className="w-6 h-6" />}
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
          title="Script Editor"
          description="Write and edit your screenplay"
          icon={<Film className="w-8 h-8" />}
          color="accent-purple"
          link="/script-editor"
        />
        <QuickActionCard
          title="Storyboard"
          description="Create visual storyboards"
          icon={<Film className="w-8 h-8" />}
          color="accent-pink"
          link="/storyboard"
        />
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

function ProjectCard({ project }) {
  return (
    <div className="flex items-center justify-between p-4 bg-dark-200 rounded-lg hover:bg-dark-300 transition-colors">
      <div className="flex-1">
        <h3 className="font-medium text-dark-900">{project.title}</h3>
        <p className="text-sm text-dark-600">{project.description}</p>
        <div className="flex gap-4 mt-2 text-xs text-dark-500">
          <span>Updated {new Date(project.updated_at).toLocaleDateString()}</span>
          <span>{project.status}</span>
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
      <Film className="w-16 h-16 text-dark-400 mx-auto mb-4" />
      <p className="text-dark-600 mb-4">No projects yet. Start your creative journey!</p>
      <Link to="/projects/new" className="btn-primary">
        Create Your First Project
      </Link>
    </div>
  )
}
