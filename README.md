# 🧭 khappha.online - Trợ lý du lịch thông minh

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![LangChain](https://img.shields.io/badge/🦜🔗_LangChain-blue)](https://python.langchain.com/)

> **AI Agent tự động lên kế hoạch du lịch thông minh kết hợp LLM, Web Search và Database**

---

## 📋 Mục lục

- [Tổng quan dự án](#-tổng-quan-dự-án)
- [Tính năng chính](#-tính-năng-chính)
- [Kiến trúc hệ thống](#️-kiến-trúc-hệ-thống)
- [Công nghệ sử dụng](#-công-nghệ-sử-dụng)
- [Database Schema](#️-database-schema)
- [Cài đặt & Chạy](#-cài-đặt--chạy)
- [API Documentation](#-api-documentation)
- [AI Agent Pipeline](#-ai-agent-pipeline)
- [Cấu trúc dự án](#-cấu-trúc-dự-án)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Roadmap](#-roadmap)

---

## 🎯 Tổng quan dự án

### **Thông tin cơ bản**

| Thông tin | Chi tiết |
|-----------|----------|
| **Tên dự án** | khappha.online |
| **Phiên bản** | 1.0.0 (MVP) |
| **Lĩnh vực** | AI trong du lịch & chuyển đổi số |
| **Đối tượng** | Du khách cá nhân, gia đình, nhóm bạn |
| **Mục tiêu** | Tự động hóa việc lên kế hoạch du lịch bằng AI |
| **Team** | SGU Innovators |
| **Hackathon** | SGU Hackathon 2025 |

### **Vấn đề giải quyết**

#### ❌ **Hiện tại:**
- ⏱️ Mất nhiều giờ research địa điểm, khách sạn, nhà hàng
- 🔀 Thông tin rời rạc từ nhiều nguồn (Google, TripAdvisor, blog,...)
- 🤔 Khó tạo lịch trình tối ưu theo sở thích cá nhân
- 💸 Không biết ngân sách ước tính trước khi đi
- 📱 Phải mở nhiều app/website khác nhau

#### ✅ **khappha.online giải quyết:**
- ⚡ **Nhanh**: Tạo lịch trình chi tiết trong < 30 giây
- 🔍 **Tự động**: Tìm kiếm thông tin mới nhất từ web real-time
- 🧠 **Thông minh**: Cá nhân hóa theo sở thích, ngân sách, phong cách du lịch
- 💾 **Tiện lợi**: Lưu trữ và quản lý tất cả kế hoạch ở một nơi
- 💬 **Tự nhiên**: Giao tiếp như chat với bạn bè

### **Demo Use Case**

```
👤 User: "Tôi muốn đi Đà Lạt 3 ngày 2 đêm cuối tuần này, ngân sách 
         5 triệu, thích chụp ảnh và khám phá thiên nhiên"

🤖 khappha.online:
   ✓ Tìm kiếm thông tin thời tiết Đà Lạt cuối tuần
   ✓ Phân tích sở thích (photography, nature)
   ✓ Tính toán ngân sách 5 triệu
   ✓ Tạo lịch trình chi tiết 3 ngày
   ✓ Gợi ý địa điểm phù hợp với chụp ảnh
   ✓ Ước tính chi phí cho từng hoạt động
   → Trả về kế hoạch hoàn chỉnh trong 25 giây!
```

---

## ✨ Tính năng chính

### **Core Features**

| Feature | Mô tả | Tech | Status |
|---------|-------|------|--------|
| 💬 **Natural Chat** | Trò chuyện tự nhiên tiếng Việt | Gemini Pro | ✅ |
| 🔍 **Real-time Search** | Tìm kiếm thông tin du lịch mới nhất | DuckDuckGo API | ✅ |
| 📅 **Smart Planning** | Sinh lịch trình chi tiết theo ngày/giờ | LangChain Agent | ✅ |
| 💰 **Budget Calculator** | Ước tính chi phí ăn-ở-chơi-di chuyển | Custom Algorithm | ✅ |
| 💾 **Plan Management** | Lưu, xem, chỉnh sửa kế hoạch | SQLite | ✅ |
| 📊 **Recommendation** | Gợi ý dựa trên lịch sử và sở thích | ML-based | ✅ |
| 🗺️ **Map Integration** | Hiển thị địa điểm trên bản đồ | Google Maps | 🔄 |
| 📱 **Responsive UI** | Giao diện đẹp mọi thiết bị | TailwindCSS | ✅ |
| 📤 **Export PDF** | Xuất kế hoạch ra file PDF | ReportLab | 📋 |
| 🎤 **Voice Input** | Nhập lệnh bằng giọng nói | Web Speech API | 📋 |

**Chú thích:** ✅ Hoàn thành | 🔄 Đang phát triển | 📋 Trong kế hoạch

### **🎯 Use Cases**

1. **Solo Traveler**: Lên kế hoạch một mình, budget conscious
2. **Family Trip**: Kế hoạch phù hợp gia đình có trẻ nhỏ
3. **Group Travel**: Điều phối lịch trình cho nhóm bạn
4. **Business Travel**: Tối ưu thời gian cho công tác
5. **Backpacker**: Budget thấp, trải nghiệm địa phương

---

## 🏗️ Kiến trúc hệ thống

### **High-Level Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                       │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │  HTML/Jinja2  │  │  JavaScript   │  │  TailwindCSS  │       │
│  │   Templates   │  │  (Vanilla JS) │  │   + Custom    │       │
│  └───────────────┘  └───────────────┘  └───────────────┘       │
│  Features: Real-time chat, typing effect, error handling        │
└─────────────────────────────────────────────────────────────────┘
                              ↕ REST API (JSON)
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER (Flask)                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  API Routes: /chat, /save-plan, /plans, /upload        │    │
│  │  Middleware: CORS, Session, Error Handler              │    │
│  │  Services: AuthService, PlanService, SearchService     │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                       AI AGENT LAYER                            │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  LangChain  │→ │ Gemini Pro   │→ │ DuckDuckGo   │           │
│  │   Agent     │  │   LLM API    │  │   Search     │           │
│  └─────────────┘  └──────────────┘  └──────────────┘           │
│         ↓                                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │           Trip Planner Engine                           │    │
│  │  • Intent Detection      • Context Management           │    │
│  │  • Web Data Extraction   • Budget Calculation           │    │
│  │  • Itinerary Generation  • Response Formatting          │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   SQLite3    │  │   File       │  │   In-Memory  │          │
│  │   Database   │  │   Storage    │  │    Cache     │          │
│  │              │  │  (uploads/)  │  │   (LRU/TTL)  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### **Request Flow - Chi tiết**

```
1. User Input
   ↓
2. Frontend (chat.js) → POST /api/chat
   ↓
3. Flask Route → Validate Input
   ↓
4. AI Agent (ai_agent.py)
   ├─→ Intent Detection (Gemini)
   │   • Extract: destination, duration, budget, preferences
   │
   ├─→ Web Search (search_tool.py)
   │   • DuckDuckGo: "{destination} travel guide"
   │   • Parse results & extract relevant info
   │
   ├─→ Database Query (db_manager.py)
   │   • Get similar plans from history
   │   • Fetch cached search results
   │
   ├─→ Trip Planner (planner.py)
   │   • Generate day-by-day itinerary
   │   • Calculate budget breakdown
   │   • Format as structured JSON
   │
   └─→ Response Generation (Gemini)
       • Create natural language response
       • Include itinerary & recommendations
   ↓
5. Save to Database
   • conversations table (chat history)
   • travel_plans table (itinerary)
   • search_cache table (search results)
   ↓
6. Return JSON Response
   ↓
7. Frontend Render
   • Display chat message
   • Show itinerary cards
   • Enable save/export actions
```

---

## 💻 Công nghệ sử dụng

### **Backend Stack**

| Technology | Version | Purpose | Why? |
|------------|---------|---------|------|
| **Python** | 3.10+ | Core language | Modern, AI-friendly |
| **Flask** | 3.0.0 | Web framework | Lightweight, flexible |
| **LangChain** | 0.1.0+ | AI framework | Agent orchestration |
| **Gemini Pro** | Latest | LLM | Free, powerful, Vietnamese support |
| **DuckDuckGo** | 4.0+ | Search API | No API key required |
| **SQLite3** | Built-in | Database | Simple, portable |
| **Flask-CORS** | 4.0+ | CORS handling | API security |
| **python-dotenv** | 1.0+ | Environment | Config management |

### **Frontend Stack**

| Technology | Purpose | Why? |
|------------|---------|------|
| **HTML5** | Structure | Standard |
| **Jinja2** | Templating | Flask integration |
| **TailwindCSS 3** | Styling | Modern, utility-first |
| **Vanilla JavaScript** | Interactions | No dependencies, fast |
| **Fetch API** | HTTP requests | Native, promise-based |

---

## 🗄️ Database Schema

### **SQLite Tables**

```sql
-- Table 1: users - Quản lý session người dùng
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON
);

-- Table 2: conversations - Lịch sử chat
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    message_type TEXT DEFAULT 'text',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES users(session_id) ON DELETE CASCADE
);

-- Table 3: travel_plans - Kế hoạch du lịch
CREATE TABLE travel_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    plan_name TEXT,
    destination TEXT NOT NULL,
    duration_days INTEGER NOT NULL,
    budget REAL,
    budget_currency TEXT DEFAULT 'VND',
    preferences TEXT,
    itinerary JSON NOT NULL,
    total_cost REAL,
    status TEXT DEFAULT 'active',
    is_favorite BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES users(session_id) ON DELETE CASCADE
);

-- Table 4: search_cache - Cache kết quả tìm kiếm
CREATE TABLE search_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT UNIQUE NOT NULL,
    results JSON NOT NULL,
    source TEXT DEFAULT 'duckduckgo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    hit_count INTEGER DEFAULT 0
);

-- Indexes để tối ưu performance
CREATE INDEX idx_session_id ON conversations(session_id);
CREATE INDEX idx_plan_destination ON travel_plans(destination);
CREATE INDEX idx_plan_created ON travel_plans(created_at DESC);
CREATE INDEX idx_cache_query ON search_cache(query);
```

### **Itinerary JSON Format**

```json
{
  "destination": "Đà Lạt",
  "summary": "3 ngày 2 đêm khám phá Đà Lạt",
  "days": [
    {
      "day": 1,
      "date": "2025-10-25",
      "theme": "Check-in & Khám phá",
      "morning": {
        "time": "08:00-12:00",
        "activity": "Di chuyển từ TP.HCM đến Đà Lạt",
        "location": "Đà Lạt",
        "cost": 300000,
        "cost_note": "Vé xe khách",
        "tips": "Nên đi xe đêm để tiết kiệm thời gian"
      },
      "afternoon": {
        "time": "14:00-18:00",
        "activity": "Check-in khách sạn + Hồ Xuân Hương",
        "location": "Trung tâm Đà Lạt",
        "cost": 100000,
        "cost_note": "Thuê xe máy + vé tham quan"
      },
      "evening": {
        "time": "19:00-22:00",
        "activity": "Chợ Đà Lạt Night Market",
        "location": "Chợ Đà Lạt",
        "cost": 200000,
        "cost_note": "Ăn uống + mua sắm"
      }
    }
  ],
  "budget_breakdown": {
    "transport": 500000,
    "accommodation": 2000000,
    "food": 1500000,
    "activities": 800000,
    "other": 200000,
    "total": 5000000
  },
  "tips": [
    "Mang áo ấm vì Đà Lạt lạnh",
    "Đặt khách sạn trước 1 tuần"
  ],
  "recommended_for": ["couples", "photography", "nature"]
}
```

---

## 🚀 Cài đặt & Chạy

### **Prerequisites**

- Python 3.10 trở lên
- pip (Python package manager)
- Git (optional)

### **Bước 1: Clone / Download Project**

```bash
git clone https://github.com/your-username/SGU_Hackathon.git
cd SGU_Hackathon
```

### **Bước 2: Tạo Virtual Environment**

```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### **Bước 3: Install Dependencies**

```bash
cd backend
pip install -r requirements.txt
```

**requirements.txt:**
```txt
# Web Framework
flask==3.0.0
flask-cors==4.0.0

# AI & LangChain
langchain==0.1.0
langchain-google-genai==0.0.5
google-generativeai==0.3.0

# Search Tool
duckduckgo-search==4.0.0

# Utilities
python-dotenv==1.0.0
requests==2.31.0
werkzeug==3.0.0
```

### **Bước 4: Cấu hình Environment Variables**

Tạo file `.env` trong thư mục `backend/`:

```env
# API KEYS
GEMINI_API_KEY=your_gemini_api_key_here

# FLASK CONFIG
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this

# DATABASE
DATABASE_PATH=data/travelmate.db

# UPLOAD
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

**Lấy Gemini API Key miễn phí:** https://ai.google.dev/

### **Bước 5: Khởi tạo Database**

```bash
python -m database.init_db
```

### **Bước 6: Chạy Application**

```bash
python app.py
```

Truy cập: **http://localhost:5000**

---

## 📡 API Documentation

### **1. Chat với AI**

```http
POST /api/chat
Content-Type: application/json

{
  "message": "Tôi muốn đi Đà Lạt 3 ngày 2 đêm",
  "session_id": "optional"
}
```

**Response:**
```json
{
  "success": true,
  "response": "Tuyệt vời! Đây là kế hoạch...",
  "session_id": "abc123",
  "has_plan": true,
  "plan_data": { ... }
}
```

### **2. Lưu kế hoạch**

```http
POST /api/save-plan
Content-Type: application/json

{
  "session_id": "abc123",
  "destination": "Đà Lạt",
  "duration_days": 3,
  "budget": 5000000,
  "itinerary": { ... }
}
```

### **3. Lấy danh sách kế hoạch**

```http
GET /api/plans?session_id=abc123&limit=10
```

---

## 🤖 AI Agent Pipeline

### **LangChain Agent Setup**

```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)

# Define Tools
tools = [
    Tool(
        name="web_search",
        func=search_web,
        description="Tìm kiếm thông tin du lịch mới nhất"
    ),
    Tool(
        name="get_similar_plans",
        func=get_similar_plans,
        description="Lấy các kế hoạch tương tự từ database"
    )
]

# Create Agent
agent = create_react_agent(llm, tools, prompt_template)
agent_executor = AgentExecutor(agent=agent, tools=tools, max_iterations=5)
```

### **Prompt Template**

```python
SYSTEM_PROMPT = """
Bạn là khappha.online - trợ lý du lịch thông minh chuyên nghiệp của Việt Nam.

NHIỆM VỤ:
1. Phân tích yêu cầu du lịch của người dùng
2. Sử dụng tools để tìm kiếm thông tin
3. Tạo lịch trình chi tiết, thực tế
4. Ước tính chi phí cụ thể

FORMAT LỊCH TRÌNH:
{
  "destination": "...",
  "days": [...],
  "budget_breakdown": {...}
}

NGUYÊN TẮC:
- Luôn thân thiện, nhiệt tình
- Chi phí phải sát với thực tế VN
- Lịch trình hợp lý về thời gian
"""
```

---

## 📂 Cấu trúc dự án

```plaintext
SGU_Hackathon/
│
├── backend/
│   ├── app.py                    # Flask main application
│   ├── config.py                 # Configuration
│   ├── requirements.txt          # Dependencies
│   │
│   ├── agents/
│   │   ├── ai_agent.py           # LangChain agent
│   │   ├── search_tool.py        # DuckDuckGo wrapper
│   │   └── planner.py            # Trip planning
│   │
│   ├── database/
│   │   ├── db_manager.py         # CRUD operations
│   │   ├── models.py             # Data models
│   │   └── init_db.py            # DB initialization
│   │
│   ├── uploads/                  # User files
│   └── data/
│       └── travelmate.db         # SQLite database
│
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   │   └── chat.js           # Chat logic
│   │   └── images/
│   │
│   └── templates/
│       ├── index.html            # Main interface
│       └── plans.html            # Plans page
│
├── tests/
│   ├── test_api.py
│   └── test_agent.py
│
├── .env                          # Environment variables
├── .gitignore
└── README.md
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=backend tests/

# Specific test
pytest tests/test_agent.py -v
```

---

## 🚢 Deployment

### **Development**
```bash
flask run --debug
```

### **Production (Gunicorn)**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### **Cloud Hosting**
- **Render**: Free tier, easy deployment
- **Railway**: Simple, good free tier
- **VPS**: Full control (DigitalOcean, Vultr)

---

## 📈 Roadmap

### **Phase 1: MVP** ✅
- [x] Chat interface
- [x] AI agent với Gemini
- [x] DuckDuckGo search
- [x] SQLite database
- [x] Trip planning

### **Phase 2: Enhancement** 🔄
- [ ] Streaming responses
- [ ] Multi-language support
- [ ] PDF export
- [ ] Google Maps integration
- [ ] Weather API

### **Phase 3: Advanced** 📋
- [ ] Voice input/output
- [ ] Mobile app
- [ ] OTA integration
- [ ] Community features

---

## 📄 License

MIT License - See `LICENSE` file

---

## 👥 Team

**SGU Innovators** - SGU Hackathon 2025

---

## 🙏 Acknowledgments

- [LangChain](https://langchain.com) - AI Agent framework
- [Google Gemini](https://deepmind.google/technologies/gemini/) - LLM API
- [DuckDuckGo](https://duckduckgo.com) - Search API
- [Flask](https://flask.palletsprojects.com) - Web framework
- [TailwindCSS](https://tailwindcss.com) - UI framework

---

<div align="center">

**Made with ❤️ for SGU Hackathon 2025**

[📚 Documentation](#-mục-lục) • [🐛 Report Bug](https://github.com/your-repo/issues) • [💡 Request Feature](https://github.com/your-repo/issues)

</div>
