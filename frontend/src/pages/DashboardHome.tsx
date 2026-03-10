import { useEffect, useState, useCallback } from 'react'
import { useLocation } from 'react-router-dom'
import { analyticsApi } from '../services/api'

export default function DashboardHome() {
  const location = useLocation()
  const [summary, setSummary] = useState<{
    total_pickups_completed: number
    total_pickups_missed: number
    total_pickups_delayed: number
    total_pickups: number
    completion_rate: number
    active_route_count: number | null
  } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchSummary = useCallback(() => {
    setLoading(true)
    setError(null)
    analyticsApi
      .getSummary()
      .then((data) => {
        setSummary(data)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  // Refetch whenever user navigates to the dashboard so metrics stay up to date
  useEffect(() => {
    if (location.pathname === '/') {
      fetchSummary()
    }
  }, [location.pathname, fetchSummary])

  if (error) {
    return (
      <div className="rounded-lg bg-red-950/50 border border-red-800 p-4 text-red-400">
        Failed to load metrics: {error}. Ensure backend services are running.
      </div>
    )
  }

  if (!summary) {
    return <div className="text-zinc-500">Loading dashboard…</div>
  }

  const cards = [
    { label: 'Total pickups completed', value: summary.total_pickups_completed, color: 'bg-emerald-500' },
    { label: 'Total missed pickups', value: summary.total_pickups_missed, color: 'bg-amber-500' },
    { label: 'Completion rate', value: `${summary.completion_rate.toFixed(1)}%`, color: 'bg-blue-500' },
    { label: 'Active route count', value: summary.active_route_count ?? '—', color: 'bg-violet-500' },
  ]

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold text-zinc-100 tracking-wide">Dashboard</h2>
        <button
          type="button"
          onClick={fetchSummary}
          disabled={loading}
          className="px-4 py-2 bg-zinc-600 text-white rounded-lg font-medium hover:bg-zinc-500 disabled:opacity-50 text-sm font-normal"
        >
          {loading ? 'Updating…' : 'Refresh'}
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map(({ label, value, color }) => (
          <div key={label} className="rounded-xl border border-zinc-700 bg-zinc-900 shadow-lg overflow-hidden">
            <div className={`h-1 ${color}`} />
            <div className="p-4">
              <p className="text-sm text-zinc-500 uppercase tracking-wider">{label}</p>
              <p className="text-2xl font-bold text-zinc-100 mt-1">{value}</p>
            </div>
          </div>
        ))}
      </div>
      <p className="mt-6 text-zinc-500 text-sm">
        * Weekly schedules and daily routes can be generated on the Weekly Schedule and Daily Route pages respectively. The pickups can also be simulated in the Daily Routes page.
      </p>
      {summary.total_pickups === 0 && summary.active_route_count != null && (summary.active_route_count as number) > 0 && (
        <p className="mt-2 text-amber-400/90 text-sm">
          Routes exist but no pickup events yet. On <strong>Daily Routes</strong>, click <strong>Simulate pickups</strong> on each route. Ensure Planning and Operations services are both running, then click Refresh.
        </p>
      )}
    </div>
  )
}
