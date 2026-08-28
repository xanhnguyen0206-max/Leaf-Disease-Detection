import React, { useEffect, useState } from 'react';
import { fetchDiseaseById } from '../services/api';
import { Disease } from '../types';
import { SafeImage } from '../components/SafeImage';

interface DiseaseDetailProps {
  diseaseId: string;
  onBack: () => void;
  onDiagnoseNow: () => void;
  onNavigateCare?: () => void;
}

export const DiseaseDetailPage: React.FC<DiseaseDetailProps> = ({
  diseaseId,
  onBack,
  onDiagnoseNow,
  onNavigateCare
}) => {
  const [disease, setDisease] = useState<Disease | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'symptoms' | 'prevention' | 'ipm' | 'aftercare' | 'sources'>('overview');

  useEffect(() => {
    fetchDiseaseById(diseaseId).then(setDisease);
  }, [diseaseId]);

  if (!disease) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center text-on-surface-variant flex items-center justify-center gap-2">
        <span className="material-symbols-outlined animate-spin text-primary-container">sync</span>
        Đang tải hồ sơ bệnh học chuyên sâu...
      </div>
    );
  }

  const getSeverityBadgeClass = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'nghiêm trọng':
        return 'bg-error/20 border-error/40 text-error';
      case 'trung bình':
        return 'bg-amber-500/20 border-amber-500/40 text-amber-300';
      default:
        return 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300';
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 md:px-8 py-8 pb-24 md:pb-12 flex flex-col gap-8">
      {/* Back Navigation Bar */}
      <div className="flex justify-between items-center flex-wrap gap-4">
        <button
          onClick={onBack}
          className="text-xs font-semibold text-on-surface-variant hover:text-primary-container flex items-center gap-1.5 transition-colors"
        >
          <span className="material-symbols-outlined text-base">arrow_back</span>
          Quay lại Thư viện bệnh
        </button>

        <div className="flex gap-2">
          <button
            onClick={onDiagnoseNow}
            className="bg-primary-container text-on-primary font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-1.5 hover:opacity-90 transition-all shadow-[0_0_12px_rgba(25,211,174,0.3)]"
          >
            <span className="material-symbols-outlined text-sm">add_a_photo</span>
            Chẩn đoán lá ngay
          </button>
        </div>
      </div>

      {/* Hero Card */}
      <div className="glass-panel rounded-3xl overflow-hidden border border-white/10 flex flex-col gap-6">
        <div className="relative h-72 md:h-96 w-full overflow-hidden">
          <SafeImage
            src={disease.image_url}
            alt={disease.name}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-background via-background/60 to-transparent opacity-95" />
          
          <div className="absolute bottom-6 left-6 right-6 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
            <div className="flex flex-col gap-1.5">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="bg-secondary/20 border border-secondary/30 text-secondary px-2.5 py-0.5 rounded-full text-xs font-bold">
                  {disease.plant}
                </span>
                {disease.english_name && (
                  <span className="text-xs text-on-surface-variant font-medium">
                    {disease.english_name}
                  </span>
                )}
              </div>

              <h1 className="text-2xl md:text-4xl font-extrabold text-on-surface leading-tight">
                {disease.name}
              </h1>

              {disease.scientific_name && (
                <p className="text-sm text-primary-container italic">
                  Tác nhân khoa học: {disease.scientific_name}
                </p>
              )}
            </div>

            <span className={`border px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider backdrop-blur-md shrink-0 ${getSeverityBadgeClass(disease.severity)}`}>
              Mức độ: {disease.severity}
            </span>
          </div>
        </div>

        {/* Quick Biological Metrics Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 px-6 pb-2">
          <div className="glass-panel p-3.5 rounded-xl flex flex-col gap-1 border border-white/5">
            <span className="text-[10px] uppercase font-bold text-on-surface-variant">Tác nhân gây bệnh</span>
            <span className="text-xs font-semibold text-on-surface truncate">{disease.pathogen || 'Chưa cập nhật'}</span>
          </div>
          <div className="glass-panel p-3.5 rounded-xl flex flex-col gap-1 border border-white/5">
            <span className="text-[10px] uppercase font-bold text-on-surface-variant">Điều kiện thuận lợi</span>
            <span className="text-xs font-semibold text-on-surface truncate">{disease.favorable_conditions || 'Ẩm độ cao >80%'}</span>
          </div>
          <div className="glass-panel p-3.5 rounded-xl flex flex-col gap-1 border border-white/5">
            <span className="text-[10px] uppercase font-bold text-on-surface-variant">Con đường lây lan</span>
            <span className="text-xs font-semibold text-on-surface truncate">Gió, nước bắn, tàn dư</span>
          </div>
          <div className="glass-panel p-3.5 rounded-xl flex flex-col gap-1 border border-white/5">
            <span className="text-[10px] uppercase font-bold text-on-surface-variant">Phác đồ phòng trị</span>
            <span className="text-xs font-semibold text-primary-container">IPM Đa tầng</span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex border-b border-outline-variant/30 px-6 overflow-x-auto gap-2">
          {[
            { id: 'overview', label: 'Tổng quan & Tác nhân', icon: 'info' },
            { id: 'symptoms', label: 'Triệu chứng & Nhận biết', icon: 'visibility' },
            { id: 'prevention', label: 'Phòng bệnh & Canh tác', icon: 'shield' },
            { id: 'ipm', label: 'Kiểm soát & Trị bệnh (IPM)', icon: 'medical_services' },
            { id: 'aftercare', label: 'Theo dõi & Sai lầm', icon: 'history_edu' },
            { id: 'sources', label: 'Nguồn tham khảo', icon: 'menu_book' },
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

        {/* Tab Contents */}
        <div className="p-6 pt-2 flex flex-col gap-6">
          {/* TAB 1: OVERVIEW */}
          {activeTab === 'overview' && (
            <div className="flex flex-col gap-6">
              <div>
                <h3 className="text-base font-bold text-primary-container mb-2">Mô tả tổng quan</h3>
                <p className="text-sm text-on-surface-variant leading-relaxed">
                  {disease.overview || disease.description}
                </p>
              </div>

              {disease.risk_level_explanation && (
                <div className="p-4 rounded-xl bg-error/10 border border-error/20 flex flex-col gap-1">
                  <h4 className="text-xs font-bold text-error uppercase tracking-wider flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-base">warning</span>
                    Đánh giá mức độ nguy hiểm:
                  </h4>
                  <p className="text-xs text-error/90 leading-relaxed">{disease.risk_level_explanation}</p>
                </div>
              )}

              {disease.favorable_conditions && (
                <div>
                  <h3 className="text-base font-bold text-primary-container mb-2">Điều kiện phát sinh & phát triển</h3>
                  <div className="glass-panel p-4 rounded-xl text-xs text-on-surface leading-relaxed border border-white/5">
                    {disease.favorable_conditions}
                  </div>
                </div>
              )}

              {disease.transmission && disease.transmission.length > 0 && (
                <div>
                  <h3 className="text-base font-bold text-primary-container mb-3">Con đường lây lan dịch bệnh</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {disease.transmission.map((item, idx) => (
                      <div key={idx} className="glass-panel p-3.5 rounded-xl flex items-start gap-2.5 text-xs text-on-surface border border-white/5">
                        <span className="material-symbols-outlined text-secondary text-base mt-0.5 shrink-0">arrow_forward</span>
                        <span>{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: SYMPTOMS */}
          {activeTab === 'symptoms' && (
            <div className="flex flex-col gap-6">
              <div>
                <h3 className="text-base font-bold text-primary-container mb-3">Diễn tiến triệu chứng theo giai đoạn</h3>
                <div className="flex flex-col gap-3">
                  <div className="glass-panel p-4 rounded-xl border border-white/5 flex flex-col gap-1.5">
                    <span className="text-xs font-bold uppercase text-emerald-400 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-emerald-400" />
                      1. Giai đoạn sớm (Mới phát sinh)
                    </span>
                    <ul className="text-xs text-on-surface-variant list-disc pl-5 leading-relaxed flex flex-col gap-1">
                      {disease.early_symptoms?.map((s, idx) => <li key={idx}>{s}</li>) || <li>{disease.symptoms[0]}</li>}
                    </ul>
                  </div>

                  <div className="glass-panel p-4 rounded-xl border border-white/5 flex flex-col gap-1.5">
                    <span className="text-xs font-bold uppercase text-amber-400 flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-amber-400" />
                      2. Giai đoạn phát triển (Bùng phát)
                    </span>
                    <ul className="text-xs text-on-surface-variant list-disc pl-5 leading-relaxed flex flex-col gap-1">
                      {disease.mid_symptoms?.map((s, idx) => <li key={idx}>{s}</li>) || <li>{disease.symptoms[1] || disease.symptoms[0]}</li>}
                    </ul>
                  </div>

                  <div className="glass-panel p-4 rounded-xl border border-white/5 flex flex-col gap-1.5">
                    <span className="text-xs font-bold uppercase text-error flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-error" />
                      3. Giai đoạn nặng (Tàn lụi / Hoại tử)
                    </span>
                    <ul className="text-xs text-on-surface-variant list-disc pl-5 leading-relaxed flex flex-col gap-1">
                      {disease.severe_symptoms?.map((s, idx) => <li key={idx}>{s}</li>) || <li>{disease.symptoms[2] || disease.symptoms[0]}</li>}
                    </ul>
                  </div>
                </div>
              </div>

              {disease.similar_diseases_diff && disease.similar_diseases_diff.length > 0 && (
                <div>
                  <h3 className="text-base font-bold text-primary-container mb-3">Cách phân biệt với các bệnh tương tự</h3>
                  <div className="flex flex-col gap-2">
                    {disease.similar_diseases_diff.map((diff, idx) => (
                      <div key={idx} className="p-3.5 rounded-xl bg-surface-container-high border border-outline-variant/30 text-xs text-on-surface leading-relaxed">
                        🔍 {diff}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: PREVENTION */}
          {activeTab === 'prevention' && (
            <div className="flex flex-col gap-6">
              {disease.prevention_before_planting && (
                <div>
                  <h3 className="text-base font-bold text-primary-container mb-2">1. Phòng bệnh trước khi gieo trồng</h3>
                  <ul className="grid grid-cols-1 gap-2">
                    {disease.prevention_before_planting.map((p, idx) => (
                      <li key={idx} className="glass-panel p-3 rounded-xl flex items-start gap-2.5 text-xs text-on-surface border border-white/5">
                        <span className="material-symbols-outlined text-primary-container text-sm mt-0.5">verified_user</span>
                        <span>{p}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {disease.prevention_during_growth && (
                <div>
                  <h3 className="text-base font-bold text-primary-container mb-2">2. Phòng bệnh trong quá trình canh tác</h3>
                  <ul className="grid grid-cols-1 gap-2">
                    {disease.prevention_during_growth.map((p, idx) => (
                      <li key={idx} className="glass-panel p-3 rounded-xl flex items-start gap-2.5 text-xs text-on-surface border border-white/5">
                        <span className="material-symbols-outlined text-secondary text-sm mt-0.5">eco</span>
                        <span>{p}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {disease.water_management && (
                  <div className="glass-panel p-4 rounded-xl border border-white/5 flex flex-col gap-1">
                    <strong className="text-xs text-primary-container uppercase font-bold">💧 Quản lý nước tưới</strong>
                    <p className="text-xs text-on-surface-variant leading-relaxed">{disease.water_management}</p>
                  </div>
                )}
                {disease.nutrition_management && (
                  <div className="glass-panel p-4 rounded-xl border border-white/5 flex flex-col gap-1">
                    <strong className="text-xs text-primary-container uppercase font-bold">🌱 Quản lý dinh dưỡng</strong>
                    <p className="text-xs text-on-surface-variant leading-relaxed">{disease.nutrition_management}</p>
                  </div>
                )}
                {disease.density_management && (
                  <div className="glass-panel p-4 rounded-xl border border-white/5 flex flex-col gap-1">
                    <strong className="text-xs text-primary-container uppercase font-bold">📐 Mật độ & Thông thoáng</strong>
                    <p className="text-xs text-on-surface-variant leading-relaxed">{disease.density_management}</p>
                  </div>
                )}
                {disease.pruning_guide && (
                  <div className="glass-panel p-4 rounded-xl border border-white/5 flex flex-col gap-1">
                    <strong className="text-xs text-primary-container uppercase font-bold">✂️ Cắt tỉa & Khử trùng</strong>
                    <p className="text-xs text-on-surface-variant leading-relaxed">{disease.pruning_guide}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 4: IPM & TREATMENT */}
          {activeTab === 'ipm' && (
            <div className="flex flex-col gap-6">
              {disease.biological_control && disease.biological_control.length > 0 && (
                <div>
                  <h3 className="text-base font-bold text-primary-container mb-2">1. Biện pháp sinh học & Nấm đối kháng</h3>
                  <div className="flex flex-col gap-2">
                    {disease.biological_control.map((bio, idx) => (
                      <div key={idx} className="glass-panel p-3.5 rounded-xl flex items-start gap-2.5 text-xs text-on-surface border border-emerald-500/20">
                        <span className="material-symbols-outlined text-emerald-400 text-base mt-0.5">psychiatry</span>
                        <span>{bio}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {disease.chemical_control_principles && disease.chemical_control_principles.length > 0 && (
                <div>
                  <h3 className="text-base font-bold text-primary-container mb-2">2. Nguyên tắc can thiệp hóa học an toàn (Khi dịch bệnh vượt ngưỡng)</h3>
                  <div className="flex flex-col gap-2">
                    {disease.chemical_control_principles.map((chem, idx) => (
                      <div key={idx} className="glass-panel p-3.5 rounded-xl flex items-start gap-2.5 text-xs text-on-surface border border-amber-500/20">
                        <span className="material-symbols-outlined text-amber-400 text-base mt-0.5">science</span>
                        <span>{chem}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="p-4 rounded-xl bg-primary-container/10 border border-primary-container/30 flex items-start gap-3">
                <span className="material-symbols-outlined text-primary-container text-xl mt-0.5">gavel</span>
                <div className="text-xs text-on-surface flex flex-col gap-1 leading-relaxed">
                  <strong className="text-primary-container">Lưu ý tuân thủ quy định thuốc BVTV:</strong>
                  <span>
                    Chỉ sử dụng các sản phẩm hoạt chất đã được đăng ký lưu hành hợp pháp tại cơ quan BVTV địa phương. 
                    Tuyệt đối tuân thủ hướng dẫn nồng độ, liều lượng, trang bị bảo hộ và Thời gian cách ly (PHI) ghi trên nhãn sản phẩm.
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: AFTERCARE & MISTAKES */}
          {activeTab === 'aftercare' && (
            <div className="flex flex-col gap-6">
              {disease.aftercare_monitoring && (
                <div>
                  <h3 className="text-base font-bold text-primary-container mb-2">Theo dõi sau điều trị</h3>
                  <ul className="flex flex-col gap-2">
                    {disease.aftercare_monitoring.map((m, idx) => (
                      <li key={idx} className="glass-panel p-3 rounded-xl flex items-start gap-2 text-xs text-on-surface border border-white/5">
                        <span className="material-symbols-outlined text-emerald-400 text-sm mt-0.5">task_alt</span>
                        <span>{m}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {disease.common_mistakes && disease.common_mistakes.length > 0 && (
                <div>
                  <h3 className="text-base font-bold text-error mb-2">Những sai lầm phổ biến cần tránh</h3>
                  <div className="flex flex-col gap-2">
                    {disease.common_mistakes.map((mis, idx) => (
                      <div key={idx} className="p-3.5 rounded-xl bg-error/10 border border-error/20 text-xs text-error/90 flex items-start gap-2">
                        <span className="material-symbols-outlined text-error text-base mt-0.5">cancel</span>
                        <span>{mis}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {disease.when_to_seek_help && (
                <div className="glass-panel p-4 rounded-xl border border-white/5 flex flex-col gap-1">
                  <strong className="text-xs text-secondary uppercase font-bold">Khi nào cần tham vấn chuyên gia nông nghiệp?</strong>
                  <p className="text-xs text-on-surface-variant leading-relaxed">{disease.when_to_seek_help}</p>
                </div>
              )}
            </div>
          )}

          {/* TAB 6: SOURCES */}
          {activeTab === 'sources' && (
            <div className="flex flex-col gap-4">
              <h3 className="text-base font-bold text-primary-container mb-1">Tài liệu tham khảo & Nguồn xác thực</h3>
              <p className="text-xs text-on-surface-variant">
                Hồ sơ bệnh học này được tổng hợp và đối chiếu từ các tài liệu khuyến nông và nghiên cứu bệnh cây quốc tế:
              </p>

              <div className="flex flex-col gap-2">
                {disease.sources && disease.sources.length > 0 ? (
                  disease.sources.map((src, idx) => (
                    <div key={idx} className="glass-panel p-3 rounded-xl flex items-start gap-2 text-xs text-on-surface border border-white/5">
                      <span className="material-symbols-outlined text-primary-container text-sm mt-0.5">menu_book</span>
                      <span>{src}</span>
                    </div>
                  ))
                ) : (
                  <div className="glass-panel p-3 rounded-xl text-xs text-on-surface-variant">
                    FAO Plant Protection Series & University Agricultural Extension.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Bottom Cross-linking CTA */}
        <div className="p-6 pt-4 border-t border-outline-variant/30 flex flex-col sm:flex-row gap-4">
          <button
            onClick={onDiagnoseNow}
            className="flex-1 bg-primary-container text-on-primary font-bold py-3.5 rounded-xl text-sm flex items-center justify-center gap-2 hover:opacity-90 transition-all shadow-[0_0_15px_rgba(25,211,174,0.3)]"
          >
            <span className="material-symbols-outlined">add_a_photo</span>
            Chẩn đoán lá cà chua ngay
          </button>
          {onNavigateCare && (
            <button
              onClick={onNavigateCare}
              className="flex-1 bg-transparent border border-primary-container text-primary-container font-semibold py-3.5 rounded-xl text-sm flex items-center justify-center gap-2 hover:bg-primary-container/10 transition-all"
            >
              <span className="material-symbols-outlined">menu_book</span>
              Xem sổ tay chăm sóc IPM toàn diện
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
