import React, { useEffect, useState } from 'react';
import { fetchDiseaseById } from '../services/api';
import { Disease } from '../types';

interface DiseaseDetailProps {
  diseaseId: string;
  onBack: () => void;
  onDiagnoseNow: () => void;
}

export const DiseaseDetailPage: React.FC<DiseaseDetailProps> = ({ diseaseId, onBack, onDiagnoseNow }) => {
  const [disease, setDisease] = useState<Disease | null>(null);

  useEffect(() => {
    fetchDiseaseById(diseaseId).then(setDisease);
  }, [diseaseId]);

  if (!disease) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center text-on-surface-variant flex items-center justify-center gap-2">
        <span className="material-symbols-outlined animate-spin text-primary-container">sync</span>
        Đang tải thông tin bệnh...
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 md:px-8 py-8 pb-24 md:pb-12 flex flex-col gap-8">
      <button
        onClick={onBack}
        className="self-start text-xs font-semibold text-on-surface-variant hover:text-primary-container flex items-center gap-1"
      >
        <span className="material-symbols-outlined text-sm">arrow_back</span>
        Quay lại Thư viện
      </button>

      <div className="glass-panel p-6 md:p-8 rounded-2xl border border-white/10 flex flex-col gap-6">
        <div className="relative h-64 md:h-80 rounded-xl overflow-hidden">
          <img
            src={disease.image_url}
            alt={disease.name}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent opacity-80" />
          <div className="absolute bottom-4 left-4 right-4 flex justify-between items-end">
            <div>
              <span className="text-xs font-semibold text-secondary">{disease.plant}</span>
              <h1 className="text-2xl md:text-3xl font-extrabold text-on-surface">{disease.name}</h1>
            </div>
            <span className="bg-error/20 border border-error text-error px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
              {disease.severity}
            </span>
          </div>
        </div>

        <div>
          <h3 className="text-base font-bold text-primary-container mb-2">Mô tả tổng quan</h3>
          <p className="text-sm text-on-surface-variant leading-relaxed">{disease.description}</p>
        </div>

        <div>
          <h3 className="text-base font-bold text-primary-container mb-3">Triệu chứng nhận biết</h3>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {disease.symptoms.map((sym, idx) => (
              <li key={idx} className="glass-panel p-3.5 rounded-xl flex items-start gap-2.5 text-xs text-on-surface">
                <span className="material-symbols-outlined text-primary-container text-base">warning</span>
                <span>{sym}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 pt-4 border-t border-outline-variant/30">
          <button
            onClick={onDiagnoseNow}
            className="flex-1 bg-primary-container text-on-primary font-bold py-3.5 rounded-xl text-sm flex items-center justify-center gap-2 hover:opacity-90 transition-all shadow-[0_0_15px_rgba(25,211,174,0.3)]"
          >
            <span className="material-symbols-outlined">add_a_photo</span>
            Chẩn đoán lá ngay
          </button>
        </div>
      </div>
    </div>
  );
};
