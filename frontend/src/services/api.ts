/**
 * API client for the distributed backend services.
 * Planning (8000), Operations (8001), Analytics (8002).
 * In dev with Vite proxy: use /api/planning, /api/operations, /api/analytics.
 * In Docker: use same paths if frontend is served with nginx proxy, or full URLs via env.
 */

const planningBase = import.meta.env.VITE_PLANNING_API || '/api/planning'
const operationsBase = import.meta.env.VITE_OPERATIONS_API || '/api/operations'
const analyticsBase = import.meta.env.VITE_ANALYTICS_API || '/api/analytics'

async function get<T>(base: string, path: string): Promise<T> {
  const res = await fetch(`${base}${path}`)
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

async function post<T>(base: string, path: string, body?: object): Promise<T> {
  const res = await fetch(`${base}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const text = await res.text()
    try {
      const j = JSON.parse(text)
      const msg = typeof j.detail === 'string' ? j.detail : text
      throw new Error(msg)
    } catch (e) {
      if (e instanceof Error && e.name === 'Error' && e.message !== text) throw e
      throw new Error(text)
    }
  }
  return res.json()
}

// --- Planning Service ---
export const planningApi = {
  getNeighbourhoods: () => get<{ id: number; name: string }[]>(planningBase, '/neighbourhoods'),
  getHouses: (neighbourhoodId?: number) =>
    get<{ id: number; address: string; neighbourhood_id: number; estimated_residents: number; bin_types_supported: string[] }[]>(
      planningBase,
      neighbourhoodId != null ? `/houses?neighbourhood_id=${neighbourhoodId}` : '/houses'
    ),
  generateSchedule: (weekStart?: string) =>
    post<{ id: number; neighbourhood_id: number; waste_type: string; scheduled_day: number }[]>(
      planningBase,
      '/generate-schedule',
      weekStart ? { week_start: weekStart } : {}
    ),
  getSchedule: (weekStart?: string) =>
    get<{ id: number; neighbourhood_id: number; waste_type: string; scheduled_day: number }[]>(
      planningBase,
      weekStart ? `/schedule?week_start=${weekStart}` : '/schedule'
    ),
  generateRoute: (date: string, neighbourhoodId?: number, wasteType?: string) =>
    post<{ id: number; truck_id: string; date: string; neighbourhood_id: number; waste_type: string; stops: { house_id: number; address: string; order_index: number }[] }[]>(
      planningBase,
      '/generate-route',
      { date, neighbourhood_id: neighbourhoodId ?? null, waste_type: wasteType ? wasteType : null }
    ),
  getRoutes: (date?: string, neighbourhoodId?: number) => {
    const params = new URLSearchParams()
    if (date) params.set('date', date)
    if (neighbourhoodId != null) params.set('neighbourhood_id', String(neighbourhoodId))
    return get<{ id: number; truck_id: string; date: string; neighbourhood_id: number; waste_type: string; stops: { house_id: number; address: string; order_index: number }[] }[]>(
      planningBase,
      params.toString() ? `/routes?${params}` : '/routes'
    )
  },
  getRoute: (routeId: number) =>
    get<{ id: number; truck_id: string; date: string; neighbourhood_id: number; waste_type: string; stops: { house_id: number; address: string; order_index: number }[] }>(
      planningBase,
      `/routes/${routeId}`
    ),
}

// --- Operations Service ---
export const operationsApi = {
  simulateRoute: (routeId: number) =>
    post<{ route_id: number; events_created: number; completed: number; missed: number; delayed: number }>(
      operationsBase,
      `/simulate-route/${routeId}`
    ),
  getPickupEvents: (routeId?: number, limit?: number) => {
    const params = new URLSearchParams()
    if (routeId != null) params.set('route_id', String(routeId))
    if (limit != null) params.set('limit', String(limit))
    return get<{ id: number; route_id: number; house_id: number; waste_type: string; timestamp: string; status: string }[]>(
      operationsBase,
      params.toString() ? `/pickup-events?${params}` : '/pickup-events'
    )
  },
  getPickupEventsByRoute: (routeId: number) =>
    get<{ id: number; route_id: number; house_id: number; waste_type: string; timestamp: string; status: string }[]>(
      operationsBase,
      `/pickup-events/route/${routeId}`
    ),
}

// --- Analytics Service ---
export const analyticsApi = {
  getSummary: () =>
    get<{ total_pickups_completed: number; total_pickups_missed: number; total_pickups_delayed: number; total_pickups: number; completion_rate: number; active_route_count: number | null }>(
      analyticsBase,
      '/metrics/summary'
    ),
  getByNeighbourhood: () =>
    get<{ neighbourhood_id: number; neighbourhood_name: string; completed: number; missed: number; delayed: number; total: number; completion_rate: number }[]>(
      analyticsBase,
      '/metrics/by-neighbourhood'
    ),
  getByWasteType: () =>
    get<{ waste_type: string; completed: number; missed: number; delayed: number; total: number; completion_rate: number }[]>(
      analyticsBase,
      '/metrics/by-waste-type'
    ),
  getMissedPickups: (limit?: number) =>
    get<{ id: number; route_id: number; house_id: number; waste_type: string; timestamp: string; status: string }[]>(
      analyticsBase,
      limit != null ? `/metrics/missed-pickups?limit=${limit}` : '/metrics/missed-pickups'
    ),
}
