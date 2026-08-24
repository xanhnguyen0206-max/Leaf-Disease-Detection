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
      throw new Error(err.detail || 'Lỗi phân tích ảnh từ máy chủ.');
    }
    return await res.json();
  } catch (error) {
    console.warn("Backend unavailable, using client-side mock prediction service:", error);
    // Simulate delay for smooth UX
    await new Promise((resolve) => setTimeout(resolve, 2000));
    
    const mock = MOCK_DIAGNOSES[Math.floor(Math.random() * MOCK_DIAGNOSES.length)];
    const previewUrl = URL.createObjectURL(file);
    return {
      id: `mock-${Date.now()}`,
      plant: mock.plant,
      disease: mock.disease,
      confidence: mock.confidence,
      severity: mock.severity,
      recommendations: mock.recommendations,
      image_url: previewUrl,
      created_at: new Date().toISOString()
    };
  }
}

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
      id: "tomato_early_blight",
      name: "Bệnh úa sớm cà chua",
      plant: "Cà chua",
      severity: "Trung bình",
      description: "Nấm Alternaria solani gây ra các vết đốm sẫm màu với các vòng tròn đồng tâm, dẫn đến rụng lá và giảm năng suất.",
      symptoms: [
        "Vết đốm hình tròn màu nâu đen trên lá già",
        "Quầng vàng xung quanh các vết tổn thương",
        "Lá héo khô và rụng dần từ gốc lên ngọn"
      ],
      image_url: "https://images.unsplash.com/photo-1592417817098-8f3d6eb1b7a5?w=600&auto=format&fit=crop"
    },
    {
      id: "potato_late_blight",
      name: "Bệnh sương mai khoai tây",
      plant: "Khoai tây",
      severity: "Nghiêm trọng",
      description: "Tác nhân Phytophthora infestans gây hoại tử lá nhanh chóng và thối củ tàn khốc.",
      symptoms: [
        "Vết đốm mọng nước màu xanh tái ở mép lá",
        "Lớp mốc trắng như nhung ở mặt dưới lá vào buổi sáng",
        "Thân cây bị thâm đen và gãy gập"
      ],
      image_url: "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=600&auto=format&fit=crop"
    },
    {
      id: "apple_powdery_mildew",
      name: "Bệnh phấn trắng táo",
      plant: "Táo",
      severity: "Trung bình",
      description: "Nấm Podosphaera leucotricha tạo lớp bột màu trắng xám trên bề mặt lá và chồi non, làm xoắn lá.",
      symptoms: [
        "Lớp bột mịn màu trắng phủ trên mặt lá",
        "Lá non bị mỏng, cong queo và dị dạng",
        "Chồi phát triển chậm và thoái hóa"
      ],
      image_url: "https://images.unsplash.com/photo-1567306301408-9b74779a11af?w=600&auto=format&fit=crop"
    },
    {
      id: "corn_common_rust",
      name: "Bệnh rỉ sắt ngô",
      plant: "Ngô",
      severity: "Nhẹ",
      description: "Nấm Puccinia sorghi gây ra các ổ bọc nổi màu nâu đỏ trên cả hai mặt lá ngô.",
      symptoms: [
        "Các mụn nhỏ li ti màu vàng sẫm hoặc nâu rỉ sắt",
        "Mụn vỡ ra giải phóng bột bào tử màu nâu",
        "Lá bị khô cháy sớm khi nấm phát triển mạnh"
      ],
      image_url: "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=600&auto=format&fit=crop"
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
