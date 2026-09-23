import React, { useState, useRef } from 'react';
import { predictImage } from '../services/api';
import { DiagnosisResult, DetectionItem, DetectedDiseaseGroup } from '../types';

interface DiagnosePageProps {
  onNavigate: (tab: string) => void;
  onSelectDisease?: (diseaseId: string) => void;
}

// Disease-specific visual palettes
const DISEASE_COLOR_PALETTES: Record<string, {
  border: string;
  bg: string;
  badge: string;
  text: string;
  hex: string;
}> = {
  Tomato___Bacterial_spot: {
    border: 'border-red-500',
    bg: 'bg-red-500/20',
    badge: 'bg-red-600 border-red-400',
    text: 'text-red-400',
    hex: '#ef4444',
  },
  Tomato___Early_blight: {
    border: 'border-amber-500',
    bg: 'bg-amber-500/20',
    badge: 'bg-amber-600 border-amber-400',
    text: 'text-amber-400',
    hex: '#f59e0b',
  },
  Tomato___Late_blight: {
    border: 'border-purple-500',
    bg: 'bg-purple-500/20',
    badge: 'bg-purple-600 border-purple-400',
    text: 'text-purple-400',
    hex: '#a855f7',
  },
  Tomato___Septoria_leaf_spot: {
    border: 'border-emerald-500',
    bg: 'bg-emerald-500/20',
    badge: 'bg-emerald-600 border-emerald-400',
    text: 'text-emerald-400',
    hex: '#10b981',
  },
  Tomato___Leaf_mold: {
    border: 'border-yellow-500',
    bg: 'bg-yellow-500/20',
    badge: 'bg-yellow-600 border-yellow-400',
    text: 'text-yellow-400',
    hex: '#eab308',
  },
  Tomato___Powdery_mildew: {
    border: 'border-slate-400',
    bg: 'bg-slate-400/20',
    badge: 'bg-slate-500 border-slate-300',
    text: 'text-slate-300',
    hex: '#94a3b8',
  },
};

const DEFAULT_PALETTE = {
  border: 'border-cyan-400',
  bg: 'bg-cyan-500/20',
  badge: 'bg-cyan-600 border-cyan-400',
  text: 'text-cyan-400',
  hex: '#06b6d4',
};

