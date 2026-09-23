import React, { useState } from 'react';

interface CarePageProps {
  onDiagnoseNow?: () => void;
}

export const CarePage: React.FC<CarePageProps> = ({ onDiagnoseNow }) => {
  const [activeTab, setActiveTab] = useState<'principles' | 'checklist' | 'ipm' | 'safety' | 'specific_diseases'>('principles');

  const principles = [
    {
      id: 'foundation',
      title: '1. Nền tảng của một cây khỏe',
      icon: 'spa',
      color: 'text-emerald-400',
      summary: 'Cây khỏe mạnh có cơ chế đề kháng tự nhiên (miễn dịch thực vật) vượt trội.',
      content: [
        'Cây giống sạch bệnh: Chọn nguồn giống từ các cơ sở ươm chứng nhận, hạt giống đã qua xử lý nhiệt hoặc khử trùng mầm bệnh.',
        'Hệ rễ vững chắc: Đất tơi xốp, giàu chất hữu cơ và hệ vi sinh vật đối kháng giúp rễ hấp thụ dinh dưỡng tối đa.',
        'Dinh dưỡng cân đối: Không bón thừa đạm (N) làm mỏng thành tế bào lá; bổ sung đủ Silic, Canxi và Kali để gia cố biểu bì chống nấm xâm nhập.',
        'Vi khí hậu tối ưu: Đảm bảo độ chiếu sáng, độ ẩm và lưu thông gió đều khắp tán cây để lá khô ráo nhanh nhất.'
      ]
    },
    {
      id: 'soil',
      title: '2. Đất trồng & Giá thể',
      icon: 'grass',
      color: 'text-amber-400',
      summary: 'Đất là môi trường sống của rễ và cũng là nơi lưu tồn của hầu hết nấm, tuyến trùng và vi khuẩn hại rễ.',
      content: [
        'Độ pH tối ưu phụ thuộc từng loại cây: Ví dụ cà chua phát triển tốt nhất ở pH 6.0 - 6.8, trong khi khoai tây ưa đất hơi chua pH 5.0 - 6.0 để hạn chế bệnh ghẻ củ.',
        'Độ thoát nước & Thông khí: Đất bị nén chặt hoặc ngập úng gây thiếu oxy vùng rễ, làm thối rễ non và mở đường cho nấm Pythium, Phytophthora tấn công.',
        'Bổ sung hữu cơ vi sinh: Phân chuồng ủ hoai mục (nhiệt độ ủ >60°C để diệt mầm bệnh) cung cấp mùn và hệ vi sinh có ích cho đất.',
        'Xử lý đất trước khi trồng: Phơi ải đất dưới nắng gắt hoặc rắc vôi bột (CaCO3) để tiêu diệt ấu trùng sâu hại và bào tử nấm còn sót lại.'
      ]
    },
    {
      id: 'water',
      title: '3. Quản lý nước khoa học',
      icon: 'water_drop',
      color: 'text-cyan-400',
      summary: 'Thời gian lá bị ướt là yếu tố quyết định tốc độ nảy mầm và xâm nhiễm của nấm & vi khuẩn.',
      content: [
        'Quy tắc vàng: Hầu hết bào tử nấm (sương mai, úa sớm) và vi khuẩn Xanthomonas chỉ có thể xâm nhập khi màng nước đọng trên lá liên tục trên 4-6 giờ.',
        'Phương pháp tưới: Ưu tiên tưới nhỏ giọt tại gốc hoặc tưới rãnh ngấm. Tránh tưới phun mưa trên cao làm văng giọt nước chứa vi khuẩn từ lá bệnh sang lá lành.',
        'Thời điểm tưới: Tưới vào buổi sáng sớm (6h - 8h) để ánh nắng mặt trời làm khô ráo bề mặt đất và tán lá trước khi đêm xuống.',
        'Stress nước: Thiếu nước làm cây héo rũ, giảm sức đề kháng; nhưng thừa nước gây úng rễ và làm vách tế bào sũng nước, dễ bị tổn thương.'
      ]
    },
    {
      id: 'nutrition',
      title: '4. Dinh dưỡng & Cân đối phân bón',
      icon: 'science',
      color: 'text-purple-400',
      summary: 'Dinh dưỡng không phải là một công thức chung cho mọi cây mà thay đổi theo từng thời kỳ sinh trưởng.',
      content: [
        'Đạm (Nitrogen - N): Cần thiết cho phát triển thân lá, nhưng thừa đạm khiến lá xanh đậm mềm yếu, mọng nước, thu hút rầy rệp và cực kỳ mẫn cảm với nấm bệnh.',
        'Lân (Phosphorus - P): Kích thích rễ vươn sâu, củng cố khung xương cây và tăng khả năng chịu hạn.',
        'Kali (Potassium - K): Điều hòa đóng mở khí khổng, tăng độ dày thành tế bào và hỗ trợ vận chuyển đường bột nuôi quả.',
        'Canxi (Ca) & Silic (Si): Đóng vai trò như "xi măng" liên kết các vách tế bào biểu bì, ngăn ngừa vòi hút của sâu và giác bám của nấm bệnh xuyên thủng lá.'
      ]
    },
    {
      id: 'density',
      title: '5. Mật độ & Lưu thông không khí',
      icon: 'air',
      color: 'text-sky-400',
      summary: 'Tán lá rậm rạp tạo ra vi khí hậu ẩm thấp lý tưởng cho bào tử nấm nhân lên.',
      content: [
        'Khoảng cách hàng và cây: Giữ khoảng cách tối thiểu giữa các hàng (ví dụ cà chua 70-80cm, cây cách cây 45-50cm) để luồng gió tự nhiên lưu thông làm khô lá.',
        'Tỉa chồi nách (cành vô hiệu): Định kỳ vặt bỏ các chồi phụ mọc ở nách lá, chỉ giữ lại thân chính (hoặc 1-2 thân phụ tùy kỹ thuật) để tập trung ánh sáng vào lòng tán.',
        'Định hướng luống trồng: Bố trí hàng cây theo hướng gió chính hoặc hướng Bắc - Nam để tối ưu hóa khả năng đón ánh nắng mặt trời.'
      ]
    },
    {
      id: 'pruning',
      title: '6. Kỹ thuật cắt tỉa & Khử trùng dụng cụ',
      icon: 'content_cut',
      color: 'text-rose-400',
      summary: 'Vết cắt tỉa là cửa ngõ xâm nhập của vi khuẩn nếu không được thao tác đúng cách.',
      content: [
        'Tỉa lá già sát gốc: Sau khi cây bắt đầu đậu quả, cắt bỏ 3-4 lá già ở tầng dưới cùng cách mặt đất 20-30cm để ngăn đất bẩn bắn lên lá khi mưa.',
        'Thời điểm cắt tỉa: Chỉ tỉa vào ngày nắng ráo từ 9h sáng đến 3h chiều để vết thương khô miệng và đóng vảy nhanh.',
        'Khử trùng kéo cắt: Nhúng lưỡi kéo vào cồn 70 độ hoặc dung dịch Javel 1% sau mỗi cây hoặc mỗi hàng để ngăn lây lan mầm bệnh chéo.',
        'Không bẻ cành thô bạo: Luôn dùng kéo sắc, cắt dứt khoát sát nách lá, không để lại vết tước vỏ dài.'
      ]
    },
    {
      id: 'sanitation',
      title: '7. Vệ sinh đồng ruộng & Quản lý tàn dư',
      icon: 'cleaning_services',
      color: 'text-teal-400',
      summary: 'Tàn dư cây bệnh để sót trên ruộng là nguồn lây nhiễm chính cho các vụ tiếp theo.',
      content: [
        'Thu gom ngay lập tức: Lá bệnh tỉa xuống hoặc lá rụng phải được cho ngay vào bao nilon kín đem ra khỏi khu vực trồng để tiêu hủy.',
        'Không ủ phân lộ thiên từ cây bệnh: Nấm Alternaria và vi khuẩn Xanthomonas có thể sống sót nhiều tháng nếu đống ủ không đạt nhiệt độ diệt khuẩn (>65°C).',
        'Dọn sạch cỏ dại bờ ruộng: Nhiều loài cỏ dại họ Cà (cà dại, tầm bóp) là nơi ẩn náu của nấm bệnh và virus truyền bởi côn trùng.'
      ]
    },
    {
      id: 'rotation',
      title: '8. Luân canh cây trồng (Crop Rotation)',
      icon: 'published_with_changes',
      color: 'text-lime-400',
      summary: 'Phá vỡ chu kỳ sinh học của dịch hại trong đất bằng cách thay đổi cây trồng khác họ.',
      content: [
        'Quy tắc họ cây trồng: Không trồng liên tiếp các cây cùng họ Solanaceae (Cà chua, Khoai tây, Cà tím, Ớt) trên cùng một mảnh đất quá 2 vụ.',
        'Cây luân canh lý tưởng: Luân canh với cây họ Hòa thảo (ngô, lúa nước), họ Đậu (đậu tương, đậu cô ve) hoặc họ Thập tự (bắp cải, súp lơ).',
        'Cắt đứt nguồn thức ăn: Phần lớn nấm và vi khuẩn gây bệnh chuyên tính sẽ bị suy giảm mật độ nghiêm trọng sau 2-3 năm không có cây ký chủ phù hợp.'
      ]
    }
  ];

  const weeklyChecklist = [
    {
      step: 'Bước 1',
      title: 'Quan sát ngọn non & Sức khỏe tổng thể',
      icon: 'nature',
      desc: 'Ngọn non vươn thẳng, màu xanh tươi sáng, không bị quăn queo hoặc thun ngọn. Nếu ngọn non chuyển màu tím tái hoặc vàng nhạt, kiểm tra dinh dưỡng và nhiệt độ.'
    },
    {
      step: 'Bước 2',
      title: 'Kiểm tra mặt dưới lá già sát gốc',
      icon: 'search',
      desc: 'Lật mặt dưới của các lá tầng dưới để tìm đốm ngậm nước nhỏ (vi khuẩn), mốc trắng như tuyết (sương mai) hoặc đốm vòng tròn nâu (úa sớm).'
    },
    {
      step: 'Bước 3',
      title: 'Khám xét thân chính & Cuống lá',
      icon: 'line_style',
      desc: 'Tìm các vệt loét màu nâu đen, vết nứt sần sùi hoặc dấu hiệu gãy gập do nấm ăn sâu vào mô mạch dẫn.'
    },
    {
      step: 'Bước 4',
      title: 'Kiểm tra côn trùng chích hút & Môi giới truyền bệnh',
      icon: 'pest_control',
      desc: 'Lắc nhẹ ngọn cây để phát hiện rầy phấn trắng, bọ trĩ hoặc rệp muội ẩn nấp ở mặt dưới lá non (đây là tác nhân truyền virus gây xoăn lá).'
    },
    {
      step: 'Bước 5',
      title: 'Đo lường độ ẩm đất & Thoát nước',
      icon: 'water_damage',
      desc: 'Dùng ngón tay kiểm tra độ ẩm đất cách gốc 5cm. Đất phải ẩm nhưng không được úng nước đọng vũng quanh cổ rễ.'
    },
    {
      step: 'Bước 6',
      title: 'Vệ sinh tàn dư & Nhổ cỏ dại',
      icon: 'delete_sweep',
      desc: 'Thu dọn toàn bộ lá khô rụng, nhổ cỏ dại quanh gốc cây để đảm bảo gốc luôn khô ráo và thông thoáng.'
    },
    {
      step: 'Bước 7',
      title: 'Ghi nhật ký & Chụp ảnh đối chiếu',
      icon: 'camera_alt',
      desc: 'Nếu phát hiện bất kỳ đốm lá lạ nào, chụp ảnh rõ nét và sử dụng ngay công cụ chẩn đoán AI của LEAF_AI để khoanh vùng và xử lý sớm.'
    }
  ];

  return (
    <div className="max-w-5xl mx-auto px-4 md:px-8 py-8 pb-24 md:pb-12 flex flex-col gap-8">
      {/* Header */}
      <header className="flex flex-col gap-2">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-primary-container text-2xl">eco</span>
          <span className="text-xs uppercase font-bold tracking-widest text-primary-container">
            CẨM NANG NÔNG NGHIỆP BỀN VỮNG
          </span>
        </div>
        <h1 className="text-3xl md:text-4xl font-extrabold text-on-surface">
          Hướng dẫn Chăm sóc & Phòng trừ Dịch hại (IPM)
        </h1>
        <p className="text-on-surface-variant text-sm md:text-base leading-relaxed">
          Tổng hợp các nguyên tắc khoa học từ FAO và Viện khuyến nông quốc tế giúp cây trồng sinh trưởng khỏe mạnh, tối ưu năng suất và phòng ngừa dịch bệnh chủ động.
        </p>
      </header>

      {/* Navigation Sub-Tabs */}
      <div className="flex border-b border-outline-variant/30 overflow-x-auto gap-2">
        {[
          { id: 'principles', label: '8 Nguyên tắc Chăm sóc Cốt lõi', icon: 'psychiatry' },
          { id: 'checklist', label: 'Sổ tay Kiểm tra 7 Bước Hàng tuần', icon: 'fact_check' },
          { id: 'ipm', label: 'Quy trình Quản lý IPM 10 Bước', icon: 'shield' },
          { id: 'safety', label: 'An toàn Thuốc BVTV & Kháng thuốc', icon: 'health_and_safety' },
          { id: 'specific_diseases', label: 'Đặc trị Bệnh Phổ biến', icon: 'coronavirus' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`pb-3 px-3 text-xs md:text-sm font-semibold flex items-center gap-1.5 whitespace-nowrap transition-all border-b-2 ${
              activeTab === tab.id
                ? 'border-primary-container text-primary-container'
                : 'border-transparent text-on-surface-variant hover:text-on-surface'
            }`}
          >
            <span className="material-symbols-outlined text-base">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* TAB 1: PRINCIPLES */}
      {activeTab === 'principles' && (
        <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {principles.map((item) => (
            <article
              key={item.id}
              className="glass-panel p-6 rounded-2xl flex flex-col gap-4 border border-white/5 hover:border-primary-container/40 transition-all group"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-surface-container-high flex items-center justify-center border border-white/10 group-hover:border-primary-container/30 transition-colors">
                  <span className={`material-symbols-outlined text-2xl ${item.color}`}>{item.icon}</span>
                </div>
                <h3 className="text-base font-bold text-on-surface group-hover:text-primary-container transition-colors">
                  {item.title}
                </h3>
              </div>

              <p className="text-xs text-primary-container/90 italic">
                {item.summary}
              </p>

              <ul className="flex flex-col gap-2 text-xs text-on-surface-variant">
                {item.content.map((point, pIdx) => (
                  <li key={pIdx} className="flex items-start gap-2">
                    <span className="text-primary-container text-sm font-bold">•</span>
                    <span className="leading-relaxed">{point}</span>
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </section>
      )}

      {/* TAB 2: WEEKLY CHECKLIST */}
      {activeTab === 'checklist' && (
        <section className="flex flex-col gap-6">
          <div className="p-4 rounded-xl bg-primary-container/10 border border-primary-container/20 text-xs text-on-surface flex items-start gap-3">
            <span className="material-symbols-outlined text-primary-container text-xl mt-0.5">assignment</span>
            <div className="flex flex-col gap-1 leading-relaxed">
              <strong className="text-primary-container">Lời khuyên của chuyên gia:</strong>
              <span>
                Thực hiện kiểm tra vườn định kỳ 1-2 lần/tuần vào buổi sáng sớm. 
                Phát hiện sớm ở giai đoạn lá già xuất hiện đốm đầu tiên sẽ giúp kiểm soát bệnh bằng biện pháp sinh học đơn giản mà không cần dùng hóa chất mạnh.
              </span>
            </div>
          </div>

          <div className="flex flex-col gap-4">
            {weeklyChecklist.map((item, idx) => (
              <div
                key={idx}
                className="glass-panel p-4 md:p-5 rounded-2xl flex flex-col md:flex-row gap-4 items-start md:items-center border border-white/5 hover:border-primary-container/30 transition-all"
              >
                <div className="flex items-center gap-3 shrink-0">
                  <span className="w-8 h-8 rounded-full bg-primary-container/20 text-primary-container flex items-center justify-center text-xs font-extrabold">
                    {idx + 1}
                  </span>
                  <div className="w-10 h-10 rounded-xl bg-surface-container-high flex items-center justify-center text-secondary">
                    <span className="material-symbols-outlined text-2xl">{item.icon}</span>
                  </div>
                </div>

                <div className="flex-grow flex flex-col gap-1">
                  <span className="text-[10px] uppercase font-bold text-secondary tracking-wider">{item.step}</span>
                  <h4 className="text-sm font-bold text-on-surface">{item.title}</h4>
                  <p className="text-xs text-on-surface-variant leading-relaxed">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* TAB 3: IPM 10-STEP PROCESS */}
      {activeTab === 'ipm' && (
        <section className="flex flex-col gap-6">
          <div className="glass-panel p-6 rounded-2xl border border-white/10 flex flex-col gap-4">
            <div className="flex items-center gap-2 text-primary-container">
              <span className="material-symbols-outlined text-2xl">shield</span>
              <h3 className="text-lg font-bold text-on-surface">Khái niệm Quản lý Dịch hại Tổng hợp (IPM) theo FAO</h3>
            </div>
            <p className="text-xs text-on-surface-variant leading-relaxed">
              Theo Tổ chức Lương thực và Nông nghiệp Liên Hợp Quốc (FAO), IPM là việc cân nhắc cẩn thận tất cả các kỹ thuật kiểm soát dịch hại có sẵn và tích hợp các biện pháp thích hợp để ngăn chặn sự phát triển của quần thể dịch hại, giữ cho việc sử dụng thuốc BVTV ở mức độ hợp lý về mặt kinh tế và giảm thiểu rủi ro đối với sức khỏe con người và môi trường.
            </p>

            {/* IPM Pyramid Flow */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 pt-2">
              <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex flex-col gap-1">
                <span className="text-[10px] uppercase font-bold text-emerald-400">Tầng 1 - Nền tảng</span>
                <strong className="text-xs text-emerald-300">Biện pháp Canh tác</strong>
                <p className="text-[11px] text-on-surface-variant">Giống kháng, luân canh, vệ sinh đồng ruộng, tưới nhỏ giọt.</p>
              </div>

              <div className="p-3.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex flex-col gap-1">
                <span className="text-[10px] uppercase font-bold text-cyan-400">Tầng 2 - Giám sát</span>
                <strong className="text-xs text-cyan-300">Điều tra & Chẩn đoán</strong>
                <p className="text-[11px] text-on-surface-variant">Kiểm tra định kỳ, bẫy dính vàng, chẩn đoán AI nhận diện đúng tác nhân.</p>
              </div>

              <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 flex flex-col gap-1">
                <span className="text-[10px] uppercase font-bold text-amber-400">Tầng 3 - Can thiệp sinh học</span>
                <strong className="text-xs text-amber-300">Thiên địch & Vi sinh</strong>
                <p className="text-[11px] text-on-surface-variant">Bảo vệ thiên địch tự nhiên, phun Trichoderma, Bacillus subtilis.</p>
              </div>

              <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 flex flex-col gap-1">
                <span className="text-[10px] uppercase font-bold text-rose-400">Tầng 4 - Giải pháp cuối</span>
                <strong className="text-xs text-rose-300">Hóa học khi cần thiết</strong>
                <p className="text-[11px] text-on-surface-variant">Chỉ phun khi bệnh vượt ngưỡng kinh tế, chọn thuốc chọn lọc và luân phiên hoạt chất.</p>
              </div>
            </div>
          </div>

          <div className="glass-panel p-6 rounded-2xl border border-white/10 flex flex-col gap-4">
            <h4 className="text-sm font-bold text-primary-container">Chu trình 10 bước ra quyết định trong IPM</h4>
            <ol className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-on-surface">
              {[
                { step: '1. Phòng ngừa', desc: 'Chọn giống sạch bệnh, khử trùng đất và giá thể.' },
                { step: '2. Giám sát', desc: 'Kiểm tra mật độ bệnh hại và thời tiết hàng tuần.' },
                { step: '3. Xác định đúng', desc: 'Phân biệt chính xác giữa nấm, vi khuẩn, virus hoặc thiếu dinh dưỡng.' },
                { step: '4. Đánh giá ngưỡng', desc: 'Xác định mức độ gây hại có đe dọa năng suất kinh tế hay không.' },
                { step: '5. Biện pháp cơ học', desc: 'Tỉa bỏ lá bệnh, nhổ cây nhiễm nặng, làm bẫy dính.' },
                { step: '6. Tác động môi trường', desc: 'Điều chỉnh hệ thống tưới và thông gió nhà màng.' },
                { step: '7. Kiểm soát sinh học', desc: 'Phun chế phẩm vi sinh đối kháng để chiếm lĩnh bề mặt.' },
                { step: '8. Can thiệp hóa học', desc: 'Sử dụng hoạt chất đặc hiệu theo nhãn đăng ký hợp pháp.' },
                { step: '9. Tuân thủ an toàn', desc: 'Đảm bảo bảo hộ lao động và thời gian cách ly (PHI).' },
                { step: '10. Đánh giá lại', desc: 'Kiểm tra hiệu quả sau 5-7 ngày và ghi chép nhật ký vườn.' },
              ].map((item, idx) => (
                <li key={idx} className="glass-panel p-3 rounded-xl flex items-start gap-2 border border-white/5">
                  <span className="font-bold text-primary-container shrink-0">{idx + 1}.</span>
                  <div>
                    <strong className="text-on-surface block mb-0.5">{item.step}</strong>
                    <span className="text-on-surface-variant leading-relaxed">{item.desc}</span>
                  </div>
                </li>
              ))}
            </ol>
          </div>
        </section>
      )}

      {/* TAB 4: SAFETY & RESISTANCE MANAGEMENT */}
      {activeTab === 'safety' && (
        <section className="flex flex-col gap-6">
          <div className="glass-panel p-6 rounded-2xl border border-white/10 flex flex-col gap-4">
            <h3 className="text-base font-bold text-amber-400 flex items-center gap-2">
              <span className="material-symbols-outlined text-xl">warning</span>
              Nguyên tắc 4 Đúng khi sử dụng Thuốc Bảo vệ Thực vật
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="glass-panel p-3.5 rounded-xl border border-white/5 flex flex-col gap-1">
                <strong className="text-primary-container">1. Đúng thuốc</strong>
                <p className="text-on-surface-variant">Chọn đúng loại thuốc có hoạt chất đặc trị tác nhân gây bệnh (không dùng thuốc trừ nấm để trị bệnh do vi khuẩn).</p>
              </div>
              <div className="glass-panel p-3.5 rounded-xl border border-white/5 flex flex-col gap-1">
                <strong className="text-primary-container">2. Đúng liều lượng & nồng độ</strong>
                <p className="text-on-surface-variant">Pha đúng theo chỉ dẫn trên nhãn. Không tự ý tăng liều gây cháy lá hoặc giảm liều tạo điều kiện cho nấm kháng thuốc.</p>
              </div>
              <div className="glass-panel p-3.5 rounded-xl border border-white/5 flex flex-col gap-1">
                <strong className="text-primary-container">3. Đúng lúc</strong>
                <p className="text-on-surface-variant">Phun khi bệnh chớm xuất hiện hoặc trước đợt sương mù kéo dài. Tránh phun khi trời nắng gắt (trên 32°C) hoặc sắp mưa.</p>
              </div>
              <div className="glass-panel p-3.5 rounded-xl border border-white/5 flex flex-col gap-1">
                <strong className="text-primary-container">4. Đúng cách</strong>
                <p className="text-on-surface-variant">Phun phủ đều 2 mặt lá, đi xuôi theo chiều gió, mang đầy đủ đồ bảo hộ và tuân thủ nghiêm ngặt thời gian cách ly.</p>
              </div>
            </div>
          </div>

          <div className="glass-panel p-6 rounded-2xl border border-white/10 flex flex-col gap-3">
            <h3 className="text-base font-bold text-primary-container flex items-center gap-2">
              <span className="material-symbols-outlined text-xl">autorenew</span>
              Quản lý Nguy cơ Kháng thuốc (Fungicide Resistance Management - FRAC)
            </h3>
            <p className="text-xs text-on-surface-variant leading-relaxed">
              Nếu sử dụng liên tục một hoạt chất trừ nấm duy nhất (đặc biệt là các nhóm thuốc có cơ chế tác động đơn điểm), các cá thể nấm mang đột biến kháng thuốc sẽ nhanh chóng chiếm ưu thế và khiến thuốc mất hoàn toàn hiệu lực.
            </p>
            <ul className="text-xs text-on-surface-variant list-disc pl-5 flex flex-col gap-1.5 leading-relaxed">
              <li>Luân phiên các nhóm thuốc có mã nhóm FRAC khác nhau (khác cơ chế tác động sinh học).</li>
              <li>Kết hợp hoạt chất lưu dẫn chuyên biệt với hoạt chất tiếp xúc đa điểm (Multi-site như Mancozeb, Chlorothalonil).</li>
              <li>Không bao giờ phun dưới liều khuyến cáo của nhà sản xuất.</li>
            </ul>
          </div>
        </section>
      )}

      {/* TAB 5: SPECIFIC DISEASES (Septoria, Leaf Mold, Powdery Mildew) */}
      {activeTab === 'specific_diseases' && (
        <section className="flex flex-col gap-6">
          <div className="glass-panel p-6 rounded-2xl border border-white/10 flex flex-col gap-4">
            <div className="flex items-center gap-2 text-primary-container">
              <span className="material-symbols-outlined text-2xl">coronavirus</span>
              <h3 className="text-lg font-bold text-on-surface">Đặc trị các bệnh hại lá phổ biến</h3>
            </div>
            <p className="text-xs text-on-surface-variant leading-relaxed">
              Hướng dẫn nhận diện và điều trị chuyên sâu cho các bệnh nấm thường gặp gây thiệt hại nặng trên cà chua và cây họ Cà.
            </p>

            <div className="flex flex-col gap-5 mt-2">
              {/* Septoria */}
              <div className="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20 flex flex-col gap-2">
                <h4 className="text-sm font-bold text-emerald-400">1. Đốm mắt cua (Septoria Leaf Spot)</h4>
                <p className="text-[11px] text-on-surface-variant">
                  <strong>Triệu chứng:</strong> Đốm nhỏ hình tròn (1-2mm), viền nâu đậm, tâm xám nhạt đục lỗ chỗ. Lây từ dưới gốc lên ngọn.
                </p>
                <p className="text-[11px] text-on-surface-variant">
                  <strong>Cách trị:</strong> Luân canh cây trồng; loại bỏ lá bị bệnh; phun thuốc trị nấm có gốc Chlorothalonil hoặc Copper.
                </p>
              </div>

              {/* Leaf Mold */}
              <div className="p-4 rounded-xl bg-yellow-500/5 border border-yellow-500/20 flex flex-col gap-2">
                <h4 className="text-sm font-bold text-yellow-400">2. Nấm mốc lá (Leaf Mold - Passalora fulva)</h4>
                <p className="text-[11px] text-on-surface-variant">
                  <strong>Triệu chứng:</strong> Đốm vàng nhạt ở mặt trên lá, mặt dưới nổi lớp nấm mốc màu ô liu hoặc nâu tím. Rất dễ bùng phát trong nhà màng ẩm.
                </p>
                <p className="text-[11px] text-on-surface-variant">
                  <strong>Cách trị:</strong> Tăng cường thông gió nhà màng (độ ẩm &lt; 85%); giảm mật độ trồng; sử dụng giống kháng bệnh; phun thuốc gốc Mancozeb hoặc Difenoconazole.
                </p>
              </div>

              {/* Powdery Mildew */}
              <div className="p-4 rounded-xl bg-slate-400/10 border border-slate-400/30 flex flex-col gap-2">
                <h4 className="text-sm font-bold text-slate-300">3. Nấm phấn trắng (Powdery Mildew)</h4>
                <p className="text-[11px] text-on-surface-variant">
                  <strong>Triệu chứng:</strong> Lớp bột màu trắng như phấn phủ trên mặt lá, làm lá vàng úa và rụng sớm. Phát triển mạnh ở nhiệt độ khô ấm và thiếu nắng.
                </p>
                <p className="text-[11px] text-on-surface-variant">
                  <strong>Cách trị:</strong> Phun lưu huỳnh thấm ướt (chú ý không phun khi trời quá nóng), dung dịch Bicarbonate hoặc dầu Neem. Giữ lá khô ráo.
                </p>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* CTA Card linking to Diagnose */}
      <section className="glass-panel p-6 rounded-2xl border border-primary-container/40 emerald-glow flex flex-col sm:flex-row justify-between items-center gap-4">
        <div className="flex flex-col gap-1 text-center sm:text-left">
          <h3 className="text-lg font-bold text-on-surface">Phát hiện dấu hiệu đốm lạ trên lá cây?</h3>
          <p className="text-xs text-on-surface-variant">
            Chụp ảnh cận cảnh mẫu lá để mô hình AI tự động phát hiện, khoanh vùng và đề xuất phác đồ điều trị ngay.
          </p>
        </div>

        {onDiagnoseNow && (
          <button
            onClick={onDiagnoseNow}
            className="bg-primary-container text-on-primary font-bold px-6 py-3 rounded-xl text-xs flex items-center gap-2 hover:opacity-90 transition-all whitespace-nowrap shadow-[0_0_15px_rgba(25,211,174,0.3)]"
          >
            <span className="material-symbols-outlined">add_a_photo</span>
            Chẩn đoán lá ngay
          </button>
        )}
      </section>
    </div>
  );
};
