import React, { useEffect, useState } from 'react';
import { fetchHistory, deleteHistoryItem } from '../services/api';
import { DiagnosisResult } from '../types';

export const HistoryPage: React.FC = () => {
  const [history, setHistory] = useState<DiagnosisResult[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await fetchHistory();
      setHistory(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    await deleteHistoryItem(id);
    setHistory((prev) => prev.filter((item) => item.id !== id));
  };

  return (
    <div className="max-w-5xl mx-auto px-4 md:px-8 py-8 pb-24 md:pb-12 flex flex-col gap-8">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl md:text-4xl font-extrabold text-on-surface">Lịch sử chẩn đoán</h1>
        <p className="text-on-surface-variant text-sm md:text-base">
          Xem lại danh sách các mẫu lá đã chẩn đoán và theo dõi diễn biến sức khỏe cây trồng.
        </p>
      </header>

      {loading ? (
        <div className="py-16 text-center text-on-surface-variant flex items-center justify-center gap-2">
          <span className="material-symbols-outlined animate-spin text-primary-container">sync</span>
          Đang tải lịch sử...
        </div>
      ) : history.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-2xl flex flex-col items-center gap-4">
          <span className="material-symbols-outlined text-5xl text-on-surface-variant">history</span>
          <p className="text-on-surface font-semibold">Chưa có lịch sử chẩn đoán nào</p>
          <p className="text-xs text-on-surface-variant max-w-sm">
            Tải lên ảnh lá cây ở mục "Chẩn đoán" để lưu kết quả phân tích vào lịch sử của bạn.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {history.map((item) => (
            <div
              key={item.id}
              className="glass-panel p-5 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border border-white/5 hover:border-primary-container/30 transition-all"
            >
              <div className="flex items-center gap-4">
                {item.image_url && (
                  <img
                    src={item.image_url}
                    alt={item.disease}
                    className="w-16 h-16 rounded-xl object-cover border border-white/10"
                  />
                )}
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-secondary">{item.plant}</span>
                    <span className="text-[10px] text-on-surface-variant">• {new Date(item.created_at).toLocaleDateString('vi-VN')}</span>
                  </div>
                  <h3 className="text-base font-bold text-on-surface mt-0.5">{item.disease}</h3>
                  <p className="text-xs text-primary-container font-semibold mt-1">
                    Độ tin cậy: {Math.round(item.confidence * 100)}%
                  </p>
                </div>
              </div>

              <button
                onClick={() => handleDelete(item.id)}
                className="text-xs text-error/80 hover:text-error hover:bg-error/10 px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1"
              >
                <span className="material-symbols-outlined text-sm">delete</span>
                Xóa bản ghi
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
