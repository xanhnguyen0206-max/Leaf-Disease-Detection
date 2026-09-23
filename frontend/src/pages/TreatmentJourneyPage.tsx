import React, { useEffect, useState } from 'react';
import { fetchTreatmentPlan, updateTreatmentStepProgress, submitTreatmentFeedback, fetchHistory } from '../services/api';
import { TreatmentPlan, DiagnosisResult, TreatmentFeedbackCreate } from '../types';

interface Props {
  diagnosisId: string;
  onBack: () => void;
}

export const TreatmentJourneyPage: React.FC<Props> = ({ diagnosisId, onBack }) => {
  const [plan, setPlan] = useState<TreatmentPlan | null>(null);
  const [diagnosis, setDiagnosis] = useState<DiagnosisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [feedbackEffectiveness, setFeedbackEffectiveness] = useState<number>(0);
  const [feedbackComment, setFeedbackComment] = useState('');
  const [submittingFeedback, setSubmittingFeedback] = useState(false);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  useEffect(() => {
    loadData();
  }, [diagnosisId]);

  const loadData = async () => {
    setLoading(true);
    try {
      // We load the plan
      const planData = await fetchTreatmentPlan(diagnosisId);
      setPlan(planData);
      
      // Also load history to get image and confidence
      // In a real app we'd have a separate endpoint /api/history/{id}
      const historyList = await fetchHistory();
      const diag = historyList.find(h => h.id === diagnosisId);
      if (diag) setDiagnosis(diag);
      
    } catch (err: any) {
      setError(err.message || 'Lỗi khi tải lộ trình.');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleStep = async (stepId: string, currentCompleted: boolean) => {
    if (!plan) return;
    try {
      await updateTreatmentStepProgress(plan.id, stepId, !currentCompleted);
      // Reload plan to get updated progress and status
      const updatedPlan = await fetchTreatmentPlan(diagnosisId);
      setPlan(updatedPlan);
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleSubmitFeedback = async () => {
    if (!plan) return;
    setSubmittingFeedback(true);
    try {
      const feedback: TreatmentFeedbackCreate = {
        effectiveness_percent: feedbackEffectiveness,
        comment: feedbackComment || undefined
      };
      await submitTreatmentFeedback(plan.id, feedback);
      setFeedbackSubmitted(true);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setSubmittingFeedback(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8 text-center text-on-surface-variant flex items-center justify-center gap-2">
        <span className="material-symbols-outlined animate-spin text-primary-container">sync</span>
        Đang tải lộ trình chăm sóc...
      </div>
    );
  }

  if (error || !plan) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <button onClick={onBack} className="flex items-center gap-2 text-on-surface-variant hover:text-primary mb-6 transition-colors">
          <span className="material-symbols-outlined">arrow_back</span>
          <span>Quay lại lịch sử</span>
        </button>
        <div className="glass-panel p-8 rounded-2xl text-center flex flex-col items-center gap-4">
          <span className="material-symbols-outlined text-4xl text-error">error</span>
          <p className="text-on-surface font-semibold">{error || 'Không tìm thấy lộ trình cho chẩn đoán này.'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 pb-24 flex flex-col gap-8">
      {/* HEADER */}
      <button onClick={onBack} className="flex items-center gap-2 text-on-surface-variant hover:text-primary transition-colors self-start">
        <span className="material-symbols-outlined">arrow_back</span>
        <span className="font-medium">Quay lại lịch sử</span>
      </button>

      <header className="flex flex-col gap-2">
        <h1 className="text-3xl md:text-4xl font-extrabold text-on-surface leading-tight">
          Lộ trình xử lý bệnh
        </h1>
        <p className="text-on-surface-variant text-sm md:text-base">
          {diagnosis?.disease || 'Cà chua'}
        </p>
      </header>

      {/* DIAGNOSIS SUMMARY */}
      {diagnosis && (
        <div className="glass-panel p-5 rounded-2xl flex flex-col md:flex-row items-start md:items-center gap-4 border border-white/5">
          {diagnosis.image_url && (
            <img src={diagnosis.image_url} alt="Bệnh lá" className="w-24 h-24 rounded-xl object-cover border border-white/10 shrink-0" />
          )}
          <div className="flex-1">
            <div className="text-xs text-on-surface-variant mb-1 font-medium">
              Chẩn đoán lúc {new Date(diagnosis.created_at).toLocaleString('vi-VN')}
            </div>
            <h2 className="text-xl font-bold text-on-surface">{diagnosis.disease}</h2>
            <div className="text-sm font-semibold text-primary-container mt-1">
              Độ tin cậy: {Math.round(diagnosis.confidence * 100)}%
            </div>
          </div>
        </div>
      )}

      {/* PROGRESS */}
      {plan.progress && (
        <div className="glass-panel p-6 rounded-2xl border border-white/5 bg-surface-container-low flex flex-col gap-3">
          <div className="flex justify-between items-end">
            <div>
              <div className="text-sm font-medium text-on-surface-variant">Tiến độ thực hiện</div>
              <div className="text-xl font-bold text-on-surface">
                {plan.progress.completed} / {plan.progress.total} bước
              </div>
            </div>
            <div className="text-2xl font-extrabold text-primary-container">
              {Math.round(plan.progress.percentage)}%
            </div>
          </div>
          
          <div className="h-3 bg-surface-container rounded-full overflow-hidden w-full">
            <div 
              className="h-full bg-primary transition-all duration-500 ease-out"
              style={{ width: `${plan.progress.percentage}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* PHASES */}
      <div className="flex flex-col gap-6">
        {plan.phases.map(phase => (
          <div key={phase.id} className="flex flex-col gap-4">
            <h3 className="text-lg font-bold text-primary-container flex items-center gap-2">
              <span className="bg-primary/20 text-primary w-6 h-6 rounded-full flex items-center justify-center text-xs">
                {phase.sequence}
              </span>
              {phase.name.toUpperCase()}
            </h3>

            <div className="flex flex-col gap-3">
              {phase.steps.map(step => {
                const isCompleted = step.progress?.completed || false;
                
                return (
                  <div 
                    key={step.id} 
                    className={`glass-panel p-4 md:p-5 rounded-2xl border transition-all ${
                      isCompleted ? 'border-primary/50 bg-primary/5' : 'border-white/5 hover:border-white/20'
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      <button 
                        onClick={() => handleToggleStep(step.id, isCompleted)}
                        className={`w-6 h-6 shrink-0 rounded flex items-center justify-center transition-colors mt-0.5 ${
                          isCompleted 
                            ? 'bg-primary text-on-primary' 
                            : 'border-2 border-on-surface-variant hover:border-primary text-transparent'
                        }`}
                      >
                        <span className="material-symbols-outlined text-[18px]">check</span>
                      </button>

                      <div className="flex-1 flex flex-col gap-2">
                        <div>
                          <h4 className={`text-base font-bold ${isCompleted ? 'text-primary line-through opacity-70' : 'text-on-surface'}`}>
                            {step.title}
                          </h4>
                          {step.timing && (
                            <span className="inline-block px-2 py-0.5 rounded text-[10px] font-medium bg-surface-container-high text-secondary mt-1">
                              {step.timing === 'IMMEDIATE' ? 'Thực hiện ngay' : 
                               step.timing === 'DAILY' ? 'Hàng ngày' : 
                               step.timing === 'WEEKLY' ? 'Hàng tuần' : 
                               step.timing === 'CONDITIONAL' ? 'Tùy điều kiện' : step.timing}
                            </span>
                          )}
                        </div>
                        
                        <p className={`text-sm ${isCompleted ? 'text-on-surface-variant/70' : 'text-on-surface-variant'} leading-relaxed`}>
                          {step.description}
                        </p>

                        {step.why_it_matters && (
                          <div className="text-xs bg-surface-container p-3 rounded-lg border border-white/5 mt-1 text-on-surface-variant flex gap-2 items-start">
                            <span className="material-symbols-outlined text-sm shrink-0 text-secondary">info</span>
                            <span className="leading-snug">{step.why_it_matters}</span>
                          </div>
                        )}

                        {step.sources && step.sources.length > 0 && (
                          <div className="flex flex-wrap gap-2 mt-2">
                            {step.sources.map(source => (
                              source.url ? (
                                <a 
                                  key={source.id} 
                                  href={source.url} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="text-[10px] font-medium text-primary hover:underline flex items-center gap-1 bg-primary/10 px-2 py-1 rounded"
                                >
                                  Nguồn: {source.organization}
                                  <span className="material-symbols-outlined text-[12px]">open_in_new</span>
                                </a>
                              ) : (
                                <span key={source.id} className="text-[10px] font-medium text-on-surface-variant bg-surface-container px-2 py-1 rounded">
                                  Nguồn: {source.organization}
                                </span>
                              )
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* FEEDBACK SECTION */}
      {plan.status === 'COMPLETED' && (
        <div className="mt-8 glass-panel p-6 rounded-3xl border border-primary/30 bg-gradient-to-br from-surface to-primary/5 shadow-[0_0_30px_rgba(var(--primary-rgb),0.1)]">
          <div className="flex flex-col items-center text-center gap-2 mb-6">
            <span className="material-symbols-outlined text-4xl text-primary mb-2">verified</span>
            <h2 className="text-2xl font-bold text-on-surface">Bạn đã hoàn thành lộ trình</h2>
            <p className="text-sm text-on-surface-variant max-w-md mx-auto">
              Đánh giá mức độ hiệu quả chủ quan của lộ trình chăm sóc này đối với tình trạng thực tế của cây.
            </p>
          </div>

          {!feedbackSubmitted ? (
            <div className="flex flex-col gap-6 max-w-md mx-auto">
              <div className="flex flex-col gap-2">
                <div className="flex justify-between items-end">
                  <label className="text-sm font-semibold text-on-surface">Hiệu quả quan sát được</label>
                  <span className="text-xl font-bold text-primary">{feedbackEffectiveness}%</span>
                </div>
                <input 
                  type="range" 
                  min="0" max="100" step="5"
                  value={feedbackEffectiveness}
                  onChange={(e) => setFeedbackEffectiveness(parseInt(e.target.value))}
                  className="w-full accent-primary h-2 bg-surface-container rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-on-surface-variant font-medium mt-1">
                  <span>Không hiệu quả (0%)</span>
                  <span>Rất hiệu quả (100%)</span>
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-sm font-semibold text-on-surface">Chia sẻ thêm (không bắt buộc)</label>
                <textarea 
                  value={feedbackComment}
                  onChange={(e) => setFeedbackComment(e.target.value)}
                  placeholder="Ví dụ: Bệnh đã ngừng lan, lá mới ra xanh tốt..."
                  className="w-full bg-surface-container-low border border-white/10 rounded-xl p-3 text-sm text-on-surface focus:border-primary/50 focus:outline-none min-h-[80px] resize-none"
                />
              </div>

              <button 
                onClick={handleSubmitFeedback}
                disabled={submittingFeedback}
                className="btn-primary w-full justify-center shadow-lg shadow-primary/20"
              >
                {submittingFeedback ? 'Đang gửi...' : 'Gửi đánh giá'}
              </button>
            </div>
          ) : (
            <div className="text-center p-4 bg-surface-container rounded-xl">
              <p className="text-primary font-bold">Cảm ơn bạn đã gửi đánh giá!</p>
              <p className="text-xs text-on-surface-variant mt-1">Phản hồi của bạn giúp cải thiện hệ thống khuyến cáo IPM.</p>
            </div>
          )}
          
          <div className="mt-6 text-center">
            <p className="text-[10px] text-on-surface-variant max-w-sm mx-auto opacity-70">
              * Đây là đánh giá chủ quan của người dùng về mức độ cải thiện, không phải là độ chính xác của mô hình chẩn đoán AI.
            </p>
          </div>
        </div>
      )}

      {/* DISCLAIMER */}
      <div className="mt-8 text-[11px] text-on-surface-variant opacity-60 text-center px-4">
        Kết quả từ hình ảnh là hỗ trợ sàng lọc ban đầu. Một số bệnh có triệu chứng tương tự nhau; nếu triệu chứng không phù hợp, lan nhanh hoặc không cải thiện, nên xác nhận với chuyên gia nông nghiệp hoặc nguồn chẩn đoán uy tín.
      </div>
    </div>
  );
};
