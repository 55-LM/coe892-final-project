import { Routes, Route, NavLink } from 'react-router-dom'
import Layout from './components/Layout'
import DashboardHome from './pages/DashboardHome'
import WeeklySchedule from './pages/WeeklySchedule'
import DailyRoutes from './pages/DailyRoutes'
import PickupStatus from './pages/PickupStatus'
import Analytics from './pages/Analytics'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<DashboardHome />} />
        <Route path="/schedule" element={<WeeklySchedule />} />
        <Route path="/routes" element={<DailyRoutes />} />
        <Route path="/pickups" element={<PickupStatus />} />
        <Route path="/analytics" element={<Analytics />} />
      </Routes>
    </Layout>
  )
}

export default App
