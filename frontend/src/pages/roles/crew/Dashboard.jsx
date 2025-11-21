import { useQuery } from 'react-query'
import { motion } from 'framer-motion'
import { Wrench, Calendar, CheckCircle, AlertCircle, Users, Clock } from 'lucide-react'
import { Link } from 'react-router-dom'
import api from '@services/api'
import { useAuthStore } from '@store/authStore'

export default function CrewDashboard() {
  const { user } = useAuthStore()

  const { data: stats } = useQuery('crew-stats', async () => {
    const response = await api.get(`/users/${user.user_id}/dashboard`)
    return response.data
  })

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-display font-bold text-dark-900 mb-2">
          Crew Dashboard
        </h1>
        <p className="text-dark-600">Manage tasks, assignments, and production schedules</p>
      </div>

      {/* Stats Grid */}
      <div className="grid md:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={<Wrench className="w-6 h-6" />}
          label="Total Projects"
          value={stats?.total_projects || 0}
          color="primary-500"
        />
        <StatCard
          icon={<CheckCircle className="w-6 h-6" />}
          label="Active Projects"
          value={stats?.active_projects || 0}
          color="accent-green"
        />
        <StatCard
          icon={<Clock className="w-6 h-6" />}
          label="Collaborations"
          value={stats?.collaborations || 0}
          color="accent-orange"
        />
        <StatCard
          icon={<Users className="w-6 h-6" />}
          label="Storyboards"
          value={stats?.total_storyboards || 0}
          color="accent-purple"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <QuickActionCard
          title="Task Board"
          description="View and manage tasks"
          icon={<CheckCircle className="w-8 h-8" />}
          color="primary-500"
          link="/tasks"
        />
        <QuickActionCard
          title="Schedule"
          description="Production schedule"
          icon={<Calendar className="w-8 h-8" />}
          color="accent-purple"
          link="/schedule"
        />
        <QuickActionCard
          title="Equipment"
          description="Manage equipment"
          icon={<Wrench className="w-8 h-8" />}
          color="accent-pink"
          link="/equipment"
        />
      </div>

      {/* Task Overview */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="card">
          <h2 className="text-xl font-bold text-dark-900 mb-4">Today's Tasks</h2>
          {stats?.today_tasks?.length > 0 ? (
            <div className="space-y-3">
              {stats.today_tasks.map((task) => (
                <TaskCard key={task.id} task={task} />
              ))}
            </div>
          ) : (
            <p className="text-dark-600 text-center py-8">No tasks for today</p>
          )}
        </div>

        <div className="card">
          <h2 className="text-xl font-bold text-dark-900 mb-4">Upcoming Deadlines</h2>
          {stats?.deadlines?.length > 0 ? (
            <div className="space-y-3">
              {stats.deadlines.map((deadline) => (
                <DeadlineCard key={deadline.id} deadline={deadline} />
              ))}
            </div>
          ) : (
            <p className="text-dark-600 text-center py-8">No upcoming deadlines</p>
          )}
        </div>
      </div>

      {/* Active Projects */}
      <div className="card">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-dark-900">Active Projects</h2>
          <Link to="/projects" className="text-primary-600 hover:text-primary-700 font-medium">
            View All →
          </Link>
        </div>

        {stats?.projects?.length > 0 ? (
          <div className="space-y-4">
            {stats.projects.map((project) => (
              <ProjectCard key={project.id} project={project} />
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

function TaskCard({ task }) {
  const priorityColors = {
    high: 'bg-red-500',
    medium: 'bg-accent-orange',
    low: 'bg-accent-green'
  }

  return (
    <div className="flex items-center gap-3 p-3 bg-dark-200 rounded-lg">
      <input type="checkbox" className="w-5 h-5 rounded border-dark-300" />
      <div className="flex-1">
        <h3 className="font-medium text-dark-900 text-sm">{task.title}</h3>
        <p className="text-xs text-dark-600">{task.project_name}</p>
      </div>
      <span className={`px-2 py-1 ${priorityColors[task.priority]} text-white text-xs rounded`}>
        {task.priority}
      </span>
    </div>
  )
}

function DeadlineCard({ deadline }) {
  const daysLeft = Math.ceil((new Date(deadline.date) - new Date()) / (1000 * 60 * 60 * 24))
  const isUrgent = daysLeft <= 3

  return (
    <div className="p-3 bg-dark-200 rounded-lg">
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-medium text-dark-900 text-sm">{deadline.title}</h3>
        <span className={`text-xs font-bold ${isUrgent ? 'text-red-500' : 'text-dark-600'}`}>
          {daysLeft}d left
        </span>
      </div>
      <p className="text-xs text-dark-600">{deadline.project_name}</p>
      <div className="mt-2 flex items-center gap-2 text-xs text-dark-600">
        <Calendar className="w-3 h-3" />
        <span>{new Date(deadline.date).toLocaleDateString()}</span>
      </div>
    </div>
  )
}

function ProjectCard({ project }) {
  return (
    <div className="flex items-center justify-between p-4 bg-dark-200 rounded-lg">
      <div className="flex-1">
        <h3 className="font-medium text-dark-900">{project.title}</h3>
        <p className="text-sm text-dark-600 mb-2">Role: {project.role}</p>
        <div className="flex items-center gap-2">
          <div className="flex-1 h-2 bg-dark-300 rounded-full overflow-hidden max-w-xs">
            <div 
              className="h-full bg-primary-500"
              style={{ width: `${project.progress}%` }}
            />
          </div>
          <span className="text-xs text-dark-600">{project.progress}%</span>
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
      <Wrench className="w-16 h-16 text-dark-400 mx-auto mb-4" />
      <p className="text-dark-600 mb-4">No active projects</p>
      <Link to="/projects" className="btn-primary">
        Browse Projects
      </Link>
    </div>
  )
}
