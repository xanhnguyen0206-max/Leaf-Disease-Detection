import { DiagnosisResult, Disease, CareRecommendation } from '../types';

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
      symptoms: [
        "Vết đốm nhỏ 1-3mm màu nâu đen ngậm nước ở hai mặt lá",
        "Viền lá xuất hiện vết cháy sém hoặc quầng vàng",
        "Lá biến dạng, khô giòn và rụng hàng loạt"
      ],
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
      symptoms: [
        "Vết đốm hình tròn màu nâu đen trên lá già",
        "Quầng vàng xung quanh các vết tổn thương",
        "Lá héo khô và rụng dần từ gốc lên ngọn"
      ],
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
      symptoms: [
        "Vết đốm úng nước màu xanh xám loang lổ ở đầu và mép lá",
        "Lớp mốc trắng như sương ở mặt dưới lá trong điều kiện ẩm",
        "Thân và cuống lá xuất hiện vệt thâm đen, dễ gãy"
      ],
      image_url: "/images/diseases/tomato_late_blight.jpg"
    },
    {
      id: "potato_late_blight",
      name: "Bệnh sương mai khoai tây",
      scientific_name: "Phytophthora infestans",
      english_name: "Late Blight of Potato",
      plant: "Khoai tây",
      severity: "Nghiêm trọng",
      description: "Tác nhân Phytophthora infestans gây hoại tử lá nhanh chóng và thối củ tàn khốc.",
      symptoms: [
        "Vết đốm mọng nước màu xanh tái ở mép lá",
        "Lớp mốc trắng như nhung ở mặt dưới lá vào buổi sáng",
        "Thân cây bị thâm đen và gãy gập"
      ],
      image_url: "/images/diseases/potato_late_blight.jpg"
    },
    {
      id: "apple_powdery_mildew",
      name: "Bệnh phấn trắng táo",
      scientific_name: "Podosphaera leucotricha",
      english_name: "Apple Powdery Mildew",
      plant: "Táo",
      severity: "Trung bình",
      description: "Nấm Podosphaera leucotricha tạo lớp bột màu trắng xám trên bề mặt lá và chồi non, làm xoắn lá.",
      symptoms: [
        "Lớp bột mịn màu trắng phủ trên mặt lá",
        "Lá non bị mỏng, cong queo và dị dạng",
        "Chồi phát triển chậm và thoái hóa"
      ],
      image_url: "/images/diseases/apple_powdery_mildew.jpg"
    },
    {
      id: "corn_common_rust",
      name: "Bệnh rỉ sắt ngô",
      scientific_name: "Puccinia sorghi",
      english_name: "Common Rust of Corn / Maize",
      plant: "Ngô",
      severity: "Nhẹ",
      description: "Nấm Puccinia sorghi gây ra các ổ bọc nổi màu nâu đỏ trên cả hai mặt lá ngô.",
      symptoms: [
        "Các mụn nhỏ li ti màu vàng sẫm hoặc nâu rỉ sắt",
        "Mụn vỡ ra giải phóng bột bào tử màu nâu",
        "Lá bị khô cháy sớm khi nấm phát triển mạnh"
      ],
      image_url: "/images/diseases/corn_common_rust.jpg"
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
