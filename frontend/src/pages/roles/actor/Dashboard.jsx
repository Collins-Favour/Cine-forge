import { useQuery } from 'react-query'
import { motion } from 'framer-motion'
import { Briefcase, Calendar, Star, Clock, MapPin } from 'lucide-react'
import { Link } from 'react-router-dom'
import api from '@services/api'
import { useAuthStore } from '@store/authStore'

export default function ActorDashboard() {
  const { user } = useAuthStore()

  const { data: stats } = useQuery('actor-stats', async () => {
    const response = await api.get(`/users/${user.user_id}/dashboard`)
    return response.data
  })

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-display font-bold text-dark-900 mb-2">
          Actor Dashboard
        </h1>
        <p className="text-dark-600">Manage auditions, roles, and character studies</p>
      </div>

      {/* Stats Grid */}
      <div className="grid md:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={<Briefcase className="w-6 h-6" />}
          label="Total Projects"
          value={stats?.total_projects || 0}
          color="primary-500"
        />
        <StatCard
          icon={<Calendar className="w-6 h-6" />}
          label="Active Projects"
          value={stats?.active_projects || 0}
          color="accent-purple"
        />
        <StatCard
          icon={<Star className="w-6 h-6" />}
          label="Collaborations"
          value={stats?.collaborations || 0}
          color="accent-orange"
        />
        <StatCard
          icon={<Clock className="w-6 h-6" />}
          label="Storyboards"
          value={stats?.total_storyboards || 0}
          color="accent-pink"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <QuickActionCard
          title="Browse Roles"
          description="Find casting opportunities"
          icon={<Briefcase className="w-8 h-8" />}
          color="primary-500"
          link="/roles"
        />
        <QuickActionCard
          title="My Characters"
          description="View assigned characters"
          icon={<Star className="w-8 h-8" />}
          color="accent-purple"
          link="/characters"
        />
        <QuickActionCard
          title="Audition Schedule"
          description="Manage your schedule"
          icon={<Calendar className="w-8 h-8" />}
          color="accent-pink"
          link="/auditions"
        />
      </div>

      {/* Current Roles */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="card">
          <h2 className="text-xl font-bold text-dark-900 mb-4">Current Roles</h2>
          {stats?.current_roles?.length > 0 ? (
            <div className="space-y-4">
              {stats.current_roles.map((role) => (
                <RoleCard key={role.id} role={role} />
              ))}
            </div>
          ) : (
            <p className="text-dark-600 text-center py-8">No active roles</p>
          )}
        </div>

        <div className="card">
          <h2 className="text-xl font-bold text-dark-900 mb-4">Upcoming Auditions</h2>
          {stats?.auditions?.length > 0 ? (
            <div className="space-y-4">
              {stats.auditions.map((audition) => (
                <AuditionCard key={audition.id} audition={audition} />
              ))}
            </div>
          ) : (
            <p className="text-dark-600 text-center py-8">No upcoming auditions</p>
          )}
        </div>
      </div>

      {/* Character Studies */}
      <div className="card">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-dark-900">Character Studies</h2>
          <Link to="/characters" className="text-primary-600 hover:text-primary-700 font-medium">
            View All →
          </Link>
        </div>

        {stats?.character_studies?.length > 0 ? (
          <div className="grid md:grid-cols-3 gap-4">
            {stats.character_studies.map((character) => (
              <CharacterCard key={character.id} character={character} />
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

function RoleCard({ role }) {
  return (
    <div className="p-4 bg-dark-200 rounded-lg">
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="font-medium text-dark-900">{role.character_name}</h3>
          <p className="text-sm text-dark-600">{role.project_title}</p>
        </div>
        <span className="px-2 py-1 bg-primary-500 text-white text-xs rounded">Active</span>
      </div>
      <p className="text-sm text-dark-600 mb-2">{role.description}</p>
      <Link to={`/projects/${role.project_id}`} className="text-primary-600 text-sm hover:underline">
        View Details →
      </Link>
    </div>
  )
}

function AuditionCard({ audition }) {
  return (
    <div className="p-4 bg-dark-200 rounded-lg">
      <h3 className="font-medium text-dark-900 mb-2">{audition.role_name}</h3>
      <div className="flex items-center gap-2 text-sm text-dark-600 mb-1">
        <Calendar className="w-4 h-4" />
        <span>{new Date(audition.date).toLocaleDateString()}</span>
      </div>
      <div className="flex items-center gap-2 text-sm text-dark-600">
        <MapPin className="w-4 h-4" />
        <span>{audition.location}</span>
      </div>
    </div>
  )
}

function CharacterCard({ character }) {
  return (
    <div className="card p-4">
      <Star className="w-8 h-8 text-accent-orange mb-2" />
      <h3 className="font-medium text-dark-900 mb-1">{character.name}</h3>
      <p className="text-sm text-dark-600 mb-2">{character.description}</p>
      <Link to={`/characters/${character.id}`} className="text-primary-600 text-sm hover:underline">
        Study Character →
      </Link>
    </div>
  )
}

function EmptyState() {
  return (
    <div className="text-center py-12">
      <Star className="w-16 h-16 text-dark-400 mx-auto mb-4" />
      <p className="text-dark-600 mb-4">No character studies yet</p>
      <Link to="/roles" className="btn-primary">
        Browse Available Roles
      </Link>
    </div>
  )
}
