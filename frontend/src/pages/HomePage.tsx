import React from 'react';
import { ThreeLeaf } from '../components/ThreeLeaf';

interface HomePageProps {
  onNavigate: (tab: string) => void;
}

export const HomePage: React.FC<HomePageProps> = ({ onNavigate }) => {
  return (
    <div className="flex flex-col gap-16 pb-24 md:pb-12 max-w-6xl mx-auto px-4 md:px-8 mt-6">
      {/* Hero Section */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center pt-4">
        <div className="flex flex-col items-start gap-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-primary-container/10 border border-primary-container/20">
            <span className="w-2.5 h-2.5 rounded-full bg-primary-container animate-pulse" />
            <span className="text-xs font-semibold text-primary-container uppercase tracking-wider">
              SỨC KHỎE CÂY TRỒNG CÔNG NGHỆ AI
            </span>
          </div>

          <h1 className="text-3xl md:text-5xl font-extrabold text-on-surface leading-tight">
            Phát hiện <span className="text-primary-container">Bệnh cây trồng.</span><br />
            Nâng cao chất lượng đầu ra.
          </h1>

          <p className="text-body-lg text-on-surface-variant max-w-lg leading-relaxed">
            Tải lên hình ảnh độ phân giải cao của lá cây có triệu chứng. Lớp trí tuệ nhân tạo của chúng tôi sẽ chẩn đoán các tác nhân gây bệnh với độ chính xác hàng đầu.
          </p>

          <div className="flex flex-col sm:flex-row w-full sm:w-auto gap-4 mt-2">
            <button
              onClick={() => onNavigate('diagnose')}
              className="bg-primary-container text-on-primary font-bold text-sm py-4 px-8 rounded-xl flex items-center justify-center gap-2 hover:opacity-90 active:scale-95 transition-all shadow-[0_0_20px_rgba(25,211,174,0.3)]"
            >
              <span className="material-symbols-outlined">add_a_photo</span>
              Chẩn đoán lá ngay
            </button>
            <button
              onClick={() => onNavigate('diseases')}
              className="border border-primary-container/50 text-primary-container font-semibold text-sm py-4 px-8 rounded-xl flex items-center justify-center gap-2 hover:bg-primary-container/10 active:scale-95 transition-all"
            >
              Khám phá thư viện bệnh
            </button>
          </div>
        </div>

        {/* Hero Visual Card / 3D Canvas */}
        <div className="relative glass-panel rounded-2xl p-6 border border-white/10 overflow-hidden flex flex-col justify-between min-h-[380px]">
          <div className="absolute inset-0 pointer-events-none opacity-80">
            <ThreeLeaf />
          </div>
          
          <div className="relative z-10 flex justify-between items-start">
            <div className="glass-panel px-3 py-1.5 rounded-full border border-primary-container/30 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-primary-container animate-ping" />
              <span className="text-xs text-primary-container font-medium">Mô phỏng 3D Nơ-ron AI</span>
            </div>
          </div>

          <div className="relative z-10 flex flex-col gap-3 mt-auto">
            <div className="glass-panel p-4 rounded-xl flex justify-between items-center">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-primary-container/20 flex items-center justify-center border border-primary-container/30">
                  <span className="material-symbols-outlined text-primary-container">psychology</span>
                </div>
                <div>
                  <p className="text-xs text-on-surface-variant">Trí tuệ nhân tạo</p>
                  <p className="text-sm font-semibold text-on-surface">Chẩn đoán cấp tế bào</p>
                </div>
              </div>
              <span className="material-symbols-outlined text-primary-container">check_circle</span>
            </div>

            <div className="glass-panel p-4 rounded-xl flex justify-between items-center border-t border-primary-container">
              <p className="text-xs text-on-surface-variant">Độ tin cậy mô hình</p>
              <p className="text-xl font-bold text-primary-container">98.4%</p>
            </div>
          </div>
        </div>
      </section>

      {/* Statistics Section */}
      <section className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div className="bg-surface-container p-6 rounded-2xl border border-white/5 flex flex-col gap-2">
          <span className="material-symbols-outlined text-primary-container text-3xl">coronavirus</span>
          <h3 className="text-3xl font-extrabold text-on-surface">50+</h3>
          <p className="text-xs text-on-surface-variant">Bệnh cây trồng được hỗ trợ</p>
        </div>
        <div className="bg-surface-container p-6 rounded-2xl border border-white/5 flex flex-col gap-2">
          <span className="material-symbols-outlined text-primary-container text-3xl">forest</span>
          <h3 className="text-3xl font-extrabold text-on-surface">10+</h3>
          <p className="text-xs text-on-surface-variant">Loài cây nông nghiệp chính</p>
        </div>
        <div className="bg-surface-container p-6 rounded-2xl border border-white/5 flex flex-col gap-2 col-span-2 md:col-span-1 emerald-glow border-t-primary-container/50">
          <span className="material-symbols-outlined text-primary-container text-3xl">verified</span>
          <h3 className="text-3xl font-extrabold text-primary-container">95%+</h3>
          <p className="text-xs text-on-surface-variant">Chính xác thử nghiệm</p>
        </div>
      </section>

      {/* Process Workflow Section */}
      <section className="flex flex-col gap-8">
        <div>
          <h2 className="text-2xl font-bold text-on-surface">Quy trình xử lý chẩn đoán</h2>
          <p className="text-sm text-on-surface-variant mt-1">3 bước đơn giản giúp bảo vệ cây trồng khỏi dịch bệnh</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="glass-panel p-6 rounded-2xl flex flex-col gap-4 relative">
            <div className="w-12 h-12 rounded-full bg-surface-container border border-outline-variant flex items-center justify-center text-primary-container">
              <span className="material-symbols-outlined text-2xl">upload_file</span>
            </div>
            <div>
              <h4 className="font-bold text-lg text-on-surface">1. Tải ảnh lá cây</h4>
              <p className="text-sm text-on-surface-variant mt-1">
                Chụp hoặc chọn ảnh cận cảnh lá bị nhiễm bệnh với ánh sáng rõ ràng.
              </p>
            </div>
          </div>

          <div className="glass-panel p-6 rounded-2xl flex flex-col gap-4 relative border-primary-container/40 emerald-glow">
            <div className="w-12 h-12 rounded-full bg-surface-container border border-primary-container flex items-center justify-center text-primary-container shadow-[0_0_10px_rgba(25,211,174,0.3)]">
              <span className="material-symbols-outlined text-2xl">analytics</span>
            </div>
            <div>
              <h4 className="font-bold text-lg text-primary-container">2. Phân tích AI</h4>
              <p className="text-sm text-on-surface-variant mt-1">
                Mạng nơ-ron học sâu quét các triệu chứng hoại tử và vi vết bệnh.
              </p>
            </div>
          </div>

          <div className="glass-panel p-6 rounded-2xl flex flex-col gap-4 relative">
            <div className="w-12 h-12 rounded-full bg-surface-container border border-outline-variant flex items-center justify-center text-primary-container">
              <span className="material-symbols-outlined text-2xl">healing</span>
            </div>
            <div>
              <h4 className="font-bold text-lg text-on-surface">3. Phác đồ điều trị</h4>
              <p className="text-sm text-on-surface-variant mt-1">
                Nhận ngay danh sách hành động khắc phục và hướng dẫn phòng ngừa cụ thể.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
