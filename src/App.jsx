import { Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Generate from './pages/Generate'
import History from './pages/History'
import Settings from './pages/Settings'
import ViewPlan from './pages/ViewPlan'
import TestCaseDashboard from './pages/TestCaseDashboard'
import TestGenerator from './pages/TestGenerator'

export default function App() {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="main-content">
        <Routes>
          <Route path="/"           element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard"  element={<Dashboard />} />
          <Route path="/generate"   element={<Generate />} />
          <Route path="/history"    element={<History />} />
          <Route path="/test-cases" element={<TestCaseDashboard />} />
          <Route path="/test-generator" element={<TestGenerator />} />
          <Route path="/plan/:id"   element={<ViewPlan />} />
          <Route path="/settings"   element={<Settings />} />
        </Routes>
      </main>
    </div>
  )
}
