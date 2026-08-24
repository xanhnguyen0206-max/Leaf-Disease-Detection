import React, { useState, useRef } from 'react';
import { predictLeaf, saveLocalHistory } from '../services/api';
import { DiagnosisResult } from '../types';

interface DiagnosePageProps {
  onNavigate: (tab: string) => void;
}

export const DiagnosePage: React.FC<DiagnosePageProps> = ({ onNavigate }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<DiagnosisResult | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setErrorMsg(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setErrorMsg(null);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setIsAnalyzing(true);
    setErrorMsg(null);

    try {
      const diagnosis = await predictLeaf(selectedFile);
      setResult(diagnosis);
      await saveLocalHistory(diagnosis);
    } catch (err: any) {
      setErrorMsg(err.message || 'Phân tích thất bại, vui lòng thử lại.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const clearImage = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setErrorMsg(null);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 md:px-8 py-8 pb-24 md:pb-12 flex flex-col gap-8">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl md:text-4xl font-extrabold text-on-surface">Chẩn đoán cây của bạn</h1>
        <p className="text-on-surface-variant text-sm md:text-base">
          Tải lên hình ảnh rõ nét của lá cây bị bệnh để AI quét và phát hiện tác nhân gây bệnh.
        </p>
      </header>

      {/* Upload Dropzone */}
      {!previewUrl && (
        <section className="flex flex-col gap-4">
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className="w-full aspect-[4/3] md:aspect-[21/9] rounded-2xl border-2 border-dashed border-outline-variant hover:border-primary-container transition-colors duration-300 flex flex-col items-center justify-center gap-4 bg-surface-container-low cursor-pointer p-6 group"
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              accept="image/*"
              className="hidden"
            />
            <div className="p-4 rounded-full bg-surface-container-high group-hover:scale-110 transition-transform duration-300 text-primary-container">
              <span className="material-symbols-outlined text-4xl">add_a_photo</span>
            </div>
            <div className="text-center">
              <p className="font-semibold text-on-surface mb-1">
                Kéo thả ảnh lá vào đây hoặc nhấp để chọn file
              </p>
              <p className="text-xs text-on-surface-variant">Hỗ trợ JPG, PNG, WEBP lên tới 10MB</p>
            </div>
          </div>

          <div className="flex gap-4">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="flex-1 bg-primary-container text-on-primary font-bold py-3.5 rounded-xl flex items-center justify-center gap-2 hover:opacity-90 transition-all text-sm shadow-[0_0_15px_rgba(25,211,174,0.3)]"
            >
              <span className="material-symbols-outlined">upload_file</span>
              Tải ảnh từ thiết bị
            </button>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="flex-1 border border-primary-container text-primary-container font-semibold py-3.5 rounded-xl flex items-center justify-center gap-2 hover:bg-primary-container/10 transition-all text-sm"
            >
              <span className="material-symbols-outlined">photo_camera</span>
              Chụp ảnh trực tiếp
            </button>
          </div>
        </section>
      )}

      {/* Image Preview & Scanning Overlay */}
      {previewUrl && (
        <section className="flex flex-col gap-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold text-on-surface">Xem trước hình ảnh</h2>
            <button
              onClick={clearImage}
              disabled={isAnalyzing}
              className="text-xs text-error hover:underline flex items-center gap-1"
            >
              <span className="material-symbols-outlined text-sm">delete</span>
              Đổi ảnh khác
            </button>
          </div>

          <div className="relative rounded-2xl overflow-hidden glass-panel aspect-[4/3] md:aspect-[21/9] flex items-center justify-center border border-white/10">
            <img
              src={previewUrl}
              alt="Leaf Preview"
              className="w-full h-full object-cover"
            />

            {/* Scanning Line Animation */}
            {isAnalyzing && (
              <>
                <div className="absolute inset-0 bg-primary-container/10 backdrop-blur-[2px]" />
                <div className="absolute left-0 w-full h-1 bg-primary-container shadow-[0_0_20px_#19d3ae] scanner-line z-10" />
                <div className="absolute top-4 left-4 glass-panel rounded-full px-4 py-2 flex items-center gap-2 border border-primary-container/50">
                  <div className="w-2.5 h-2.5 rounded-full bg-primary-container glow-pulse" />
                  <span className="text-xs font-semibold text-primary-container uppercase tracking-wider">
                    ĐANG PHÂN TÍCH MẪU LÁ...
                  </span>
                </div>
              </>
            )}
          </div>

          {!result && !isAnalyzing && (
            <button
              onClick={handleAnalyze}
              className="w-full bg-primary-container text-on-primary font-bold py-4 rounded-xl flex items-center justify-center gap-2 hover:opacity-90 transition-all text-base shadow-[0_0_20px_rgba(25,211,174,0.3)]"
            >
              <span className="material-symbols-outlined">analytics</span>
              Bắt đầu phân tích bệnh
            </button>
          )}
        </section>
      )}

      {/* Error state */}
      {errorMsg && (
        <div className="p-4 rounded-xl bg-error/10 border border-error/30 text-error text-sm flex items-center gap-2">
          <span className="material-symbols-outlined">warning</span>
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Diagnosis Result Card */}
      {result && (
        <section className="glass-panel p-6 rounded-2xl flex flex-col md:flex-row gap-6 items-start md:items-center border border-primary-container/40 emerald-glow">
          {/* SVG Confidence Circle */}
          <div className="relative w-28 h-28 shrink-0 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
              <circle
                className="text-surface-container-highest"
                cx="50" cy="50" r="42"
                fill="none" stroke="currentColor" strokeWidth="8"
              />
              <circle
                className="text-primary-container transition-all duration-1000"
                cx="50" cy="50" r="42"
                fill="none" stroke="currentColor" strokeWidth="8"
                strokeDasharray="263.8"
                strokeDashoffset={263.8 * (1 - result.confidence)}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
              <span className="text-xl font-extrabold text-primary-container leading-none">
                {Math.round(result.confidence * 100)}%
              </span>
              <span className="text-[10px] text-on-surface-variant font-semibold">ĐỘ TIN CẬY</span>
            </div>
          </div>

          {/* Details */}
          <div className="flex-grow flex flex-col gap-2">
            <div className="flex items-center gap-3 flex-wrap">
              <h3 className="text-xl font-bold text-on-surface">{result.disease}</h3>
              <span className="px-3 py-1 rounded-full bg-error/10 text-error border border-error/20 text-xs font-semibold uppercase tracking-wider">
                {result.severity}
              </span>
            </div>
            <p className="text-sm text-on-surface-variant">
              Cây trồng: <strong className="text-on-surface">{result.plant}</strong>. Phát hiện tác nhân gây bệnh với mức độ ảnh hưởng {result.severity.toLowerCase()}.
            </p>

            {/* Recommendations */}
            <div className="mt-3 flex flex-col gap-2">
              <h4 className="text-xs font-bold uppercase text-primary-container tracking-wider">Phác đồ đề xuất:</h4>
              <ul className="flex flex-col gap-1.5 text-xs text-on-surface">
                {result.recommendations?.map((rec, idx) => (
                  <li key={idx} className="flex items-start gap-2 glass-panel p-2 rounded-lg">
                    <span className="material-symbols-outlined text-primary-container text-sm mt-0.5">check_circle</span>
                    <div>
                      <strong className="text-primary-container">{rec.title}: </strong>
                      <span className="text-on-surface-variant">{rec.description}</span>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <button
            onClick={() => onNavigate('history')}
            className="w-full md:w-auto bg-transparent border border-primary-container text-primary-container font-semibold px-5 py-3 rounded-xl hover:bg-primary-container/10 transition-all text-xs whitespace-nowrap"
          >
            Xem lịch sử chẩn đoán
          </button>
        </section>
      )}
    </div>
  );
};
