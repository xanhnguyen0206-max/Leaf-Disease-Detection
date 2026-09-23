import { DiagnosisResult, Disease, CareRecommendation, TreatmentPlan, TreatmentFeedbackCreate } from '../types';

const API_BASE = '/api';

// Fallback Mock Prediction Service
const MOCK_DIAGNOSES = [
  {
    plant: "Cà chua",
    disease: "Bệnh úa sớm cà chua (Early Blight)",
    confidence: 0.947,
    severity: "Trung bình",
    recommendations: [
      { title: "Cắt tỉa lá bệnh", description: "Cắt bỏ ngay các lá già ở tầng dưới có xuất hiện vết đốm sẫm màu." },
      { title: "Tưới gốc không làm ướt lá", description: "Chỉ tưới ẩm dưới gốc cây vào buổi sáng, giữ bề mặt lá khô ráo." },
      { title: "Phun chế phẩm nấm đối kháng", description: "Phun nấm Trichoderma định kỳ 7-10 ngày/lần." }
    ]
  },
  {
    plant: "Khoai tây",
    disease: "Bệnh sương mai khoai tây (Late Blight)",
    confidence: 0.962,
    severity: "Nghiêm trọng",
    recommendations: [
      { title: "Phun gốc Đồng sulfat / Mancozeb", description: "Phun phủ kín hai mặt lá ngay khi xuất hiện mốc trắng." },
      { title: "Tăng độ thông thoáng", description: "Vặt bỏ chồi phụ rậm rạp để tăng luồng gió qua tán lá." }
    ]
  },
  {
    plant: "Táo",
    disease: "Bệnh phấn trắng táo (Powdery Mildew)",
    confidence: 0.915,
    severity: "Trung bình",
    recommendations: [
      { title: "Phun dung dịch Baking Soda", description: "Pha 5g baking soda vào 1 lít nước phun lá." },
      { title: "Tỉa bớt cành rậm", description: "Mở rộng tán lá đón ánh nắng mặt trời chiếu trực tiếp." }
    ]
  }
];

export async function predictLeaf(file: File): Promise<DiagnosisResult> {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      body: formData,
    });
    
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Lỗi máy chủ (${res.status}): Không thể xử lý ảnh chẩn đoán.`);
    }
    
    const data: DiagnosisResult = await res.json();
    return data;
  } catch (error: any) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('Không thể kết nối đến máy chủ backend LeafAI (http://localhost:8000). Vui lòng đảm bảo backend đang chạy.');
    }
    throw error;
  }
}

export const predictImage = predictLeaf;

export async function fetchDiseases(search?: string, plant?: string): Promise<Disease[]> {
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (plant && plant !== 'Tất cả') params.append('plant', plant);

  try {
    const res = await fetch(`${API_BASE}/diseases?${params.toString()}`);
    if (!res.ok) throw new Error('Không thể tải danh sách bệnh.');
    return await res.json();
  } catch (error) {
    console.warn("Backend API offline, returning static disease data:", error);
    return getStaticDiseases(search, plant);
  }
}

export async function fetchDiseaseById(id: string): Promise<Disease | null> {
  try {
    const res = await fetch(`${API_BASE}/diseases/${id}`);
    if (!res.ok) throw new Error('Disease not found');
    return await res.json();
  } catch (error) {
    const all = getStaticDiseases();
    return all.find((d) => d.id === id) || null;
  }
}

export async function fetchHistory(): Promise<DiagnosisResult[]> {
  try {
    const res = await fetch(`${API_BASE}/history`);
    if (!res.ok) throw new Error('Failed to fetch history');
    return await res.json();
  } catch (error) {
    console.warn("Backend API offline, using local storage history.");
    const stored = localStorage.getItem('leafai_history');
    return stored ? JSON.parse(stored) : [];
  }
}

export async function deleteHistoryItem(id: string): Promise<void> {
  try {
    await fetch(`${API_BASE}/history/${id}`, { method: 'DELETE' });
  } catch (error) {
    const stored = localStorage.getItem('leafai_history');
    if (stored) {
      const history: DiagnosisResult[] = JSON.parse(stored);
      const filtered = history.filter(h => h.id !== id);
      localStorage.setItem('leafai_history', JSON.stringify(filtered));
    }
  }
}

export async function saveLocalHistory(item: DiagnosisResult): Promise<void> {
  const stored = localStorage.getItem('leafai_history');
  const history: DiagnosisResult[] = stored ? JSON.parse(stored) : [];
  history.unshift(item);
  localStorage.setItem('leafai_history', JSON.stringify(history));
}

export async function fetchTreatmentPlan(diagnosisId: string): Promise<TreatmentPlan> {
  const res = await fetch(`${API_BASE}/treatment-plans/${diagnosisId}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Không thể tải lộ trình chăm sóc.');
  }
  return await res.json();
}

