import React, { useState, useEffect } from 'react';
import { fetchDiseases } from '../services/api';
import { Disease } from '../types';
import { SafeImage } from '../components/SafeImage';

interface DiseaseLibraryProps {
  onSelectDisease: (id: string) => void;
}

export const DiseaseLibraryPage: React.FC<DiseaseLibraryProps> = ({ onSelectDisease }) => {
  const [diseases, setDiseases] = useState<Disease[]>([]);
  const [search, setSearch] = useState('');
  const [selectedPlant, setSelectedPlant] = useState('Tất cả');
  const [loading, setLoading] = useState(true);

  const plants = ['Tất cả', 'Cà chua'];

  useEffect(() => {
    loadDiseases();
  }, [search, selectedPlant]);

  const loadDiseases = async () => {
    setLoading(true);
    try {
      const data = await fetchDiseases(search, selectedPlant);
      setDiseases(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

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
    <div className="max-w-6xl mx-auto px-4 md:px-8 py-8 pb-24 md:pb-12 flex flex-col gap-8">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl md:text-4xl font-extrabold text-on-surface">Thư viện bệnh cây trồng</h1>
        <p className="text-on-surface-variant text-sm md:text-base">
          Cơ sở dữ liệu bệnh học nông nghiệp chuẩn hóa: Tác nhân, triệu chứng theo giai đoạn, phác đồ phòng trừ sinh học & hóa học an toàn.
        </p>
      </header>

      {/* Search & Filter */}
      <section className="flex flex-col md:flex-row gap-4 justify-between items-center">
        <div className="relative w-full md:w-96">
          <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-on-surface-variant">
            search
          </span>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Tìm theo tên bệnh, cây trồng, tác nhân..."
            className="w-full bg-surface-container-high border border-outline-variant rounded-full py-3 pl-12 pr-4 text-sm text-on-surface placeholder:text-on-surface-variant focus:outline-none focus:border-primary-container"
          />
        </div>

        {/* Plant Filter Chips */}
        <div className="flex gap-2 overflow-x-auto w-full md:w-auto pb-1">
          {plants.map((p) => (
            <button
              key={p}
              onClick={() => setSelectedPlant(p)}
              className={`px-4 py-2 rounded-full text-xs font-semibold whitespace-nowrap transition-all ${
                selectedPlant === p
                  ? 'bg-primary-container text-on-primary shadow-[0_0_10px_rgba(25,211,174,0.3)]'
                  : 'bg-surface-container-high text-on-surface-variant hover:bg-surface-variant'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </section>

      {/* Disease Grid */}
      {loading ? (
        <div className="py-16 text-center text-on-surface-variant flex items-center justify-center gap-2">
          <span className="material-symbols-outlined animate-spin text-primary-container">sync</span>
          Đang tải dữ liệu thư viện bệnh...
        </div>
      ) : diseases.length === 0 ? (
        <div className="py-16 text-center text-on-surface-variant flex flex-col items-center gap-3">
          <span className="material-symbols-outlined text-4xl text-outline-variant">search_off</span>
          <p className="text-sm">Không tìm thấy bệnh cây trồng phù hợp với từ khóa.</p>
        </div>
      ) : (
        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {diseases.map((item) => (
            <article
              key={item.id}
              className="glass-panel rounded-2xl overflow-hidden border border-outline-variant/30 flex flex-col justify-between hover:border-primary-container/50 transition-all duration-300 group"
            >
              <div>
                <div className="relative h-48 w-full overflow-hidden bg-surface-container-high">
                  <SafeImage
                    src={item.image_url}
                    alt={item.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-surface-container to-transparent opacity-85" />
                  <div className={`absolute top-3 left-3 border px-2.5 py-0.5 rounded-full text-[10px] uppercase font-bold tracking-wider backdrop-blur-md ${getSeverityBadgeClass(item.severity)}`}>
                    {item.severity}
                  </div>
                </div>

                <div className="p-5 flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <span className="text-secondary text-xs font-semibold">{item.plant}</span>
                    {item.scientific_name && (
                      <span className="text-[10px] text-on-surface-variant italic truncate max-w-[180px]">
                        {item.scientific_name}
                      </span>
                    )}
                  </div>

                  <h3 className="text-lg font-bold text-on-surface group-hover:text-primary-container transition-colors leading-snug">
                    {item.name}
                  </h3>

                  <p className="text-xs text-on-surface-variant line-clamp-3 leading-relaxed mt-1">
                    {item.description}
                  </p>

                  {/* Symptom quick chips */}
                  {item.symptoms && item.symptoms.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {item.symptoms.slice(0, 2).map((sym, sIdx) => (
                        <span key={sIdx} className="bg-surface-variant text-[11px] text-on-surface-variant px-2 py-0.5 rounded-md truncate max-w-full">
                          • {sym}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="p-5 pt-0">
                <button
                  onClick={() => onSelectDisease(item.id)}
                  className="w-full bg-transparent border border-primary-container text-primary-container font-semibold py-2.5 rounded-xl text-xs flex items-center justify-center gap-1.5 hover:bg-primary-container/10 transition-all group-hover:bg-primary-container group-hover:text-on-primary"
                >
                  Xem tài liệu chuyên sâu
                  <span className="material-symbols-outlined text-sm">arrow_forward</span>
                </button>
              </div>
            </article>
          ))}
        </section>
      )}
    </div>
  );
};
