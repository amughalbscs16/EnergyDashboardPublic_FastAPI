import React from 'react';
import { Button } from '@tremor/react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';

export default function Navigation() {
  const pathname = usePathname();

  const navItems = [
    { href: '/', label: '📊 DR Planning', color: 'blue' },
    { href: '/agents', label: '🤖 AI Agents', color: 'purple' },
    { href: '/realtime', label: '⚡ Real-Time', color: 'yellow' },
    { href: '/analytics', label: '📈 Analytics', color: 'green' },
    { href: '/market', label: '💰 Market', color: 'indigo' },
    { href: '/topology', label: '🗺️ Grid Map', color: 'cyan' },
    { href: '/verification', label: '✅ Verification', color: 'emerald' },
    { href: '/history', label: '📜 History', color: 'orange' },
  ];

  return (
    <div className="mb-8 bg-white p-4 rounded-lg shadow">
      <div className="mb-2">
        <h2 className="text-sm font-semibold text-gray-600 uppercase tracking-wider">Navigation</h2>
      </div>
      <div className="flex flex-wrap gap-3">
        {navItems.map((item) => (
          <Link key={item.href} href={item.href}>
            <Button
              className={`transition-all ${
                pathname === item.href
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-800 hover:bg-gray-200 hover:shadow'
              }`}
            >
              {item.label}
            </Button>
          </Link>
        ))}
      </div>
      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <p className="text-xs text-gray-600">
          <strong>Quick Links:</strong> Click any button above to navigate between different system modules.
          Each module provides specialized functionality for grid operations.
        </p>
      </div>
    </div>
  );
}