export async function updateTreatmentStepProgress(planId: string, stepId: string, completed: boolean): Promise<void> {
  const res = await fetch(`${API_BASE}/treatment-plans/${planId}/steps/${stepId}?completed=${completed}`, {
    method: 'PATCH',
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Không thể cập nhật tiến độ.');
  }
}

export async function submitTreatmentFeedback(planId: string, feedback: TreatmentFeedbackCreate): Promise<void> {
  const res = await fetch(`${API_BASE}/treatment-plans/${planId}/feedback`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(feedback),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Không thể gửi đánh giá.');
  }
}

function getStaticDiseases(search?: string, plant?: string): Disease[] {
  let diseases: Disease[] = [
    {
      id: "tomato_bacterial_spot",
      name: "Bệnh đốm vi khuẩn cà chua",
      scientific_name: "Xanthomonas hortorum pv. gardneri / Xanthomonas perforans",
      english_name: "Bacterial Spot of Tomato",
      plant: "Cà chua",
      severity: "Nghiêm trọng",
      description: "Vi khuẩn Xanthomonas spp. gây các vết đốm sũng nước nhỏ màu nâu đen, quầng vàng, làm suy kiệt tán lá.",
      overview: "Bệnh đốm vi khuẩn là một trong những bệnh tàn phá nghiêm trọng nhất trên cây cà chua, đặc biệt trong điều kiện thời tiết ấm và mưa nhiều. Vi khuẩn tấn công lá, thân và quả, làm giảm nghiêm trọng khả năng quang hợp và giá trị thương phẩm.",
      pathogen: "Vi khuẩn Xanthomonas spp. (nhiều chủng)",
      favorable_conditions: "Nhiệt độ ấm (24-30°C) và độ ẩm cao. Bệnh phát triển mạnh nhất trong những đợt mưa dông hoặc tưới phun mưa liên tục.",
      transmission: [
        "Lây qua hạt giống mang mầm bệnh",
        "Nước mưa và nước tưới bắn tung tóe",
        "Dụng cụ canh tác và tay người tiếp xúc",
        "Tàn dư cây bệnh vụ trước"
      ],
      risk_level_explanation: "Bệnh lây lan cực nhanh trong điều kiện ẩm ướt, làm rụng lá hàng loạt khiến quả bị rám nắng, gây thiệt hại nặng nề đến năng suất nếu không kiểm soát kịp thời.",
      symptoms: [
        "Vết đốm nhỏ 1-3mm màu nâu đen ngậm nước ở hai mặt lá",
        "Viền lá xuất hiện vết cháy sém hoặc quầng vàng",
        "Lá biến dạng, khô giòn và rụng hàng loạt"
      ],
      early_symptoms: [
        "Xuất hiện các đốm nhỏ như đầu kim, màu nâu sẫm, ngậm nước ở mặt dưới lá",
        "Đốm có thể có quầng màu vàng hẹp xung quanh"
      ],
      mid_symptoms: [
        "Đốm lan rộng đến khoảng 3mm, có hình dạng bất định",
        "Phần trung tâm vết bệnh khô đi và có thể rụng tạo thành lỗ thủng nhỏ",
        "Nhiều vết đốm liên kết tạo mảng cháy lớn"
      ],
      severe_symptoms: [
        "Lá chuyển vàng đồng loạt và rụng sớm",
        "Quả xuất hiện đốm đen, nhám sần vảy ốc",
        "Cây còi cọc, héo úa"
      ],
      similar_diseases_diff: [
        "Khác với Đốm mắt cua (Septoria): Đốm vi khuẩn không có tâm màu xám trắng và không có các chấm đen li ti (quả thể nấm) ở giữa.",
        "Khác với Úa sớm (Early Blight): Đốm vi khuẩn nhỏ hơn và không có các vòng tròn đồng tâm đặc trưng."
      ],
      prevention_before_planting: [
        "Sử dụng hạt giống sạch bệnh, đã qua xử lý nhiệt hoặc hóa chất",
        "Chọn giống cà chua có gen kháng bệnh (nếu có)",
        "Xử lý đất và vệ sinh đồng ruộng kỹ lưỡng trước khi trồng"
      ],
      prevention_during_growth: [
        "Tránh làm việc trên ruộng khi lá đang ướt",
        "Khử trùng dụng cụ cắt tỉa thường xuyên",
        "Phát hiện và nhổ bỏ sớm những cây có triệu chứng đầu tiên"
      ],
      water_management: "Tránh tưới phun mưa lên lá, ưu tiên tưới nhỏ giọt ở gốc. Tưới vào sáng sớm để lá khô nhanh trong ngày.",
      nutrition_management: "Bón phân cân đối, tránh bón thừa đạm làm cây quá xanh tốt và rậm rạp, dễ nhiễm bệnh.",
      density_management: "Trồng đúng mật độ khuyến cáo, đảm bảo khoảng cách giữa các cây để tăng cường thông gió.",
      pruning_guide: "Tỉa bỏ bớt lá chân, cành vô hiệu, tạo độ thông thoáng. Cắt tỉa vào ngày nắng ráo.",
      biological_control: [
        "Sử dụng chế phẩm sinh học chứa vi khuẩn Bacillus subtilis hoặc vi khuẩn thực khuẩn thể (bacteriophages) để ức chế mầm bệnh.",
        "Phun phòng định kỳ các chế phẩm vi sinh từ giai đoạn cây con."
      ],
      chemical_control_principles: [
        "Sử dụng các loại thuốc gốc Đồng (Copper) kết hợp với Mancozeb để tăng hiệu lực diệt khuẩn.",
        "Phun phòng ngay khi có dự báo mưa kéo dài.",
        "Luân phiên hóa chất để tránh vi khuẩn kháng thuốc."
      ],
      aftercare_monitoring: [
        "Kiểm tra mặt dưới lá 2 ngày một lần trong thời điểm thời tiết bất lợi.",
        "Đánh giá hiệu quả của thuốc sau 5-7 ngày phun."
      ],
      common_mistakes: [
        "Tưới phun mưa vào buổi chiều tối khiến lá ướt qua đêm.",
        "Chỉ bắt đầu phun thuốc khi lá đã vàng rụng tơi tả (quá muộn)."
      ],
      when_to_seek_help: "Khi bệnh lan nhanh sang trái hoặc không có dấu hiệu ngừng lại sau 2 lần phun thuốc gốc Đồng.",
      sources: ["UC Statewide IPM Program", "Cornell Cooperative Extension", "FAO Plant Production and Protection Paper"],
      image_url: "/images/diseases/tomato_bacterial_spot.jpg"
    },
    {
      id: "tomato_early_blight",
      name: "Bệnh úa sớm cà chua",
      scientific_name: "Alternaria solani",
      english_name: "Early Blight of Tomato",
      plant: "Cà chua",
      severity: "Trung bình",
      description: "Nấm Alternaria solani gây ra các vết đốm sẫm màu với các vòng tròn đồng tâm, dẫn đến rụng lá và giảm năng suất.",
      overview: "Bệnh úa sớm là một bệnh nấm phổ biến rộng khắp, tấn công lá, thân và trái. Bệnh làm giảm tuổi thọ của bộ lá, khiến trái dễ bị cháy nắng và suy giảm năng suất đáng kể.",
      pathogen: "Nấm Alternaria solani",
      favorable_conditions: "Phát triển mạnh ở nhiệt độ 24-29°C kết hợp với độ ẩm cao, có sương mù hoặc mưa nhẹ xen kẽ ngày nắng.",
      transmission: [
        "Bào tử nấm tồn tại trong tàn dư thực vật ở đất từ vụ trước",
        "Lây lan chủ yếu qua gió và mưa bắn",
        "Côn trùng mang mầm bệnh"
      ],
      risk_level_explanation: "Bệnh tiến triển từ từ nhưng có thể làm rụng trụi lá dưới, khiến trái mất năng suất và dễ bị hỏng do nắng trực tiếp.",
      symptoms: [
        "Vết đốm hình tròn màu nâu đen trên lá già",
        "Quầng vàng xung quanh các vết tổn thương",
        "Lá héo khô và rụng dần từ gốc lên ngọn"
      ],
      early_symptoms: [
        "Đốm nhỏ màu nâu hoặc đen, hình dạng bất quy tắc trên các lá già ở phần thấp của cây",
        "Kích thước đốm từ 1-2mm"
      ],
      mid_symptoms: [
        "Vết đốm lớn dần lên đến 1cm, xuất hiện các vòng tròn đồng tâm rất đặc trưng (giống bia ngắm)",
        "Mô lá xung quanh vết đốm bắt đầu chuyển sang màu vàng"
      ],
      severe_symptoms: [
        "Các đốm liên kết lại với nhau làm chết cả mảng lá lớn",
        "Lá khô, teo lại và rụng đi",
        "Vết lõm thâm đen, có vòng đồng tâm xuất hiện ở cuống trái"
      ],
      similar_diseases_diff: [
        "Khác với Bệnh sương mai (Late Blight): Úa sớm tiến triển chậm hơn, vết đốm có vòng đồng tâm rạch ròi, trong khi sương mai lan rất nhanh và không có vòng đồng tâm."
      ],
      prevention_before_planting: [
        "Luân canh cây trồng (không trồng họ cà trong 2-3 năm ở cùng một diện tích)",
        "Sử dụng giống có khả năng kháng bệnh úa sớm",
        "Vệ sinh kỹ tàn dư cây trồng vụ trước"
      ],
      prevention_during_growth: [
        "Phủ màng nông nghiệp để hạn chế đất bắn lên lá chân",
        "Cọc/giàn nâng đỡ cây để lá không chạm đất"
      ],
      water_management: "Giữ tán lá khô ráo. Tránh tưới phun từ trên xuống.",
      nutrition_management: "Đảm bảo cây đủ dinh dưỡng, đặc biệt là Kali. Cây yếu và thiếu dinh dưỡng dễ mẫn cảm với úa sớm hơn.",
      density_management: "Đảm bảo khoảng cách trồng rộng rãi để không khí lưu thông tốt, làm khô lá nhanh chóng.",
      pruning_guide: "Thường xuyên tỉa bỏ các lá già, lá sát đất ngay khi có dấu hiệu bệnh đầu tiên.",
      biological_control: [
        "Áp dụng nấm đối kháng Trichoderma spp. vào đất để giảm mật độ mầm bệnh.",
        "Phun các loại trà ủ phân vi sinh (compost tea) lên lá."
      ],
      chemical_control_principles: [
        "Phun thuốc phòng ngừa chứa hoạt chất Mancozeb, Chlorothalonil khi thời tiết thuận lợi cho bệnh.",
        "Sử dụng thuốc nội hấp (như Azoxystrobin) khi bệnh chớm xuất hiện."
      ],
      aftercare_monitoring: [
        "Theo dõi sự tiến triển của bệnh lên các tầng lá phía trên.",
        "Đảm bảo đã thu dọn toàn bộ lá bệnh ra khỏi vườn."
      ],
      common_mistakes: [
        "Vứt lá bệnh ngay trên luống trồng khiến mầm bệnh tiếp tục lây lan.",
        "Nhầm lẫn với bệnh sương mai và xử lý sai cách."
      ],
      when_to_seek_help: "Khi bệnh tiến triển quá nhanh lên đến đỉnh ngọn cây và không phản ứng với thuốc diệt nấm.",
      sources: ["University of California IPM", "Cornell Cooperative Extension"],
      image_url: "/images/diseases/tomato_early_blight.jpg"
    },
    {
      id: "tomato_late_blight",
      name: "Bệnh sương mai cà chua",
      scientific_name: "Phytophthora infestans",
      english_name: "Late Blight of Tomato",
      plant: "Cà chua",
      severity: "Nghiêm trọng",
      description: "Nấm noãn Phytophthora infestans tấn công nhanh trong thời tiết nồm ẩm mát mẻ, gây cháy lá và thối quả diện rộng.",
      overview: "Sương mai là một trong những bệnh thực vật tàn phá khủng khiếp nhất trong lịch sử (tác nhân gây Nạn đói khoai tây Ireland). Bệnh có thể quét sạch toàn bộ vườn cà chua chỉ trong vài ngày nếu gặp thời tiết nồm ẩm.",
      pathogen: "Nấm noãn Phytophthora infestans (Oomycete)",
      favorable_conditions: "Nhiệt độ mát mẻ (15-21°C) và độ ẩm rất cao (sương mù, mưa phùn dầm dề).",
      transmission: [
        "Bào tử phân tán rất xa theo gió",
        "Nước mưa và dòng chảy",
        "Củ khoai tây bệnh bị bỏ quên (ký chủ phụ)"
      ],
      risk_level_explanation: "Nguy cơ tàn phá cực đoan. Bệnh lây lan theo cấp số nhân và có thể hủy diệt toàn bộ cây trồng trong thời gian chưa đầy một tuần.",
      symptoms: [
        "Vết đốm úng nước màu xanh xám loang lổ ở đầu và mép lá",
        "Lớp mốc trắng như sương ở mặt dưới lá trong điều kiện ẩm",
        "Thân và cuống lá xuất hiện vệt thâm đen, dễ gãy"
      ],
      early_symptoms: [
        "Vết đốm mọng nước màu xanh nhạt hoặc xám, không có ranh giới rõ rệt, thường bắt đầu ở mép lá"
      ],
      mid_symptoms: [
        "Vết đốm lan rộng nhanh chóng, chuyển sang màu nâu đen",
        "Vào buổi sáng sớm hoặc khi trời ẩm, xuất hiện lớp tơ nấm màu trắng ở mặt dưới lá",
        "Thân cây có các vệt sũng nước màu nâu đen, làm cành dễ gãy"
      ],
      severe_symptoms: [
        "Toàn bộ lá cây héo rũ, đen sì và bốc mùi hôi thối",
        "Quả cứng, nổi những mảng màu nâu sẫm, hơi lõm, bề mặt nhăn nheo",
        "Cây chết lụi hoàn toàn"
      ],
      similar_diseases_diff: [
        "Khác với Úa sớm (Early Blight): Sương mai lây lan nhanh hơn, vết đốm sũng nước, không có vòng tròn đồng tâm và gây thối cứng trên quả thay vì chỉ lõm ở cuống."
      ],
      prevention_before_planting: [
        "Sử dụng giống kháng bệnh sương mai (như Mountain Magic, Defiant).",
        "Không trồng cà chua gần khoai tây."
      ],
      prevention_during_growth: [
        "Theo dõi bản tin thời tiết cảnh báo sương mai định kỳ.",
        "Trồng trong nhà màng để bảo vệ khỏi mưa dầm và sương."
      ],
      water_management: "Giữ tuyệt đối khô ráo bộ lá vào ban đêm. Tuyệt đối không tưới phun sương chiều tối.",
      nutrition_management: "Quản lý đạm nghiêm ngặt, tránh cây quá sung tốt.",
      density_management: "Trồng thưa để bảo đảm nắng chiếu sâu vào tán, gió thông thoáng tối đa.",
      pruning_guide: "Cắt bỏ ngay lập tức những cây hoặc nhánh đầu tiên có biểu hiện sương mai và tiêu hủy bằng cách đốt hoặc bỏ vào túi nilon buộc kín.",
      biological_control: [
        "Các chế phẩm sinh học có tác dụng rất hạn chế đối với sương mai một khi bệnh đã bùng phát mạnh."
      ],
      chemical_control_principles: [
        "Phòng bệnh bằng thuốc gốc Đồng, Mancozeb hoặc Chlorothalonil trước các đợt mưa.",
        "Khi phát hiện chớm bệnh, phải sử dụng thuốc nội hấp đặc trị nấm noãn (Mefenoxam, Cymoxanil, Dimethomorph) ngay lập tức."
      ],
      aftercare_monitoring: [
        "Cần kiểm tra toàn bộ vườn mỗi buổi sáng.",
        "Phun lặp lại sau 5-7 ngày theo đúng hướng dẫn trên nhãn."
      ],
      common_mistakes: [
        "Chủ quan không phun phòng khi thời tiết chuyển nồm ẩm.",
        "Dùng tay vặt lá bệnh sau đó tiếp tục đi chạm vào các cây khỏe."
      ],
      when_to_seek_help: "Sương mai là bệnh cần báo động cộng đồng nông nghiệp vì bào tử bay xa. Cần tham vấn khuyến nông để phun dập dịch kịp thời.",
      sources: ["Plant Disease Clinics", "FAO"],
      image_url: "/images/diseases/tomato_late_blight.jpg"
    },
    {
      id: "tomato_septoria_leaf_spot",
      name: "Bệnh đốm mắt cua cà chua",
      scientific_name: "Septoria lycopersici",
      english_name: "Septoria Leaf Spot of Tomato",
      plant: "Cà chua",
      severity: "Trung bình",
      description: "Nấm Septoria lycopersici gây các đốm nhỏ có tâm màu xám trắng rải rác trên lá, dẫn đến rụng lá sớm.",
      overview: "Bệnh đốm mắt cua là bệnh đặc trưng của bộ lá. Bệnh không tấn công quả nhưng làm rụng trụi lá rất nhanh, làm trái chậm phát triển, dễ bị sém nắng.",
      pathogen: "Nấm Septoria lycopersici",
      favorable_conditions: "Nhiệt độ trung bình (20-25°C) và độ ẩm cao. Mưa nhiều hoặc sương ướt lá.",
      transmission: [
        "Bào tử lây lan chủ yếu qua nước mưa, nước tưới bắn từ mặt đất lên lá thấp",
        "Có thể mang mầm bệnh qua nông cụ, tay, côn trùng",
        "Tồn dư trong xác bã thực vật hoặc cỏ dại họ cà"
      ],
      risk_level_explanation: "Bệnh không làm chết cây ngay lập tức nhưng phá hủy nhanh chóng diện tích quang hợp. Việc chẩn đoán bằng ảnh có thể khó do đốm khá nhỏ, cần chú ý phân biệt.",
      symptoms: [
        "Đốm nhỏ hình tròn viền nâu sẫm, tâm xám trắng",
        "Chấm đen li ti ở tâm vết đốm",
        "Lá vàng và rụng dần từ gốc lên ngọn"
      ],
      early_symptoms: [
        "Bắt đầu ở các lá già phía dưới.",
        "Đốm tròn nhỏ (1-2mm), lúc đầu thấm nước, sau đó chuyển sang màu nâu sậm."
      ],
      mid_symptoms: [
        "Đốm có tâm chuyển sang màu trắng xám xỉn, viền ngoài vẫn màu nâu đen sậm (trông giống mắt cua).",
        "Nếu nhìn kỹ hoặc dùng kính lúp, có thể thấy các chấm đen liti (quả thể nấm - pycnidia) ở giữa trung tâm màu trắng xám."
      ],
      severe_symptoms: [
        "Nhiều đốm liên kết khiến lá chuyển sang màu vàng, héo úa và rụng",
        "Bệnh tiến dần lên các tán lá phía trên, cây trơ trụi"
      ],
      similar_diseases_diff: [
        "Khác với Úa sớm (Early Blight): Đốm Septoria thường nhỏ hơn, tròn hơn, tâm màu sáng và CÓ chấm đen liti ở giữa, không có vòng tròn đồng tâm.",
        "Khác với Đốm vi khuẩn (Bacterial Spot): Đốm Septoria có tâm màu xám trắng, trong khi đốm vi khuẩn có màu tối đen hoàn toàn."
      ],
      prevention_before_planting: [
        "Luân canh không trồng cà chua tối thiểu 1-2 năm.",
        "Dọn sạch tàn dư lá bệnh, cày ải đất."
      ],
      prevention_during_growth: [
        "Dùng lớp phủ đất (mulch) bằng rơm rạ hoặc nilon để nước không bắn đất lên lá dưới."
      ],
      water_management: "Tưới nhỏ giọt hoặc tưới ngầm là biện pháp kiểm soát hiệu quả nhất. Không tưới lên lá.",
      nutrition_management: "Giữ cây phát triển cân đối, không bón đạm muộn làm lá mỏng dễ nhiễm bệnh.",
      density_management: "Trồng thưa để lá mau khô sau mưa.",
      pruning_guide: "Thường xuyên lảy bỏ lá chân đã già và lá mang triệu chứng bệnh.",
      biological_control: [
        "Phun định kỳ chế phẩm Bacillus subtilis."
      ],
      chemical_control_principles: [
        "Phòng bằng gốc Đồng hoặc Chlorothalonil.",
        "Đặc trị bằng thuốc nhóm Difenoconazole hoặc Azoxystrobin khi bệnh xuất hiện."
      ],
      aftercare_monitoring: [
        "Kiểm tra mặt lá chân hằng ngày.",
        "Tránh chạm vào cây ướt."
      ],
      common_mistakes: [
        "Nhầm lẫn với đốm vi khuẩn dẫn đến sử dụng sai loại thuốc đặc trị.",
        "Tưới nước vòi rồng thẳng vào bụi cây."
      ],
      when_to_seek_help: "Sử dụng kính lúp nông nghiệp để xác định chắc chắn quả thể nấm (chấm đen nhỏ) ở giữa vết đốm khi chẩn đoán không rõ ràng bằng ảnh.",
      sources: ["University of Maryland Extension", "Penn State Extension"],
      image_url: "/images/diseases/tomato_septoria_leaf_spot.jpg"
    },
    {
      id: "tomato_leaf_mold",
      name: "Bệnh nấm mốc lá cà chua",
      scientific_name: "Passalora fulva (Cladosporium fulvum)",
      english_name: "Tomato Leaf Mold",
      plant: "Cà chua",
      severity: "Cao",
      description: "Nấm gây mốc màu xám nhạt đục mặt dưới lá, trong khi mặt trên xuất hiện đốm vàng.",
      overview: "Mốc lá là bệnh chủ yếu đe dọa các vườn cà chua trồng trong nhà màng, nhà kính do môi trường kín, độ ẩm cao. Bệnh làm vàng và chết lá nhanh chóng.",
      pathogen: "Nấm Passalora fulva",
      favorable_conditions: "Độ ẩm không khí rất cao (>85%) và nhiệt độ ôn hòa (22-26°C). Môi trường nhà kính lưu thông không khí kém là điều kiện lý tưởng.",
      transmission: [
        "Bào tử nấm lây lan mạnh mẽ qua luồng gió",
        "Có thể tồn tại trên hạt giống hoặc tàn dư trong đất"
      ],
      risk_level_explanation: "Gây tổn thất lớn cho mô hình trồng nhà kính, nhà màng. Lá héo sớm dẫn đến hoa rụng và trái nhỏ.",
      symptoms: [
        "Đốm màu vàng xanh trên mặt lá",
        "Mốc xám nhạt đến nâu ô-liu dưới mặt lá",
        "Lá khô cong và rụng"
      ],
      early_symptoms: [
        "Mặt trên lá (đặc biệt lá già) xuất hiện các mảng màu xanh nhạt hoặc vàng nhạt, không có ranh giới rõ ràng."
      ],
      mid_symptoms: [
        "Tại vị trí các đốm vàng đó, quan sát mặt dưới lá sẽ thấy một lớp mốc nhung màu xám nhạt, xám xanh hoặc nâu ô-liu.",
        "Mảng vàng mặt trên đậm màu dần."
      ],
      severe_symptoms: [
        "Lá bị quăn lại, khô giòn màu nâu và chết rụng dần",
        "Bệnh lây lan nhanh lên các lá non phía trên"
      ],
      similar_diseases_diff: [
        "Khác với Phấn trắng (Powdery Mildew): Bệnh phấn trắng có lớp mốc trắng trên CẢ mặt trên và mặt dưới lá. Mốc lá (Leaf Mold) có mốc chủ yếu ở mặt dưới, mặt trên là các đốm vàng.",
        "Khác với Sương mai (Late Blight): Mốc lá không gây hoại tử sũng nước đen sì, và không trực tiếp gây thối quả."
      ],
      prevention_before_planting: [
        "Sử dụng giống kháng bệnh mốc lá (nhiều giống nhà kính hiện đại có gen kháng).",
        "Xử lý hạt giống bằng nước nóng."
      ],
      prevention_during_growth: [
        "Mở thông gió nhà màng.",
        "Làm sạch nhà kính và khử trùng trước khi bắt đầu vụ mới."
      ],
      water_management: "Giữ độ ẩm nhà màng dưới 85%. Không để ngưng tụ nước trong nhà kính.",
      nutrition_management: "Cung cấp dinh dưỡng đầy đủ, tránh thiếu Magie (triệu chứng thiếu Magie có thể gây vàng lá dễ nhầm với mốc lá).",
      density_management: "Tỉa thưa hợp lý, đảm bảo gió lưu thông tốt giữa các hàng cây.",
      pruning_guide: "Ngắt bỏ lá bệnh cẩn thận đưa vào túi để tránh làm tung bào tử ra không khí.",
      biological_control: [
        "Chế phẩm nấm Bacillus subtilis có tác dụng ức chế nấm mốc lá."
      ],
      chemical_control_principles: [
        "Sử dụng Chlorothalonil hoặc Mancozeb làm thuốc phòng.",
        "Thuốc nội hấp nhóm Difenoconazole cho hiệu quả trị liệu cao."
      ],
      aftercare_monitoring: [
        "Theo dõi độ ẩm trong nhà màng bằng ẩm kế liên tục."
      ],
      common_mistakes: [
        "Trồng quá dày trong nhà kính không trang bị quạt đối lưu không khí.",
        "Nhầm với triệu chứng thiếu chất."
      ],
      when_to_seek_help: "Sử dụng ảnh chụp mặt dưới lá để hệ thống AI hoặc chuyên gia có thể xác nhận chính xác lớp mốc nhung ô-liu.",
      sources: ["University of Minnesota Extension", "Cornell"],
      image_url: "/images/diseases/tomato_leaf_mold.jpg"
    },
    {
      id: "tomato_powdery_mildew",
      name: "Bệnh phấn trắng cà chua",
      scientific_name: "Oidium neolycopersici / Leveillula taurica",
      english_name: "Powdery Mildew of Tomato",
      plant: "Cà chua",
      severity: "Trung bình",
      description: "Nấm gây bệnh tạo ra lớp mốc trắng mịn như bột rắc rải rác trên bề mặt lá.",
      overview: "Bệnh phấn trắng bao phủ lá cây bằng một lớp bào tử màu trắng, cản trở quá trình quang hợp. Bệnh khá đặc biệt vì có thể phát triển trong điều kiện khô ráo, không cần nước ướt trên bề mặt lá.",
      pathogen: "Nấm Oidium neolycopersici (hoặc Leveillula taurica ở vùng nóng khô)",
      favorable_conditions: "Nhiệt độ ôn hòa (20-27°C) và độ ẩm trung bình. Đặc trưng của nấm phấn trắng là BÀO TỬ CÓ THỂ NẢY MẦM TRONG ĐIỀU KIỆN KHÔNG CÓ NƯỚC BỀ MẶT (lá khô).",
      transmission: [
        "Bào tử bay nhẹ trong không khí, lây lan dễ dàng theo gió."
      ],
      risk_level_explanation: "Làm giảm năng suất từ từ do làm giảm diện tích quang hợp. Không lập tức gây chết cây nhưng làm cây suy kiệt.",
      symptoms: [
        "Đốm mốc như phấn trắng trên lá",
        "Lá héo khô màng giấy",
        "Lan ra cuống hoa"
      ],
      early_symptoms: [
        "Xuất hiện các đốm phấn nhỏ li ti, màu trắng hoặc xám nhạt, có hình thức giống như bột mịn, chủ yếu trên mặt trên của lá."
      ],
      mid_symptoms: [
        "Các đốm bột lan rộng, bao phủ cả mặt trên và có thể mặt dưới lá.",
        "Lá bên dưới lớp bột bắt đầu ngả vàng."
      ],
      severe_symptoms: [
        "Lá bị bao phủ toàn bộ, khô giòn, nhăn nheo, cuộn lại và hoại tử.",
        "Có thể bao phủ thân và cuống hoa, làm rụng hoa."
      ],
      similar_diseases_diff: [
        "Khác với Mốc lá (Leaf Mold): Phấn trắng mọc chủ yếu ở mặt trên lá và có màu trắng bột, trong khi mốc lá có màu xám/ô liu và mọc ở mặt dưới."
      ],
      prevention_before_planting: [
        "Sử dụng giống có khả năng chống chịu bệnh phấn trắng.",
        "Tiêu hủy cỏ dại xung quanh vườn vì cỏ dại có thể là ký chủ mang bệnh."
      ],
      prevention_during_growth: [
        "Kiểm soát độ thông thoáng.",
        "Có thể phun rửa lá bằng tia nước mạnh vào buổi sáng sớm (bào tử phấn trắng bị ức chế bởi nước đọng)."
      ],
      water_management: "Duy trì độ ẩm thích hợp, cây bị khô hạn sẽ mẫn cảm hơn với bệnh.",
      nutrition_management: "Tránh bón thừa đạm.",
      density_management: "Tỉa bớt cành và lá để nắng chiếu vào (tia UV từ nắng ức chế sự phát triển của nấm phấn trắng).",
      pruning_guide: "Loại bỏ các lá bị nhiễm nặng để giảm mật độ bào tử trong không khí.",
      biological_control: [
        "Phun hỗn hợp Baking soda (Natri bicarbonat) pha loãng với một chút dầu khoáng.",
        "Phun dung dịch sữa tươi pha loãng (tỉ lệ 1:9 với nước) có tác dụng hiệu quả kiểm soát phấn trắng nhờ tác động của vi sinh vật lên men và enzyme."
      ],
      chemical_control_principles: [
        "Sử dụng thuốc gốc Lưu huỳnh (Sulfur) - rất đặc hiệu trị phấn trắng.",
        "Phun các loại dầu khoáng nông nghiệp hoặc dầu Neem."
      ],
      aftercare_monitoring: [
        "Theo dõi các lá non mới ra xem có tái nhiễm không."
      ],
      common_mistakes: [
        "Phun lưu huỳnh trong lúc nhiệt độ trên 32°C sẽ làm cháy lá.",
        "Nghĩ rằng lá ướt mới bị bệnh nấm nên ngưng tưới hoàn toàn."
      ],
      when_to_seek_help: "Hình ảnh bột trắng rất đặc trưng nên chẩn đoán bằng ảnh thường có độ chính xác cao.",
      sources: ["RHS", "UC IPM"],
      image_url: "/images/diseases/tomato_powdery_mildew.jpg"
    }
  ];

  if (plant && plant !== "Tất cả") {
    diseases = diseases.filter(d => d.plant === plant);
  }
  if (search) {
    const q = search.toLowerCase();
    diseases = diseases.filter(d => d.name.toLowerCase().includes(q) || d.plant.toLowerCase().includes(q) || d.description.toLowerCase().includes(q));
  }
  return diseases;
}
