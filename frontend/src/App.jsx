import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@store/authStore'

// Pages
import LandingPage from '@pages/Landing'
import Login from '@pages/auth/Login'
import Register from '@pages/auth/Register'
import Dashboard from '@pages/Dashboard'
import Projects from '@pages/Projects'
import NewProject from '@pages/NewProject'
import ProjectDetails from '@pages/ProjectDetails'
import ProjectEdit from '@pages/ProjectEdit'
import ProjectSettings from '@pages/ProjectSettings'
import ScriptEditor from '@pages/ScriptEditor'
import Storyboard from '@pages/Storyboard'
import CSpace from '@pages/CSpace'
import Settings from '@pages/Settings'
import NotFound from '@pages/NotFound'

// Role-based Dashboards
import InvestorDashboard from '@pages/roles/investor/Dashboard'
import AdminDashboard from '@pages/roles/admin/Dashboard'
import UserManagement from '@pages/roles/admin/UserManagement'
import UserDetail from '@pages/roles/admin/UserDetail'
import SystemSettings from '@pages/roles/admin/SystemSettings'
import Analytics from '@pages/roles/admin/Analytics'
import SecurityLogs from '@pages/roles/admin/SecurityLogs'
import ProjectManagement from '@pages/roles/admin/ProjectManagement'

// Layout
import MainLayout from '@components/layout/MainLayout'
import AuthLayout from '@components/layout/AuthLayout'

function App() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<LandingPage />} />
      
      {/* Auth Routes */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Route>

      {/* Protected Routes */}
      <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
        <Route path="/dashboard" element={<RoleDashboard />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/projects/new" element={<NewProject />} />
        <Route path="/projects/:id" element={<ProjectDetails />} />
        <Route path="/projects/:id/edit" element={<ProjectEdit />} />
        <Route path="/projects/:id/script" element={<ScriptEditor />} />
        <Route path="/projects/:id/settings" element={<ProjectSettings />} />
        <Route path="/script-editor" element={<Navigate to="/projects" replace />} />
        <Route path="/projects/:id/storyboard" element={<Storyboard />} />
        <Route path="/storyboard" element={<Navigate to="/projects" replace />} />
        <Route path="/c-space" element={<CSpace />} />
        <Route path="/projects/:id/c-space" element={<CSpace />} />
        <Route path="/settings" element={<Settings />} />
        
        {/* Admin Routes */}
        <Route path="/admin/users" element={<AdminRoute><UserManagement /></AdminRoute>} />
        <Route path="/admin/users/:userId" element={<AdminRoute><UserDetail /></AdminRoute>} />
        <Route path="/admin/projects" element={<AdminRoute><ProjectManagement /></AdminRoute>} />
        <Route path="/admin/settings" element={<AdminRoute><SystemSettings /></AdminRoute>} />
        <Route path="/admin/analytics" element={<AdminRoute><Analytics /></AdminRoute>} />
        <Route path="/admin/security" element={<AdminRoute><SecurityLogs /></AdminRoute>} />
      </Route>

      {/* 404 */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}

// Protected Route Component
function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuthStore()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return children
}

// Admin Route Component
function AdminRoute({ children }) {
  const { user } = useAuthStore()
  
  if (user?.role !== 'admin') {
    return <Navigate to="/dashboard" replace />
  }
  
  return children
}

// Role-based Dashboard Component
function RoleDashboard() {
  const { user } = useAuthStore()
  
  // Only admin and investor get special dashboards
  if (user?.role === 'admin') {
    return <AdminDashboard />
  }
  
  if (user?.role === 'investor') {
    return <InvestorDashboard />
  }
  
  // All other roles use the unified dashboard
  return <Dashboard />
}

export default App
