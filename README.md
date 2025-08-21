# AI Resume Screening Agent

An intelligent AI-powered resume screening and job matching tool that uses advanced natural language processing and RAG (Retrieval-Augmented Generation) to provide comprehensive resume analysis and job matching capabilities.

## 🚀 Features

### 📄 Resume Upload & Analysis
- **Multi-format Support**: Upload PDF, DOCX, DOC, and TXT files
- **AI-Powered Analysis**: Comprehensive resume scoring and insights
- **Skill Extraction**: Automatic identification of technical and soft skills
- **Experience Analysis**: Detailed work experience evaluation
- **Red Flag Detection**: Identification of potential issues and gaps

### 📊 Analytics Dashboard
- **Resume Score**: 0-100 scoring based on multiple criteria
- **Skills Breakdown**: Visual representation of identified skills
- **Experience Timeline**: Chronological work experience analysis
- **Improvement Suggestions**: Actionable recommendations for enhancement
- **RAG-Enhanced Insights**: Context-aware analysis using knowledge base

### 🔍 JD Matching
- **Smart Matching**: AI-powered resume-to-job description matching
- **Keyword Analysis**: Matched and missing keyword identification
- **Skill Gap Analysis**: Detailed skill gaps with learning recommendations
- **Salary Estimation**: Market-based salary range predictions
- **Cultural Fit Assessment**: Company culture alignment evaluation
- **Action Items**: Specific improvement recommendations

### 💬 AI Chat Assistant
- **Context-Aware Responses**: Resume-specific advice and guidance
- **Career Counseling**: Professional development recommendations
- **Improvement Tips**: Personalized suggestions for resume enhancement
- **Industry Insights**: Sector-specific advice and trends
- **RAG-Enhanced Knowledge**: Access to HR best practices and knowledge base

## 🛠️ Technology Stack

### Backend
- **Flask**: Python web framework
- **OpenAI GPT-3.5 Turbo**: Advanced language model for analysis
- **spaCy**: Natural language processing for keyword extraction
- **ChromaDB**: Vector database for RAG system
- **Sentence Transformers**: Embedding generation for semantic search
- **pyresparser**: Resume parsing and structured data extraction

### Frontend
- **HTML5/CSS3**: Modern, responsive interface
- **JavaScript**: Interactive user experience
- **Tailwind CSS**: Utility-first CSS framework
- **Material Icons**: Professional iconography

### AI & ML
- **RAG System**: Retrieval-Augmented Generation for enhanced responses
- **Semantic Search**: Advanced similarity matching
- **Knowledge Base**: HR best practices and industry insights
- **Vector Embeddings**: High-dimensional data representation

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Modern web browser

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Pavan-Kalyan112/AI-Resume-Screening-Agent.git
cd AI-Resume-Screening-Agent
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
```

### 3. Activate Virtual Environment
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 5. Set Up Environment Variables
Create a `.env` file in the `backend` directory:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 6. Install spaCy Model
```bash
python -m spacy download en_core_web_sm
```

## 🎯 Usage

### 1. Start the Application
```bash
cd backend
python app.py
```

### 2. Access the Application
Open your browser and navigate to: `http://127.0.0.1:5000`

### 3. Upload Resume
- Click on the "Upload Resume" tab
- Drag and drop or select a resume file (PDF, DOCX, DOC, TXT)
- Click "Analyze Resume" to get comprehensive insights

### 4. View Analytics
- Navigate to the "Analytics" tab to see detailed breakdown
- View resume score, skills analysis, and improvement suggestions
- Access RAG-enhanced insights for better understanding

### 5. Match with Job Description
- Go to the "JD Match" tab
- Upload a resume and paste a job description
- Get detailed matching analysis with skill gaps and recommendations

### 6. Chat with AI Assistant
- Use the "AI Chat" tab for personalized advice
- Ask questions about your resume, career, or job search
- Get context-aware responses based on your uploaded resume

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `FLASK_ENV`: Set to 'development' for debug mode
- `FLASK_DEBUG`: Enable/disable debug mode

### RAG System Configuration
The RAG system automatically initializes with:
- HR knowledge base with best practices
- Industry-specific insights
- Resume analysis guidelines
- Job matching criteria

## 📁 Project Structure

```
AI-Resume-Screening-Agent/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── rag_system.py          # RAG system implementation
│   ├── requirements.txt       # Python dependencies
│   ├── uploads/              # Temporary file storage
│   └── rag_database/         # Vector database (auto-created)
├── frontend/
│   ├── templates/
│   │   └── index.html        # Main application interface
│   └── static/
│       ├── app.js            # Frontend JavaScript
│       └── styles.css        # Custom styling
├── .gitignore               # Git ignore rules
└── README.md               # Project documentation
```

## 🔒 Security Features

- **API Key Protection**: Environment variables for sensitive data
- **File Validation**: Secure file upload with type checking
- **Session Management**: Secure user session handling
- **Input Sanitization**: Protection against malicious inputs
- **Temporary File Cleanup**: Automatic cleanup of uploaded files

## 🚀 Advanced Features

### RAG-Enhanced Analysis
- **Knowledge Base Integration**: Access to HR best practices
- **Similar Case Analysis**: Learning from similar resumes
- **Context-Aware Responses**: Personalized advice based on resume content
- **Industry Insights**: Sector-specific recommendations

### Smart Matching Algorithm
- **Semantic Similarity**: Advanced text matching beyond keywords
- **Skill Gap Analysis**: Detailed learning path recommendations
- **Cultural Fit Assessment**: Company culture alignment
- **Salary Estimation**: Market-based compensation insights

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT-3.5 Turbo API
- spaCy for natural language processing capabilities
- ChromaDB for vector database functionality
- The open-source community for various libraries and tools

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation for common solutions
- Review the troubleshooting section

## 🔄 Version History

- **v1.0.0**: Initial release with basic resume analysis
- **v1.1.0**: Added RAG system integration
- **v1.2.0**: Enhanced JD matching capabilities
- **v1.3.0**: Improved UI/UX and analytics dashboard

---

**Note**: This application requires an OpenAI API key to function. Please ensure you have a valid API key and sufficient credits in your OpenAI account.
