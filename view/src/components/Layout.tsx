import React, { ReactNode } from 'react';
import { texts } from '../../i18n/texts';

type ViewType = 'realtime' | 'accepted' | 'incidents-list';

interface LayoutProps {
  children: ReactNode;
  currentView: ViewType;
  onNavigate: (view: ViewType) => void;
}

interface NavButtonProps {
  label: string;
  isActive: boolean;
  onClick: () => void;
}

const NavButton: React.FC<NavButtonProps> = ({ label, isActive, onClick }) => (
  <button
    onClick={onClick}
    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
      isActive
        ? 'bg-primary text-white'
        : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
    }`}
  >
    {label}
  </button>
);

export const Layout: React.FC<LayoutProps> = ({ children, currentView, onNavigate }) => {
  return (
    <div className="min-h-screen bg-gray-100 [direction:rtl]">
      {/* Navigation Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo / Title */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">ي</span>
              </div>
              <h1 className="text-xl font-bold text-gray-900">
                {texts.navigation.alertsSystem}
              </h1>
            </div>

            {/* Navigation Buttons */}
            <nav className="flex items-center gap-2">
              <NavButton
                label={texts.navigation.incidents}
                isActive={currentView === 'incidents-list'}
                onClick={() => onNavigate('incidents-list')}
              />
              <NavButton
                label="مكالمة مباشرة"
                isActive={currentView === 'realtime'}
                onClick={() => onNavigate('realtime')}
              />
              <NavButton
                label="بلاغ مقبول"
                isActive={currentView === 'accepted'}
                onClick={() => onNavigate('accepted')}
              />
            </nav>

            {/* User Menu Placeholder */}
            <div className="flex items-center gap-3">
              <button className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                  />
                </svg>
              </button>
              <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main>{children}</main>
    </div>
  );
};

export default Layout;
