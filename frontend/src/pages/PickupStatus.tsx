import { useEffect, useState } from 'react'
import { operationsApi } from '../services/api'
import { planningApi } from '../services/api'

type Event = {
  id: number
  route_id: number
  house_id: number
  waste_type: string
  timestamp: string
  status: string
}

export default function PickupStatus() {
  const [events, setEvents] = useState<Event[]>([])
  const [routes, setRoutes] = useState<{ id: number; truck_id: string; date: string; neighbourhood_id: number; waste_type: string }[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filterRoute, setFilterRoute] = useState<number | ''>('')
  const [filterType, setFilterType] = useState<string>('')

  const load = () => {
    setLoading(true)
    Promise.all([
      operationsApi.getPickupEvents(undefined, 200),
      planningApi.getRoutes(),
    ])
      .then(([ev, r]) => {
        setEvents(ev)
        setRoutes(r)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [])

  let filtered = events
  if (filterRoute !== '') filtered = filtered.filter((e) => e.route_id === filterRoute)
  if (filterType) filtered = filtered.filter((e) => e.waste_type === filterType)

  const types = [...new Set(events.map((e) => e.waste_type))]

  if (error) {
    return (
      <div className="rounded-lg bg-red-950/50 border border-red-800 p-4 text-red-400">
        Error: {error}
      </div>
    )
  }

  const statusBadge = (status: string) => {
    const c =
      status === 'completed' ? 'bg-emerald-900/60 text-emerald-400 border border-emerald-700' :
      status === 'missed' ? 'bg-amber-900/60 text-amber-400 border border-amber-700' :
      'bg-zinc-700 text-zinc-400 border border-zinc-600'
    return <span className={`px-2 py-0.5 rounded text-xs font-medium ${c}`}>{status}</span>
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold text-zinc-100 tracking-wide">Pickup Status</h2>
        <button
          onClick={load}
          disabled={loading}
          className="px-4 py-2 bg-zinc-700 text-zinc-200 rounded-lg font-medium hover:bg-zinc-600 disabled:opacity-50 border border-zinc-600"
        >
          Refresh
        </button>
      </div>
      <div className="flex flex-wrap gap-4 mb-4">
        <select
          value={filterRoute}
          onChange={(e) => setFilterRoute(e.target.value === '' ? '' : Number(e.target.value))}
          className="rounded-lg border border-zinc-600 bg-zinc-800 px-3 py-2 text-sm text-zinc-100"
        >
          <option value="">All routes</option>
          {routes.map((r) => (
            <option key={r.id} value={r.id}>Route {r.id} ({r.waste_type})</option>
          ))}
        </select>
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="rounded-lg border border-zinc-600 bg-zinc-800 px-3 py-2 text-sm text-zinc-100"
        >
          <option value="">All waste types</option>
          {types.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </div>
      {loading ? (
        <p className="text-zinc-500">Loading…</p>
      ) : filtered.length === 0 ? (
        <p className="text-zinc-500">No pickup events. Simulate a route from Daily Routes to generate events.</p>
      ) : (
        <div className="rounded-xl border border-zinc-700 bg-zinc-900 shadow-lg overflow-hidden">
          <table className="min-w-full divide-y divide-zinc-700">
            <thead className="bg-zinc-800">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-zinc-400 uppercase tracking-wider">Time</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-zinc-400 uppercase tracking-wider">Route</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-zinc-400 uppercase tracking-wider">House</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-zinc-400 uppercase tracking-wider">Waste type</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-zinc-400 uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-700">
              {filtered.slice(0, 100).map((e) => (
                <tr key={e.id} className="hover:bg-zinc-800/50">
                  <td className="px-4 py-2 text-sm text-zinc-400">{new Date(e.timestamp).toLocaleString()}</td>
                  <td className="px-4 py-2 text-sm text-zinc-300">{e.route_id}</td>
                  <td className="px-4 py-2 text-sm text-zinc-300">{e.house_id}</td>
                  <td className="px-4 py-2 text-sm text-zinc-300">{e.waste_type}</td>
                  <td className="px-4 py-2">{statusBadge(e.status)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {filtered.length > 100 && (
            <p className="px-4 py-2 text-sm text-zinc-500 border-t border-zinc-700">Showing first 100 of {filtered.length}</p>
          )}
        </div>
      )}
    </div>
  )
}
