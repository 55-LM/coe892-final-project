import { useEffect, useState } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'
import { analyticsApi } from '../services/api'

const CHART_COLORS = ['#71717a', '#f59e0b', '#6366f1', '#ec4899', '#94a3b8']

export default function Analytics() {
  const [byNeighbourhood, setByNeighbourhood] = useState<{ neighbourhood_name: string; completed: number; missed: number; total: number; completion_rate: number }[]>([])
  const [byWasteType, setByWasteType] = useState<{ waste_type: string; completed: number; missed: number; total: number; completion_rate: number }[]>([])
  const [summary, setSummary] = useState<{ total_pickups: number; completion_rate: number } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([
      analyticsApi.getByNeighbourhood(),
      analyticsApi.getByWasteType(),
      analyticsApi.getSummary(),
    ])
      .then(([n, w, s]) => {
        setByNeighbourhood(n)
        setByWasteType(w)
        setSummary(s)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (error) {
    return (
      <div className="rounded-lg bg-red-950/50 border border-red-800 p-4 text-red-400">
        Error: {error}
      </div>
    )
  }

  if (loading || !summary) {
    return <p className="text-zinc-500">Loading analytics…</p>
  }

  const pieData = byWasteType.map((r, i) => ({
    name: r.waste_type,
    value: r.total,
    color: CHART_COLORS[i % CHART_COLORS.length],
  }))

  return (
    <div>
      <h2 className="text-2xl font-semibold text-zinc-100 mb-6 tracking-wide">Analytics</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="rounded-xl border border-zinc-700 bg-zinc-900 p-4 shadow-lg">
          <h3 className="font-medium text-zinc-100 mb-4 uppercase tracking-wider">Pickups by waste type</h3>
          {pieData.length === 0 ? (
            <p className="text-zinc-500 text-sm">No data yet. Simulate routes to see metrics.</p>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={2}
                  dataKey="value"
                  nameKey="name"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={pieData[i].color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#27272a', border: '1px solid #52525b', borderRadius: '6px' }} labelStyle={{ color: '#e4e4e7' }} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="rounded-xl border border-zinc-700 bg-zinc-900 p-4 shadow-lg">
          <h3 className="font-medium text-zinc-100 mb-4 uppercase tracking-wider">Pickups by neighbourhood</h3>
          {byNeighbourhood.length === 0 ? (
            <p className="text-zinc-500 text-sm">No data yet.</p>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={byNeighbourhood} margin={{ top: 10, right: 10, left: 0, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#52525b" />
                <XAxis dataKey="neighbourhood_name" angle={-25} textAnchor="end" height={60} tick={{ fontSize: 11, fill: '#a1a1aa' }} />
                <YAxis tick={{ fontSize: 11, fill: '#a1a1aa' }} />
                <Tooltip contentStyle={{ backgroundColor: '#27272a', border: '1px solid #52525b', borderRadius: '6px' }} />
                <Legend wrapperStyle={{ color: '#e4e4e7' }} />
                <Bar dataKey="completed" name="Completed" fill="#71717a" radius={[2, 2, 0, 0]} />
                <Bar dataKey="missed" name="Missed" fill="#f59e0b" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="rounded-xl border border-zinc-700 bg-zinc-900 p-4 shadow-lg">
        <h3 className="font-medium text-zinc-100 mb-4 uppercase tracking-wider">Completion rate by waste type</h3>
        {byWasteType.length === 0 ? (
          <p className="text-zinc-500 text-sm">No data yet.</p>
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={byWasteType} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#52525b" />
              <XAxis dataKey="waste_type" tick={{ fontSize: 12, fill: '#a1a1aa' }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#a1a1aa' }} tickFormatter={(v) => `${v}%`} />
              <Tooltip contentStyle={{ backgroundColor: '#27272a', border: '1px solid #52525b', borderRadius: '6px' }} formatter={(v: number) => [`${v.toFixed(1)}%`, 'Completion rate']} />
              <Bar dataKey="completion_rate" name="Completion rate (%)" fill="#71717a" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="mt-6 p-4 rounded-lg bg-zinc-900 border border-zinc-700">
        <p className="text-sm text-zinc-400">
          Total pickups: <strong className="text-zinc-100">{summary.total_pickups}</strong> · Overall completion rate: <strong className="text-zinc-100">{summary.completion_rate.toFixed(1)}%</strong>
        </p>
      </div>
    </div>
  )
}