export const DiagnosePage: React.FC<DiagnosePageProps> = ({ onNavigate, onSelectDisease }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [result, setResult] = useState<DiagnosisResult | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [naturalSize, setNaturalSize] = useState<{ width: number; height: number }>({ width: 0, height: 0 });

  // Interactive highlighting states
  const [hoveredDetIndex, setHoveredDetIndex] = useState<number | null>(null);
  const [highlightedDisease, setHighlightedDisease] = useState<string | null>(null);

  // Live camera stream state
  const [isCameraOpen, setIsCameraOpen] = useState<boolean>(false);
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const cameraInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setErrorMsg(null);
      setNaturalSize({ width: 0, height: 0 });
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setResult(null);
      setErrorMsg(null);
      setNaturalSize({ width: 0, height: 0 });
    }
  };

  const clearImage = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setErrorMsg(null);
    setNaturalSize({ width: 0, height: 0 });
    setHoveredDetIndex(null);
    setHighlightedDisease(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (cameraInputRef.current) cameraInputRef.current.value = '';
    closeCamera();
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setIsAnalyzing(true);
    setErrorMsg(null);
    try {
      const diagnosis = await predictImage(selectedFile);
      setResult(diagnosis);
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err?.response?.data?.detail || 'Không thể kết nối đến máy chủ phân tích hoặc ảnh không hợp lệ.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const openCamera = async () => {
    try {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } }
        });
        setCameraStream(stream);
        setIsCameraOpen(true);
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } else {
        cameraInputRef.current?.click();
      }
    } catch (err) {
      console.warn('Cannot open webcam, falling back to file picker:', err);
      cameraInputRef.current?.click();
    }
  };

  const closeCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach((track) => track.stop());
      setCameraStream(null);
    }
    setIsCameraOpen(false);
  };

  const capturePhoto = () => {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], `camera_capture_${Date.now()}.jpg`, { type: 'image/jpeg' });
          setSelectedFile(file);
          setPreviewUrl(URL.createObjectURL(file));
          setResult(null);
          setErrorMsg(null);
          setNaturalSize({ width: 0, height: 0 });
          closeCamera();
        }
      }, 'image/jpeg', 0.95);
    }
  };

  const isNoDetection = result?.status === 'no_detection' || (result && (!result.detections || result.detections.length === 0) && result.primary_disease === 'Healthy');

  const getPalette = (diseaseName: string) => {
    return DISEASE_COLOR_PALETTES[diseaseName] || DEFAULT_PALETTE;
  };

  // Group detections if result lacks pre-grouped list
  const detectedGroups: DetectedDiseaseGroup[] = result?.detected_diseases || [];
  const primaryGroup = detectedGroups.length > 0 ? detectedGroups[0] : null;
  const additionalGroups = detectedGroups.length > 1 ? detectedGroups.slice(1) : [];

  return (
    <div className="max-w-4xl mx-auto px-4 md:px-8 py-8 pb-24 md:pb-12 flex flex-col gap-8">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl md:text-4xl font-extrabold text-on-surface">Chẩn đoán bệnh cây trồng</h1>
        <p className="text-on-surface-variant text-sm md:text-base">
          Tải lên hoặc chụp ảnh lá cây để mô hình YOLO AI tự động phát hiện, khoanh vùng đa tổn thương và đề xuất phác đồ điều trị.
        </p>
      </header>

      {/* Upload Dropzone (idle state) */}
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
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
            />
            <input
              type="file"
              ref={cameraInputRef}
              onChange={handleFileSelect}
              accept="image/*"
              capture="environment"
              className="hidden"
            />
            <div className="p-4 rounded-full bg-surface-container-high group-hover:scale-110 transition-transform duration-300 text-primary-container">
              <span className="material-symbols-outlined text-4xl">add_a_photo</span>
            </div>
            <div className="text-center">
              <p className="font-semibold text-on-surface mb-1">
                Kéo thả ảnh lá vào đây hoặc nhấp để chọn file
              </p>
              <p className="text-xs text-on-surface-variant">Hỗ trợ định dạng JPG, PNG, WEBP lên tới 10MB</p>
            </div>
          </div>

          <div className="flex gap-4 flex-col sm:flex-row">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="flex-1 bg-primary-container text-on-primary font-bold py-3.5 rounded-xl flex items-center justify-center gap-2 hover:opacity-90 transition-all text-sm shadow-[0_0_15px_rgba(25,211,174,0.3)]"
            >
              <span className="material-symbols-outlined">upload_file</span>
              Tải ảnh từ thiết bị
            </button>
            <button
              onClick={openCamera}
              className="flex-1 border border-primary-container text-primary-container font-semibold py-3.5 rounded-xl flex items-center justify-center gap-2 hover:bg-primary-container/10 transition-all text-sm"
            >
              <span className="material-symbols-outlined">photo_camera</span>
              Chụp ảnh trực tiếp
            </button>
          </div>
        </section>
      )}

      {/* Live Camera Viewfinder Modal */}
      {isCameraOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-lg rounded-2xl overflow-hidden flex flex-col gap-4 p-5 border border-primary-container/30">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-bold text-on-surface flex items-center gap-2">
                <span className="material-symbols-outlined text-primary-container">videocam</span>
                Chụp ảnh mẫu lá
              </h3>
              <button
                onClick={closeCamera}
                className="text-on-surface-variant hover:text-on-surface"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            <div className="relative rounded-xl overflow-hidden aspect-[4/3] bg-black flex items-center justify-center border border-white/10">
              <video
                ref={(el) => {
                  videoRef.current = el;
                  if (el && cameraStream && el.srcObject !== cameraStream) {
                    el.srcObject = cameraStream;
                    el.play().catch(() => {});
                  }
                }}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-4 border border-dashed border-primary-container/40 rounded-lg pointer-events-none" />
            </div>

            <div className="flex gap-3">
              <button
                onClick={capturePhoto}
                className="flex-1 bg-primary-container text-on-primary font-bold py-3 rounded-xl flex items-center justify-center gap-2 hover:opacity-90 transition-all text-sm shadow-[0_0_15px_rgba(25,211,174,0.3)]"
              >
                <span className="material-symbols-outlined">camera</span>
                Chụp hình ngay
              </button>
              <button
                onClick={closeCamera}
                className="px-5 py-3 rounded-xl border border-white/20 text-on-surface-variant hover:bg-white/5 transition-all text-sm"
              >
                Hủy
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Image Preview, Scanning Animation, & YOLO Bounding Box Overlay */}
      {previewUrl && (
        <section className="flex flex-col gap-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold text-on-surface">Mẫu lá chẩn đoán</h2>
            <button
              onClick={clearImage}
              disabled={isAnalyzing}
              className="text-xs text-error hover:underline flex items-center gap-1 disabled:opacity-50"
            >
              <span className="material-symbols-outlined text-sm">delete</span>
              Đổi ảnh khác
            </button>
          </div>

          <div className="glass-panel p-3 rounded-2xl flex flex-col items-center justify-center border border-white/10 overflow-hidden">
            {/* Wrapper exactly conforming to rendered image size */}
            <div className="relative inline-block max-w-full rounded-xl overflow-hidden">
              <img
                src={previewUrl}
                alt="Leaf Preview"
                onLoad={(e) => {
                  setNaturalSize({
                    width: e.currentTarget.naturalWidth,
                    height: e.currentTarget.naturalHeight,
                  });
                }}
                className="max-h-[460px] w-auto max-w-full block object-contain mx-auto rounded-xl"
              />

              {/* Scanning Animation */}
              {isAnalyzing && (
                <>
                  <div className="absolute inset-0 bg-primary-container/15 backdrop-blur-[1px]" />
                  <div className="absolute left-0 w-full h-1 bg-primary-container shadow-[0_0_20px_#19d3ae] scanner-line z-10" />
                  <div className="absolute top-4 left-4 glass-panel rounded-full px-4 py-2 flex items-center gap-2 border border-primary-container/50 z-20">
                    <div className="w-2.5 h-2.5 rounded-full bg-primary-container glow-pulse" />
                    <span className="text-xs font-semibold text-primary-container uppercase tracking-wider">
                      ĐANG PHÂN TÍCH MẪU LÁ VỚI YOLO...
                    </span>
                  </div>
                </>
              )}

              {/* Scaled YOLO Bounding Boxes Overlay */}
              {!isAnalyzing && result && result.detections && result.detections.length > 0 && naturalSize.width > 0 && naturalSize.height > 0 && (
                <div className="absolute inset-0 pointer-events-none">
                  {result.detections.map((det: DetectionItem, idx: number) => {
                    const palette = getPalette(det.disease);
                    const leftPct = (det.bbox.x1 / naturalSize.width) * 100;
                    const topPct = (det.bbox.y1 / naturalSize.height) * 100;
                    const widthPct = ((det.bbox.x2 - det.bbox.x1) / naturalSize.width) * 100;
                    const heightPct = ((det.bbox.y2 - det.bbox.y1) / naturalSize.height) * 100;

                    const isBoxHovered = hoveredDetIndex === idx;
                    const isGroupHighlighted = highlightedDisease === det.disease;

                    return (
                      <div
                        key={idx}
                        style={{
                          left: `${Math.max(0, leftPct)}%`,
                          top: `${Math.max(0, topPct)}%`,
                          width: `${Math.min(100 - leftPct, widthPct)}%`,
                          height: `${Math.min(100 - topPct, heightPct)}%`,
                        }}
                        onMouseEnter={() => setHoveredDetIndex(idx)}
                        onMouseLeave={() => setHoveredDetIndex(null)}
                        className={`absolute border-2 ${palette.border} ${palette.bg} rounded-md transition-all pointer-events-auto cursor-pointer ${
                          isBoxHovered || isGroupHighlighted
                            ? 'ring-4 ring-white/60 scale-[1.02] z-30 shadow-lg'
                            : 'z-20 opacity-85 hover:opacity-100'
                        }`}
                      >
                        {/* Detection label tag */}
                        <div
                          className={`absolute -top-6 left-0 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider text-white border whitespace-nowrap shadow-md ${palette.badge}`}
                        >
                          #{idx + 1} {det.disease.replace('Tomato___', '').replace(/_/g, ' ')} ({Math.round(det.confidence * 100)}%)
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Bounding Box Legends Grouped by Disease Class */}
            {!isAnalyzing && result && result.detections && result.detections.length > 0 && (
              <div className="w-full mt-3 pt-3 border-t border-white/10 flex flex-col gap-2">
                <div className="flex items-center justify-between flex-wrap gap-2 text-xs">
                  <span className="text-on-surface-variant font-semibold">
                    Tổng số vùng tổn thương phát hiện: <strong className="text-on-surface">{result.detections.length}</strong>
                  </span>
                  <span className="text-[11px] text-on-surface-variant">
                    (Rê chuột vào nhãn bên dưới để làm nổi bật vùng trên ảnh)
                  </span>
                </div>

                <div className="flex flex-wrap gap-2">
                  {detectedGroups.map((group, gIdx) => {
                    const palette = getPalette(group.disease);
                    const isSelected = highlightedDisease === group.disease;

                    return (
                      <button
                        key={gIdx}
                        onMouseEnter={() => setHighlightedDisease(group.disease)}
                        onMouseLeave={() => setHighlightedDisease(null)}
                        onClick={() => setHighlightedDisease(isSelected ? null : group.disease)}
                        className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                          isSelected ? 'scale-105 ring-2 ring-white shadow-md' : 'opacity-90 hover:opacity-100'
                        } ${palette.badge} text-white`}
                      >
                        <span className="w-2.5 h-2.5 rounded-full bg-white inline-block shadow-sm" />
                        <span>{group.disease_name}</span>
                        <span className="bg-black/30 px-1.5 py-0.2 rounded-full text-[10px]">
                          {group.detection_count} vùng ({Math.round(group.max_confidence * 100)}%)
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
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
        <div className="p-4 rounded-xl bg-error/10 border border-error/30 text-error text-sm flex items-start gap-3">
          <span className="material-symbols-outlined text-lg mt-0.5 shrink-0">error</span>
          <div className="flex flex-col gap-1">
            <strong className="font-semibold">Lỗi phân tích</strong>
            <span>{errorMsg}</span>
          </div>
        </div>
      )}

      {/* No Detection State Card */}
      {result && isNoDetection && (
        <section className="glass-panel p-6 rounded-2xl flex flex-col gap-5 border border-emerald-500/30">
          <div className="flex flex-col md:flex-row gap-6 items-start md:items-center">
            <div className="relative w-20 h-20 shrink-0 flex items-center justify-center rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
              <span className="material-symbols-outlined text-4xl">task_alt</span>
            </div>

            <div className="flex-grow flex flex-col gap-2">
              <div className="flex items-center gap-3 flex-wrap">
                <h3 className="text-xl font-bold text-emerald-400">Không phát hiện vùng bệnh phù hợp</h3>
                <span className="px-3 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-semibold uppercase tracking-wider">
                  Chưa phát hiện bệnh
                </span>
              </div>
              <p className="text-sm text-on-surface-variant leading-relaxed">
                Mẫu lá không biểu hiện dấu hiệu bệnh thuộc các lớp mô hình YOLO hiện tại được huấn luyện (Đốm vi khuẩn, Úa sớm, Sương mai). 
                Cây vẫn có thể gặp vấn đề dinh dưỡng, rễ hoặc các bệnh ngoài phạm vi nhận diện.
              </p>
            </div>
          </div>

          {/* Recommendations */}
          {result.recommendations && result.recommendations.length > 0 && (
            <div className="pt-3 border-t border-outline-variant/20 flex flex-col gap-2">
              <h4 className="text-xs font-bold uppercase text-primary-container tracking-wider flex items-center gap-1.5">
                <span className="material-symbols-outlined text-sm">health_and_safety</span>
                Khuyến nghị theo dõi & chăm sóc:
              </h4>
              <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {result.recommendations.map((rec, idx) => (
                  <li key={idx} className="glass-panel p-3 rounded-xl flex items-start gap-2.5 text-xs text-on-surface border border-white/5">
                    <span className="material-symbols-outlined text-emerald-400 text-base mt-0.5 shrink-0">verified</span>
                    <div>
                      <strong className="text-emerald-300 block mb-0.5">{rec.title}</strong>
                      <span className="text-on-surface-variant leading-relaxed">{rec.description}</span>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-3 pt-2">
            <button
              onClick={() => onNavigate('care')}
              className="flex-1 bg-transparent border border-primary-container text-primary-container font-semibold py-2.5 rounded-xl hover:bg-primary-container/10 transition-all text-xs flex items-center justify-center gap-1.5"
            >
              <span className="material-symbols-outlined text-sm">menu_book</span>
              Xem sổ tay chăm sóc & IPM
            </button>
            <button
              onClick={clearImage}
              className="flex-1 bg-surface-container-high text-on-surface font-semibold py-2.5 rounded-xl hover:bg-surface-variant transition-all text-xs flex items-center justify-center gap-1.5"
            >
              <span className="material-symbols-outlined text-sm">add_photo_alternate</span>
              Chụp / Tải ảnh khác
            </button>
          </div>
        </section>
      )}

      {/* Multi-Disease Alert Banner */}
      {result && !isNoDetection && (result.is_multi_disease || additionalGroups.length > 0) && (
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 flex items-start gap-3 shadow-lg">
          <span className="material-symbols-outlined text-xl mt-0.5 text-amber-400 shrink-0">warning</span>
          <div className="flex flex-col gap-1 text-xs md:text-sm">
            <strong className="font-bold text-amber-400 text-sm">
              Cảnh báo đa bệnh: Mẫu lá có dấu hiệu đồng nhiễm của {detectedGroups.length} nhóm bệnh khác nhau!
            </strong>
            <p className="text-amber-200/90 leading-relaxed">
              Mô hình phát hiện dấu hiệu của nhiều tác nhân gây bệnh trên cùng một mẫu lá. 
              Kết quả dưới đây được phân loại thành <strong>Bệnh chẩn đoán chính</strong> và <strong>Các bệnh được phát hiện thêm</strong> theo mức độ bằng chứng và độ tin cậy.
            </p>
          </div>
        </div>
      )}

      {/* AI Fallback Status Banner */}
      {result && result.fallback_used && (
        <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 flex items-start gap-3 shadow-lg mb-4">
          <span className="material-symbols-outlined text-xl mt-0.5 text-indigo-400 shrink-0">psychology</span>
          <div className="flex flex-col gap-1 text-xs md:text-sm">
            <strong className="font-bold text-indigo-400 text-sm">
              AI Hỗ trợ xác minh (Second Opinion)
            </strong>
            <p className="text-indigo-200/90 leading-relaxed">
              Mô hình YOLO có độ tin cậy thấp nên hệ thống đã tự động kích hoạt AI để hỗ trợ xác minh. 
              Kết quả dưới đây có sự đóng góp của đánh giá độc lập từ AI.
            </p>
          </div>
        </div>
      )}

      {/* Primary Disease Card */}
      {result && !isNoDetection && primaryGroup && (
        <section className="glass-panel p-6 rounded-2xl flex flex-col gap-6 border border-primary-container/40 emerald-glow">
          <div className="flex flex-col md:flex-row gap-6 items-start md:items-center">
            {/* SVG Confidence Circle */}
            <div className="relative w-28 h-28 shrink-0 flex items-center justify-center mx-auto md:mx-0">
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
                  strokeDashoffset={263.8 * (1 - primaryGroup.max_confidence)}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                <span className="text-xl font-extrabold text-primary-container leading-none">
                  {Math.round(primaryGroup.max_confidence * 100)}%
                </span>
                <span className="text-[9px] text-on-surface-variant font-semibold mt-0.5">ĐỘ TIN CẬY</span>
              </div>
            </div>

            {/* Details */}
            <div className="flex-grow flex flex-col gap-2 text-center md:text-left">
              <div className="flex items-center gap-2.5 flex-wrap justify-center md:justify-start">
                <span className="text-xs uppercase font-bold tracking-wider text-primary-container bg-primary-container/10 px-2.5 py-0.5 rounded-full border border-primary-container/20">
                  Bệnh chẩn đoán chính
                </span>
                <span className="px-2.5 py-0.5 rounded-full bg-error/10 text-error border border-error/20 text-xs font-semibold">
                  Mức độ: {primaryGroup.severity}
                </span>
                <span className="px-2.5 py-0.5 rounded-full bg-surface-variant text-on-surface text-xs font-semibold">
                  {primaryGroup.confidence_level}
                </span>
                <span className="px-2.5 py-0.5 rounded-full bg-primary-container/15 text-primary-container border border-primary-container/30 text-xs font-semibold">
                  {primaryGroup.detection_count} vùng tổn thương
                </span>
              </div>

              <h3 className="text-2xl font-extrabold text-on-surface mt-1">{primaryGroup.disease_name}</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Cây trồng: <strong className="text-on-surface">{primaryGroup.plant}</strong>. {primaryGroup.description}
              </p>
            </div>
          </div>

          {/* Key Symptoms */}
          {primaryGroup.symptoms && primaryGroup.symptoms.length > 0 && (
            <div className="pt-4 border-t border-outline-variant/20">
              <h4 className="text-xs font-bold uppercase text-primary-container tracking-wider mb-2 flex items-center gap-1.5">
                <span className="material-symbols-outlined text-sm">symptoms</span>
                Triệu chứng nhận diện chính:
              </h4>
              <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {primaryGroup.symptoms.map((sym, sIdx) => (
                  <li key={sIdx} className="glass-panel p-2.5 rounded-lg flex items-start gap-2 text-xs text-on-surface border border-white/5">
                    <span className="material-symbols-outlined text-primary-container text-sm mt-0.5 shrink-0">check</span>
                    <span>{sym}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {primaryGroup.recommendations && primaryGroup.recommendations.length > 0 && (
            <div className="pt-2">
              <h4 className="text-xs font-bold uppercase text-primary-container tracking-wider mb-2 flex items-center gap-1.5">
                <span className="material-symbols-outlined text-sm">medical_services</span>
                Phác đồ điều trị đề xuất:
              </h4>
              <ul className="flex flex-col gap-2 text-xs text-on-surface">
                {primaryGroup.recommendations.map((rec, idx) => (
                  <li key={idx} className="glass-panel p-3 rounded-xl flex items-start gap-2.5 border border-white/5">
                    <span className="material-symbols-outlined text-primary-container text-base mt-0.5 shrink-0">check_circle</span>
                    <div>
                      <strong className="text-primary-container block mb-0.5">{rec.title}</strong>
                      <span className="text-on-surface-variant leading-relaxed">{rec.description}</span>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Action Links */}
          <div className="flex flex-col sm:flex-row gap-3 pt-2 border-t border-outline-variant/20">
            {primaryGroup.disease_id && onSelectDisease && (
              <button
                onClick={() => onSelectDisease(primaryGroup.disease_id!)}
                className="flex-1 bg-primary-container text-on-primary font-bold py-3 rounded-xl text-xs flex items-center justify-center gap-1.5 hover:opacity-90 transition-all shadow-[0_0_15px_rgba(25,211,174,0.3)]"
              >
                <span className="material-symbols-outlined text-sm">library_books</span>
                Xem chi tiết bệnh trong Thư viện
              </button>
            )}
            <button
              onClick={() => onNavigate('care')}
              className="flex-1 bg-transparent border border-primary-container text-primary-container font-semibold py-3 rounded-xl hover:bg-primary-container/10 transition-all text-xs flex items-center justify-center gap-1.5"
            >
              <span className="material-symbols-outlined text-sm">spa</span>
              Xem phác đồ IPM & Chăm sóc
            </button>
          </div>
        </section>
      )}

      {/* Additional Detected Diseases Section */}
      {result && !isNoDetection && additionalGroups.length > 0 && (
        <section className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-on-surface flex items-center gap-2">
              <span className="material-symbols-outlined text-amber-400">checklist</span>
              Các bệnh khác được phát hiện thêm ({additionalGroups.length})
            </h3>
            <span className="text-xs text-on-surface-variant">Sắp xếp theo mức độ tin cậy</span>
          </div>

          <div className="grid grid-cols-1 gap-4">
            {additionalGroups.map((group, idx) => {
              const palette = getPalette(group.disease);

              return (
                <article
                  key={idx}
                  className="glass-panel p-5 rounded-2xl border border-outline-variant/40 flex flex-col gap-4 hover:border-outline transition-all"
                >
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                    <div>
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${palette.badge} text-white`}>
                          #{idx + 2} {group.disease_name}
                        </span>
                        <span className="text-xs font-semibold text-secondary">{group.plant}</span>
                        <span className="text-xs px-2 py-0.5 rounded bg-surface-variant text-on-surface-variant">
                          {group.confidence_level}
                        </span>
                      </div>
                      <h4 className="text-base font-bold text-on-surface">{group.disease_name}</h4>
                    </div>

                    <div className="flex items-center gap-3 self-end sm:self-center">
                      <div className="text-right">
                        <div className="text-lg font-extrabold text-on-surface leading-none">
                          {Math.round(group.max_confidence * 100)}%
                        </div>
                        <span className="text-[10px] text-on-surface-variant font-medium">
                          {group.detection_count} vùng tổn thương
                        </span>
                      </div>
                    </div>
                  </div>

                  <p className="text-xs text-on-surface-variant leading-relaxed">
                    {group.description}
                  </p>

                  {/* Symptoms & Recommendations preview */}
                  {group.recommendations && group.recommendations.length > 0 && (
                    <div className="bg-surface-container/60 p-3 rounded-xl flex flex-col gap-1.5 text-xs">
                      <strong className="text-primary-container font-semibold">Khuyến nghị xử lý:</strong>
                      <p className="text-on-surface-variant">
                        {group.recommendations[0].title}: {group.recommendations[0].description}
                      </p>
                    </div>
                  )}

                  <div className="flex justify-end gap-2 pt-2 border-t border-outline-variant/20">
                    {group.disease_id && onSelectDisease && (
                      <button
                        onClick={() => onSelectDisease(group.disease_id!)}
                        className="bg-transparent border border-primary-container/60 text-primary-container font-semibold px-4 py-2 rounded-xl text-xs flex items-center gap-1 hover:bg-primary-container/10 transition-all"
                      >
                        Xem hướng dẫn điều trị bệnh này
                        <span className="material-symbols-outlined text-xs">arrow_forward</span>
                      </button>
                    )}
                  </div>
                </article>
              );
            })}
          </div>
        </section>
      )}
    </div>
  );
};
