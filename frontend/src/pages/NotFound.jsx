import { Link } from 'react-router-dom'
import { Film, Home } from 'lucide-react'
import { motion } from 'framer-motion'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-dark-50 flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center"
      >
        <Film className="w-20 h-20 text-primary-500 mx-auto mb-6" />
        <h1 className="text-6xl font-display font-bold gradient-text mb-4">404</h1>
        <h2 className="text-2xl font-bold text-dark-900 mb-2">Page Not Found</h2>
        <p className="text-dark-600 mb-8">The page you're looking for doesn't exist.</p>
        <Link to="/" className="btn-primary inline-flex items-center gap-2">
          <Home className="w-5 h-5" />
          Back to Home
        </Link>
      </motion.div>
    </div>
  )
}
