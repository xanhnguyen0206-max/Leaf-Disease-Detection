import React from 'react';

export const AboutPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 md:px-8 py-8 pb-24 md:pb-12 flex flex-col gap-8">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl md:text-4xl font-extrabold text-on-surface">Về LEAF_AI</h1>
        <p className="text-on-surface-variant text-sm md:text-base">
          Nền tảng trí tuệ nhân tạo hỗ trợ nông nghiệp chính xác và bảo vệ năng suất cây trồng.
        </p>
      </header>

      <div className="glass-panel p-6 md:p-8 rounded-2xl flex flex-col gap-6 border border-white/10">
        <div>
          <h3 className="text-lg font-bold text-primary-container mb-2">Sứ mệnh dự án</h3>
          <p className="text-sm text-on-surface-variant leading-relaxed">
            LEAF_AI ra đời với mục tiêu cung cấp công cụ chẩn đoán nhanh bệnh hại cây trồng dựa trên hình ảnh chụp từ điện thoại thông minh, giúp người nông dân phát hiện tác nhân gây bệnh ngay từ giai đoạn đầu và đưa ra phác đồ điều trị an toàn, hiệu quả.
          </p>
        </div>

        <div>
          <h3 className="text-lg font-bold text-primary-container mb-2">Kiến trúc công nghệ</h3>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-on-surface">
            <li className="glass-panel p-4 rounded-xl">
              <strong className="text-primary-container block mb-1">Frontend Layer</strong>
              React + TypeScript + Vite + Tailwind CSS với giao diện tối ưu chuẩn Google Stitch Design System.
            </li>
            <li className="glass-panel p-4 rounded-xl">
              <strong className="text-primary-container block mb-1">Backend API Layer</strong>
              Python + FastAPI + SQLAlchemy + SQLite cung cấp REST API hiệu năng cao cho dữ liệu bệnh và lưu trữ lịch sử.
            </li>
            <li className="glass-panel p-4 rounded-xl">
              <strong className="text-primary-container block mb-1">AI Prediction Service</strong>
              Mô hình học sâu (Deep Learning CNN / YOLOv8) tích hợp qua interface dịch vụ trừu tượng, sẵn sàng nâng cấp.
            </li>
            <li className="glass-panel p-4 rounded-xl">
              <strong className="text-primary-container block mb-1">Interactive Graphics</strong>
              WebGL Canvas Shaders & Three.js 3D Rendering mang lại trải nghiệm thị giác sống động.
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};
