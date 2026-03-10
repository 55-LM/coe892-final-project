import { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'

interface LayoutProps {
  children: ReactNode
}

const navItems = [
  { to: '/', label: 'Dashboard' },
  { to: '/schedule', label: 'Weekly Schedule' },
  { to: '/routes', label: 'Daily Routes' },
  { to: '/pickups', label: 'Pickup Status' },
  { to: '/analytics', label: 'Analytics' },
]

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-zinc-950">
      <header className="font-header bg-zinc-900 border-b border-zinc-700 text-zinc-100 shadow-lg overflow-hidden">
        <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
          <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2 min-h-14 py-3">
            <div className="flex flex-col leading-tight min-w-0 max-w-full">
              <span className="font-title text-lg sm:text-xl md:text-2xl lg:text-3xl font-semibold tracking-wide truncate">POINTPICKUP/</span>
              <span className="text-[10px] sm:text-xs text-zinc-500 font-header mt-0.5 truncate">WASTE COLLECTION MANAGEMENT</span>
            </div>
            <nav className="flex flex-wrap items-center justify-end gap-1 min-w-0">
              {navItems.map(({ to, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  className={({ isActive }) =>
                    `px-2 py-1.5 sm:px-3 sm:py-2 rounded-md text-xs sm:text-sm font-medium transition-colors whitespace-nowrap ${
                      isActive ? 'bg-zinc-600 text-white' : 'text-zinc-400 hover:bg-zinc-700 hover:text-zinc-100'
                    }`
                  }
                >
                  {label}
                </NavLink>
              ))}
            </nav>
          </div>
        </div>
      </header>
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 font-extralight">
        {children}
      </main>
      <footer className="border-t border-zinc-800 py-2 text-center text-sm text-zinc-500 bg-zinc-900">
        COE892 Final Project - City Waste Collection System
      </footer>
    </div>
  )
}
