import React from 'react';

export const CarePage: React.FC = () => {
  const guides = [
    {
      title: "Quản lý độ ẩm & Tưới nước",
      icon: "water_drop",
      description: "Hầu hết nấm bệnh nông nghiệp (như sương mai, úa sớm) phát triển mạnh khi nước đọng trên bề mặt lá quá 4-6 giờ. Sử dụng hệ thống tưới nhỏ giọt."
    },
    {
      title: "Cắt tỉa & Lưu thông không khí",
      icon: "air",
      description: "Thường xuyên tỉa lá già ở tầng dưới gốc để tăng khoảng trống thông thoáng, giúp ánh nắng mặt trời tiêu diệt mầm bệnh tự nhiên."
    },
    {
      title: "Luân canh cây trồng",
      icon: "published_with_changes",
      description: "Không trồng các cây cùng họ (như cà chua, khoai tây, ớt) trên cùng một mảnh đất quá 2 vụ liên tiếp để ngắt vòng đời tác nhân nấm trong đất."
    },
    {
      title: "Phòng trừ sinh học",
      icon: "eco",
      description: "Ưu tiên phun các nấm đối kháng Trichoderma hoặc chế phẩm vi sinh Bacillus subtilis để ngăn nấm bệnh chiếm lĩnh tế bào lá."
    }
  ];

  return (
    <div className="max-w-5xl mx-auto px-4 md:px-8 py-8 pb-24 md:pb-12 flex flex-col gap-8">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl md:text-4xl font-extrabold text-on-surface">Hướng dẫn chăm sóc & Phòng bệnh</h1>
        <p className="text-on-surface-variant text-sm md:text-base">
          Các nguyên tắc khoa học giúp tối ưu sức khỏe cây trồng và ngăn ngừa dịch bệnh bùng phát.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {guides.map((item, idx) => (
          <div key={idx} className="glass-panel p-6 rounded-2xl flex flex-col gap-4 border border-white/5 hover:border-primary-container/40 transition-all">
            <div className="w-12 h-12 rounded-full bg-primary-container/10 border border-primary-container/20 flex items-center justify-center text-primary-container">
              <span className="material-symbols-outlined text-2xl">{item.icon}</span>
            </div>
            <div>
              <h3 className="text-lg font-bold text-on-surface mb-2">{item.title}</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">{item.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
