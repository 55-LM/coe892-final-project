import { useEffect, useState } from 'react'
import { planningApi } from '../services/api'

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

export default function WeeklySchedule() {
  const [schedule, setSchedule] = useState<{ id: number; neighbourhood_id: number; waste_type: string; scheduled_day: number }[]>([])
  const [neighbourhoods, setNeighbourhoods] = useState<{ id: number; name: string }[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [generating, setGenerating] = useState(false)

  const load = () => {
    setLoading(true)
    Promise.all([planningApi.getSchedule(), planningApi.getNeighbourhoods()])
      .then(([s, n]) => {
        setSchedule(s)
        setNeighbourhoods(n)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [])

  const handleGenerate = () => {
    setGenerating(true)
    planningApi
      .generateSchedule()
      .then(() => load())
      .catch((e) => setError(e.message))
      .finally(() => setGenerating(false))
  }

  if (error) {
    return (
      <div className="rounded-lg bg-red-950/50 border border-red-800 p-4 text-red-400">
        Error: {error}
      </div>
    )
  }

  const byKey = (s: { neighbourhood_id: number; waste_type: string; scheduled_day: number }) =>
    `${s.neighbourhood_id}-${s.waste_type}-${s.scheduled_day}`
  const rows = schedule.length
    ? schedule.map((s) => ({
        neighbourhood: neighbourhoods.find((n) => n.id === s.neighbourhood_id)?.name ?? `N${s.neighbourhood_id}`,
        waste_type: s.waste_type,
        assigned_day: DAYS[s.scheduled_day] ?? `Day ${s.scheduled_day}`,
      }))
    : []

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold text-zinc-100 tracking-wide">Weekly Schedule</h2>
        <button
          onClick={handleGenerate}
          disabled={loading || generating}
          className="px-4 py-2 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-500 disabled:opacity-50"
        >
          {generating ? 'Generating…' : 'Generate schedule'}
        </button>
      </div>
      {loading ? (
        <p className="text-zinc-500">Loading…</p>
      ) : rows.length === 0 ? (
        <p className="text-zinc-500">No schedule. Click “Generate schedule” to create one.</p>
      ) : (
        <div className="rounded-xl border border-zinc-700 bg-zinc-900 shadow-lg overflow-hidden">
          <table className="min-w-full divide-y divide-zinc-700">
            <thead className="bg-zinc-800">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-zinc-400 uppercase tracking-wider">Neighbourhood</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-zinc-400 uppercase tracking-wider">Waste type</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-zinc-400 uppercase tracking-wider">Assigned day</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-700">
              {rows.map((row, i) => (
                <tr key={i} className="hover:bg-zinc-800/80">
                  <td className="px-4 py-3 text-sm text-zinc-200">{row.neighbourhood}</td>
                  <td className="px-4 py-3 text-sm text-zinc-300">{row.waste_type}</td>
                  <td className="px-4 py-3 text-sm text-zinc-300">{row.assigned_day}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
