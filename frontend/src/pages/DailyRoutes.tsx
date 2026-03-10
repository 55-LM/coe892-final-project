import { useEffect, useState } from 'react'
import { planningApi, operationsApi } from '../services/api'

type Route = {
  id: number
  truck_id: string
  date: string
  neighbourhood_id: number
  waste_type: string
  stops: { house_id: number; address: string; order_index: number }[]
}

export default function DailyRoutes() {
  const [routes, setRoutes] = useState<Route[]>([])
  const [neighbourhoods, setNeighbourhoods] = useState<{ id: number; name: string }[]>([])
  const [routeDate, setRouteDate] = useState(() => new Date().toISOString().slice(0, 10))
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [generating, setGenerating] = useState(false)
  const [simulatingId, setSimulatingId] = useState<number | null>(null)

  const load = () => {
    setLoading(true)
    Promise.all([
      planningApi.getRoutes(routeDate),
      planningApi.getNeighbourhoods(),
    ])
      .then(([r, n]) => {
        setRoutes(r)
        setNeighbourhoods(n)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [routeDate])

  const handleGenerate = () => {
    setGenerating(true)
    planningApi
      .generateRoute(routeDate)
      .then(() => load())
      .catch((e) => setError(e.message))
      .finally(() => setGenerating(false))
  }

  const handleSimulate = (routeId: number) => {
    setSimulatingId(routeId)
    operationsApi
      .simulateRoute(routeId)
      .then(() => setError(null))
      .catch((e) => setError(e.message))
      .finally(() => setSimulatingId(null))
  }

  const nName = (id: number) => neighbourhoods.find((n) => n.id === id)?.name ?? `N${id}`

  if (error) {
    return (
      <div className="rounded-lg bg-red-950/50 border border-red-800 p-4 text-red-400">
        Error: {error}
      </div>
    )
  }

  return (
    <div>
      <div className="flex flex-wrap justify-between items-center gap-4 mb-6">
        <h2 className="text-2xl font-semibold text-zinc-100 tracking-wide">Daily Routes</h2>
        <div className="flex items-center gap-3">
          <label className="text-sm text-zinc-400">Date</label>
          <input
            type="date"
            value={routeDate}
            onChange={(e) => setRouteDate(e.target.value)}
            className="rounded-lg border border-zinc-600 bg-zinc-800 px-3 py-2 text-sm text-zinc-100"
          />
          <button
            onClick={handleGenerate}
            disabled={loading || generating}
            className="px-4 py-2 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-500 disabled:opacity-50"
          >
            {generating ? 'Generating…' : 'Generate routes'}
          </button>
        </div>
      </div>
      {loading ? (
        <p className="text-zinc-500">Loading…</p>
      ) : routes.length === 0 ? (
        <p className="text-zinc-500">No routes for this date. Select a weekday and click “Generate routes”.</p>
      ) : (
        <div className="space-y-6">
          {routes.map((route) => (
            <div key={route.id} className="rounded-xl border border-zinc-700 bg-zinc-900 shadow-lg overflow-hidden">
              <div className="px-4 py-3 bg-zinc-800 border-b border-zinc-700 flex flex-wrap gap-4 items-center">
                <span className="font-medium text-zinc-100">Route #{route.id}</span>
                <span className="text-zinc-400">Truck: {route.truck_id}</span>
                <span className="text-zinc-400">Neighbourhood: {nName(route.neighbourhood_id)}</span>
                <span className="text-zinc-400">Waste: {route.waste_type}</span>
                <button
                  onClick={() => handleSimulate(route.id)}
                  disabled={simulatingId === route.id}
                  className="ml-auto px-3 py-1.5 bg-emerald-600 text-white text-sm rounded-lg hover:bg-emerald-500 disabled:opacity-50 font-normal"
                >
                  {simulatingId === route.id ? 'Simulating…' : 'Simulate pickups'}
                </button>
              </div>
              <ul className="divide-y divide-zinc-700 max-h-48 overflow-y-auto">
                {route.stops.map((stop, i) => (
                  <li key={stop.house_id} className="px-4 py-2 text-sm flex gap-2 text-zinc-300">
                    <span className="text-zinc-500 w-6">{i + 1}.</span>
                    <span>{stop.address}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
