import React from 'react';

interface BottomNavProps {
  currentTab: string;
  onNavigate: (tab: string) => void;
}

export const BottomNav: React.FC<BottomNavProps> = ({ currentTab, onNavigate }) => {
  const tabs = [
    { id: 'home', label: 'Trang chủ', icon: 'home_max' },
    { id: 'diagnose', label: 'Chẩn đoán', icon: 'add_a_photo' },
    { id: 'diseases', label: 'Thư viện', icon: 'database' },
    { id: 'history', label: 'Lịch sử', icon: 'history' },
    { id: 'care', label: 'Chăm sóc', icon: 'potted_plant' },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 w-full z-50 flex justify-around items-center py-2 px-3 bg-surface-container/90 backdrop-blur-xl border-t border-outline-variant shadow-2xl">
      {tabs.map((tab) => {
        const isActive = currentTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onNavigate(tab.id)}
            className={`flex flex-col items-center justify-center py-1 px-2 rounded-xl transition-all ${
              isActive ? 'text-primary-container font-bold scale-105' : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            <span className="material-symbols-outlined text-xl">
              {tab.icon}
            </span>
            <span className="text-[10px] mt-0.5 tracking-tight">{tab.label}</span>
          </button>
        );
      })}
    </nav>
  );
};
