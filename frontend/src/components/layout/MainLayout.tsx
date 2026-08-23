import React, { useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { Menu, X, Bell, Sparkles } from 'lucide-react';
import { PRIMARY_NAV, getPageHeaders } from '@/utils/navigation';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const MainLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const { title, subtitle } = getPageHeaders(location.pathname);

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);

  return (
    <div className="min-h-screen font-sans text-slate-800 antialiased dark:text-gray-200 bg-transparent">
      {/* Desktop Sidebar */}
      <aside className="fixed inset-y-4 left-4 hidden w-72 glass-card lg:block z-50 overflow-hidden shadow-2xl">
        <div className="flex h-20 items-center border-b border-slate-100/50 px-6 dark:border-gray-700/50">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-purple-600 text-white shadow-lg shadow-primary/30">
            <Sparkles className="h-5 w-5 stroke-[1.8]" />
          </div>
          <div className="ml-3">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">HR Analytics</p>
            <h1 className="text-lg font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-600 dark:from-white dark:to-gray-400">Attrition Studio</h1>
          </div>
        </div>
        <nav className="space-y-2 px-4 py-6">
          {PRIMARY_NAV.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'flex items-center rounded-xl px-4 py-3 text-sm font-medium transition-all duration-300 hover:translate-x-1',
                  isActive
                    ? 'bg-gradient-to-r from-primary to-purple-600 text-white shadow-glow'
                    : 'text-slate-600 hover:bg-slate-100/50 hover:text-slate-900 dark:text-gray-300 dark:hover:bg-gray-700/50 dark:hover:text-white'
                )
              }
            >
              <item.icon className="mr-3 h-5 w-5 stroke-[1.8]" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 bg-slate-900/40 lg:hidden">
          <div className="absolute inset-y-0 left-0 w-72 bg-white shadow-xl dark:bg-gray-800">
            <div className="flex items-center justify-between border-b border-slate-100 px-5 py-5 dark:border-gray-700">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Menu</p>
                <p className="text-lg font-bold text-slate-900 dark:text-gray-200">Attrition Studio</p>
              </div>
              <button
                type="button"
                aria-label="Close navigation"
                onClick={toggleSidebar}
                className="rounded-lg border border-slate-200 p-2 text-slate-600 transition-all duration-200 hover:bg-slate-100 dark:border-gray-700 dark:text-gray-200 dark:hover:bg-gray-700"
              >
                <X className="h-5 w-5 stroke-[1.8]" />
              </button>
            </div>
            <nav className="space-y-2 px-4 py-6">
              {PRIMARY_NAV.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center rounded-xl px-4 py-3 text-sm font-medium transition-all duration-300 hover:translate-x-1',
                      isActive
                        ? 'bg-gradient-to-r from-primary to-purple-600 text-white shadow-glow'
                        : 'text-slate-600 hover:bg-slate-100/50 hover:text-slate-900 dark:text-gray-300 dark:hover:bg-gray-700/50 dark:hover:text-white'
                    )
                  }
                >
                  <item.icon className="mr-3 h-5 w-5 stroke-[1.8]" />
                  <span>{item.label}</span>
                </NavLink>
              ))}
            </nav>
          </div>
          <button
            type="button"
            aria-label="Close navigation overlay"
            className="absolute inset-0 -z-10"
            onClick={toggleSidebar}
          />
        </div>
      )}

      {/* Main Content Wrapper */}
      <div className="lg:pl-80">
        <header className="sticky top-0 z-30 glass border-b-0 m-4 rounded-2xl shadow-sm">
          <div className="flex items-center justify-between px-4 py-4 sm:px-6">
            <div className="flex items-center gap-3">
              <button
                type="button"
                aria-label="Open navigation"
                onClick={toggleSidebar}
                className="rounded-xl border border-slate-200 p-2 text-slate-600 transition-all duration-200 hover:bg-slate-100 lg:hidden dark:border-gray-700 dark:text-gray-200 dark:hover:bg-gray-700"
              >
                <Menu className="h-5 w-5 stroke-[1.8]" />
              </button>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">{title}</p>
                <h2 className="text-xl font-bold text-slate-900 sm:text-2xl dark:text-gray-200">{subtitle}</h2>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                type="button"
                aria-label="Notifications"
                className="rounded-xl border border-slate-200 bg-white p-2 text-slate-600 transition-all duration-200 hover:bg-slate-100 dark:border-gray-700 dark:text-gray-200 dark:hover:bg-gray-700"
              >
                <Bell className="h-5 w-5 stroke-[1.8]" />
              </button>
              <div
                aria-label="User avatar placeholder"
                className="flex h-11 w-11 items-center justify-center rounded-full bg-gradient-to-br from-primary to-purple-600 text-sm font-bold text-white shadow-lg shadow-primary/30 ring-2 ring-white dark:ring-gray-800"
              >
                HR
              </div>
            </div>
          </div>
        </header>

        <main className="px-4 py-6 pb-24 sm:px-6 lg:pb-8">
          <Outlet />
        </main>
      </div>

      {/* Mobile Bottom Nav */}
      <nav className="fixed inset-x-4 bottom-4 z-30 grid grid-cols-5 gap-2 rounded-2xl border border-slate-200 bg-white/95 p-2 shadow-xl backdrop-blur lg:hidden dark:bg-gray-800/95 dark:border-gray-700">
        {PRIMARY_NAV.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              cn(
                'flex flex-col items-center justify-center rounded-xl px-2 py-2 text-[11px] font-medium transition-all duration-200',
                isActive
                  ? 'bg-primary text-white'
                  : 'text-slate-500 dark:text-gray-200'
              )
            }
          >
            <item.icon className="h-5 w-5 stroke-[1.8]" />
            <span className="mt-1">{item.label.split(' ')[0]}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
};

export default MainLayout;
