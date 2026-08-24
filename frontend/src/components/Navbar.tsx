import React from 'react';

interface NavbarProps {
  currentTab: string;
  onNavigate: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, onNavigate }) => {
  const navItems = [
    { id: 'home', label: 'Trang chủ' },
    { id: 'diagnose', label: 'Chẩn đoán' },
    { id: 'diseases', label: 'Thư viện' },
    { id: 'history', label: 'Lịch sử' },
    { id: 'care', label: 'Chăm sóc' },
    { id: 'about', label: 'Về chúng tôi' },
  ];

  return (
    <header className="sticky top-4 mx-4 md:mx-8 z-50 glass-panel rounded-full px-6 py-3 flex justify-between items-center border border-white/10 shadow-2xl">
      <div 
        className="flex items-center gap-2 cursor-pointer group"
        onClick={() => onNavigate('home')}
      >
        <span className="material-symbols-outlined text-primary-container text-2xl group-hover:rotate-12 transition-transform">
          psychology_alt
        </span>
        <span className="font-extrabold text-xl tracking-tighter text-primary-container">
          LEAF_AI
        </span>
      </div>

      <nav className="hidden md:flex items-center gap-8">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onNavigate(item.id)}
            className={`font-medium text-sm transition-colors relative py-1 ${
              currentTab === item.id 
                ? 'text-primary-container font-semibold' 
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            {item.label}
            {currentTab === item.id && (
              <span className="absolute bottom-0 left-0 w-full h-0.5 bg-primary-container rounded-full" />
            )}
          </button>
        ))}
      </nav>

      <button
        onClick={() => onNavigate('diagnose')}
        className="bg-primary-container text-on-primary font-semibold text-xs px-5 py-2.5 rounded-full hover:opacity-90 active:scale-95 transition-all shadow-[0_0_15px_rgba(25,211,174,0.3)] flex items-center gap-1.5"
      >
        <span className="material-symbols-outlined text-base">add_a_photo</span>
        Chẩn đoán ngay
      </button>
    </header>
  );
};
