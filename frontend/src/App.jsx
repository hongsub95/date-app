import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './shared/contexts/AuthContext'
import AppLayout from './shared/layouts/AppLayout'
import LoginPage from './features/auth/LoginPage'
import RegisterPage from './features/auth/RegisterPage'
import CalendarPage from './features/calendar/CalendarPage'
import ScheduleListPage from './features/schedules/ScheduleListPage'
import ScheduleDetailPage from './features/schedules/ScheduleDetailPage'
import ScheduleNewPage from './features/schedules/ScheduleNewPage'
import SettingsPage from './features/settings/SettingsPage'
import PrototypePage from './features/prototype/PrototypePage'

function PrivateRoute({ children }) {
  const { user } = useAuth()
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/prototype" element={<PrototypePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <AppLayout />
          </PrivateRoute>
        }
      >
        <Route index element={<Navigate to="/calendar" replace />} />
        <Route path="calendar" element={<CalendarPage />} />
        <Route path="schedules" element={<ScheduleListPage />} />
        <Route path="schedules/new" element={<ScheduleNewPage />} />
        <Route path="schedules/:id" element={<ScheduleDetailPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  )
}
