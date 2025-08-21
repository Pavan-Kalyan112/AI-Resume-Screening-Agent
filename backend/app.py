from flask import Flask, request, jsonify, render_template, session
import os
import pdfplumber
import docx
import re
import json
from pyresparser import ResumeParser
import spacy
from collections import Counter
import random
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

# Import RAG system
from rag_system import get_rag_system

# Resolve paths relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend', 'templates'))
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'frontend', 'static'))

# Initialize Flask with new frontend locations
app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
app.secret_key = 'supersecretkey'  # Needed for session

# Configure upload folder
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize RAG system
rag_system = get_rag_system()

# In-memory store for last uploaded resume text (per session)
resume_store = {}

# Available AI models (OpenAI)
AVAILABLE_MODELS = {
    'gpt-3.5-turbo': 'OpenAI GPT-3.5 Turbo'
}

# Load spaCy model for JD parsing
try:
    nlp = spacy.load('en_core_web_sm')
except:
    import subprocess
    subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
    nlp = spacy.load('en_core_web_sm')

# Load OpenAI credentials
load_dotenv(os.path.join(BASE_DIR, '.env'))
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
client = OpenAI(api_key=OPENAI_API_KEY)

def extract_resume_info(filepath):
    try:
        data = ResumeParser(filepath).get_extracted_data()
        return data
    except Exception as e:
        print(f"Warning: Failed to parse resume {filepath}: {e}")
        return {}

def validate_metadata_for_chromadb(metadata_dict):
    """
    Validate and clean metadata to ensure it only contains primitive types
    that ChromaDB accepts: str, int, float, bool, or None
    """
    valid_metadata = {}
    for key, value in metadata_dict.items():
        if isinstance(value, (str, int, float, bool, type(None))):
            valid_metadata[key] = value
        elif isinstance(value, dict):
            # Convert dict to string representation
            valid_metadata[key] = str(value)
        elif isinstance(value, list):
            # Convert list to string representation
            valid_metadata[key] = str(value)
        else:
            # Convert any other type to string
            valid_metadata[key] = str(value)
    return valid_metadata

def extract_jd_keywords(jd_text):
    doc = nlp(jd_text.lower())
    keywords = []
    for token in doc:
        if token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and len(token.text) > 3:
            keywords.append(token.text)
    return list(set(keywords))

def keyword_density(text, keywords):
    text_lower = text.lower()
    total_words = len(text_lower.split())
    keyword_count = sum(text_lower.count(keyword.lower()) for keyword in keywords)
    return (keyword_count / total_words * 100) if total_words > 0 else 0

def analyze_with_model(model_name, prompt, analysis_type="resume", rag_context=None):
    """Enhanced AI analysis with RAG context for improved quality"""
    try:
        model_to_use = model_name if model_name in AVAILABLE_MODELS else 'gpt-3.5-turbo'
        
        # Enhanced system prompts with RAG context
        system_prompts = {
            "resume": f"""You are an expert HR AI specializing in comprehensive resume analysis. 
Use the following HR knowledge base to provide more accurate and insightful analysis:

KNOWLEDGE BASE:
{rag_context.get('knowledge_base', '')}

Provide detailed insights including technical depth, leadership potential, and career progression.""",
            
            "jd_match": f"""You are an expert HR AI specializing in advanced job-resume matching. 
Use the following HR knowledge base and similar cases for better matching:

KNOWLEDGE BASE:
{rag_context.get('knowledge_base', '')}

SIMILAR CASES:
{rag_context.get('similar_cases', '')}

Provide comprehensive analysis with skill gaps and career path suggestions.""",
            
            "comparison": f"""You are an expert HR AI specializing in candidate comparison and ranking. 
Use the following HR knowledge base for industry-specific insights:

KNOWLEDGE BASE:
{rag_context.get('knowledge_base', '')}

Provide detailed comparison with industry benchmarks."""
        }
        
        system_prompt = system_prompts.get(analysis_type, "You are an expert HR AI.")
        
        response = client.chat.completions.create(
            model=model_to_use,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        content = response.choices[0].message.content
        match = re.search(r'\{[\s\S]*\}', content)
        if match:
            analytics = json.loads(match.group(0))
            confidence = calculate_enhanced_confidence_score(analytics, analysis_type, rag_context)
            return {
                'success': True,
                'analytics': analytics,
                'confidence': confidence,
                'model': model_to_use,
                'response_time': random.uniform(0.5, 2.0),
                'analysis_type': analysis_type,
                'rag_enhanced': bool(rag_context)
            }
        else:
            return {
                'success': False,
                'error': 'Failed to parse AI response',
                'raw_response': content
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'AI analysis failed: {str(e)}'
        }

def calculate_enhanced_confidence_score(analytics, analysis_type, rag_context=None):
    """Enhanced confidence calculation with RAG context consideration"""
    confidence = 0
    
    if analysis_type == "resume":
        if analytics.get('skills') and len(analytics['skills']) > 0:
            confidence += 20
        if analytics.get('experience') and len(analytics['experience']) > 0:
            confidence += 20
        if analytics.get('score') is not None:
            confidence += 15
        if analytics.get('summary') and len(analytics['summary']) > 50:
            confidence += 15
        if analytics.get('leadership_potential'):
            confidence += 10
        if analytics.get('technical_depth'):
            confidence += 10
        if analytics.get('career_progression'):
            confidence += 10
        # Bonus for RAG-enhanced analysis
        if rag_context:
            confidence += 10
    elif analysis_type == "jd_match":
        if analytics.get('score') is not None:
            confidence += 25
        if analytics.get('matched_keywords'):
            confidence += 20
        if analytics.get('skill_gaps'):
            confidence += 20
        if analytics.get('career_path_suggestions'):
            confidence += 15
        if analytics.get('salary_estimate'):
            confidence += 10
        if analytics.get('culture_fit'):
            confidence += 10
        # Bonus for RAG-enhanced analysis
        if rag_context:
            confidence += 10
    
    return min(confidence, 100)

def get_rag_context(resume_text, jd_text=None, analysis_type="resume"):
    """Get RAG context for enhanced analysis"""
    if not hasattr(rag_system, 'initialized') or not rag_system.initialized:
        return {}
    
    try:
        context = {}
        
        # Get relevant knowledge base entries
        if analysis_type == "resume":
            knowledge_query = f"resume analysis best practices for: {resume_text[:500]}"
        else:
            knowledge_query = f"job matching best practices for: {jd_text[:500] if jd_text else ''}"
        
        knowledge_results = rag_system.search_knowledge(knowledge_query, n_results=5)
        context['knowledge_base'] = "\n".join([result['text'] for result in knowledge_results])
        
        # Get similar resumes for context
        if analysis_type == "resume":
            similar_resumes = rag_system.search_similar_resumes(resume_text, n_results=3)
            context['similar_cases'] = "\n".join([f"Similar case: {res['text'][:200]}..." for res in similar_resumes])
        
        # Get similar job descriptions for JD matching
        if analysis_type == "jd_match" and jd_text:
            similar_jobs = rag_system.search_similar_jobs(jd_text, n_results=3)
            context['similar_jobs'] = "\n".join([f"Similar job: {job['text'][:200]}..." for job in similar_jobs])
        
        return context
    except Exception as e:
        print(f"Warning: Failed to get RAG context: {e}")
        return {}

def extract_text_from_file(filepath):
    """Extract text from PDF, DOCX, or TXT files"""
    try:
        if filepath.lower().endswith('.pdf'):
            with pdfplumber.open(filepath) as pdf:
                text = ''
                for page in pdf.pages:
                    text += page.extract_text() or ''
                return text
        elif filepath.lower().endswith(('.docx', '.doc')):
            doc = docx.Document(filepath)
            text = ''
            for paragraph in doc.paragraphs:
                text += paragraph.text + '\n'
            return text
        elif filepath.lower().endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return ''
    except Exception as e:
        print(f"Error extracting text from {filepath}: {e}")
        return ''

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save file temporarily
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        # Extract text
        resume_text = extract_text_from_file(filename)
        if not resume_text.strip():
            return jsonify({'error': 'Could not extract text from file'}), 400
    
    # Store resume text in session
        session['resume_text'] = resume_text
        
        # Get selected model
        selected_model = request.form.get('model', 'gpt-3.5-turbo')
        
        # Get RAG context for enhanced analysis
        rag_context = get_rag_context(resume_text, analysis_type="resume")
        
        # Add resume to RAG system for future reference
        if hasattr(rag_system, 'initialized') and rag_system.initialized:
            try:
    metadata = {
        'filename': file.filename,
        'upload_date': datetime.now().isoformat(),
                    'analysis_type': 'resume'
                }
    valid_metadata = validate_metadata_for_chromadb(metadata)
            rag_system.add_resume(
                resume_id=file.filename,
                resume_text=resume_text,
                metadata=valid_metadata
            )
        except Exception as e:
            print(f"Warning: Failed to add resume to RAG system: {e}")
        
        # Analyze with AI using RAG context
    prompt = f"""
        You are an expert HR AI specializing in comprehensive resume analysis. Analyze the following resume and provide detailed insights including:
        
        RESUME ANALYSIS:
        - A comprehensive summary of the candidate's profile, strengths, and areas for improvement
        - A resume score (0-100) based on relevance, skills, experience, and presentation
        - Key technical and soft skills with proficiency levels
        - Relevant work experience with achievements and impact
        - Any red flags or concerns
        - Leadership potential and management experience
        - Technical depth and expertise level
        - Career progression and growth trajectory
        - Industry alignment and market positioning
        - Specific recommendations for improvement

Return your answer in the following JSON format:
{{
          "summary": "Comprehensive candidate summary...",
          "score": 85,
          "skills": ["Python", "Machine Learning", "Team Leadership"],
          "experience": ["Senior Developer at Tech Corp", "Project Lead at Startup"],
          "redflags": ["Employment gap", "Inconsistent dates"],
          "leadership_potential": "High - demonstrated team leadership and project management",
          "technical_depth": "Advanced - deep expertise in ML and software architecture",
          "career_progression": "Strong upward trajectory with increasing responsibilities",
          "industry_alignment": "Excellent fit for tech industry roles",
          "recommendations": ["Consider for senior positions", "Strong technical background"],
          "improvement_suggestions": ["Add quantifiable achievements", "Include certifications"],
          "other": ["Additional insights..."]
}}

Resume:
{resume_text}
"""
    
        model_result = analyze_with_model(selected_model, prompt, "resume", rag_context)
    
        if not model_result['success']:
            return jsonify({'error': model_result['error']}), 500
        
        analytics = model_result['analytics']
        summary = analytics.get('summary', 'Analysis completed successfully.')
        
        # Clean up file
        os.remove(filename)
        
        result = {
            'summary': summary,
            'analytics': {
                'score': analytics.get('score'),
                'skills': analytics.get('skills'),
                'experience': analytics.get('experience'),
                'redflags': analytics.get('redflags'),
                'leadership_potential': analytics.get('leadership_potential'),
                'technical_depth': analytics.get('technical_depth'),
                'career_progression': analytics.get('career_progression'),
                'industry_alignment': analytics.get('industry_alignment'),
                'recommendations': analytics.get('recommendations', []),
                'improvement_suggestions': analytics.get('improvement_suggestions', []),
                'other': analytics.get('other'),
            },
            'model_info': {
                'name': selected_model,
                'display_name': AVAILABLE_MODELS[selected_model],
                'confidence': model_result['confidence'],
                'response_time': model_result['response_time'],
                'analysis_type': model_result.get('analysis_type', 'resume'),
                'rag_enhanced': model_result.get('rag_enhanced', False)
            },
            'response_time': model_result['response_time']
        }
        
    return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/jd_match', methods=['POST'])
def jd_match():
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file uploaded'}), 400
        
        file = request.files['resume']
        jd = request.form.get('jd', '').strip()
        
        if not jd:
            return jsonify({'error': 'No job description provided'}), 400
        
        # Save file temporarily
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        # Extract text
        resume_text = extract_text_from_file(filename)
        if not resume_text.strip():
            return jsonify({'error': 'Could not extract text from resume file'}), 400
        
        # Get selected model
        selected_model = request.form.get('model', 'gpt-3.5-turbo')
        
        # Get RAG context for enhanced JD matching
        rag_context = get_rag_context(resume_text, jd, analysis_type="jd_match")
    
    # Add to RAG system
    if hasattr(rag_system, 'initialized') and rag_system.initialized:
        try:
                # Add resume
                resume_metadata = {
                'filename': file.filename,
                'upload_date': datetime.now().isoformat(),
                'analysis_type': 'jd_match'
            }
                valid_resume_metadata = validate_metadata_for_chromadb(resume_metadata)
            rag_system.add_resume(
                    resume_id=f"jd_match_{file.filename}",
                resume_text=resume_text,
                    metadata=valid_resume_metadata
            )
    
                # Add job description
            jd_metadata = {
                'upload_date': datetime.now().isoformat(),
                'analysis_type': 'jd_match',
                'resume_filename': file.filename
            }
            valid_jd_metadata = validate_metadata_for_chromadb(jd_metadata)
            rag_system.add_job_description(
                    jd_id=f"jd_match_{file.filename}",
                jd_text=jd,
                metadata=valid_jd_metadata
            )
        except Exception as e:
                print(f"Warning: Failed to add to RAG system: {e}")
        
        # Analyze with AI using RAG context
    prompt = f"""
        You are an expert HR AI specializing in advanced job-resume matching. Provide comprehensive analysis including:
        
        MATCHING ANALYSIS:
        - A detailed match score (0-100) based on keyword overlap, skill alignment, and experience relevance
        - Matched keywords and skills from the job description found in the resume
        - Missing keywords and skills that the candidate lacks
        - Specific skill gaps with learning recommendations and timeframes
        - Career path suggestions based on the candidate's background
        - Estimated salary range for this candidate in this role with confidence level
        - Cultural fit assessment based on experience and background
        - Technical depth evaluation for the role requirements
        - Leadership potential for the position
        - Industry alignment and market positioning
        - Specific action items for improvement

Return your answer in the following JSON format:
{{
          "score": 85,
          "matched_keywords": ["Python", "Machine Learning", "Team Leadership"],
          "missing_keywords": ["AWS", "Docker", "Kubernetes"],
          "skill_gaps": [
            {{
              "skill": "AWS",
              "importance": "High",
              "learning_path": "AWS Certified Solutions Architect",
              "time_to_learn": "3-6 months",
              "priority": "Immediate"
            }}
          ],
          "career_path_suggestions": ["Senior ML Engineer", "Tech Lead", "AI Product Manager"],
          "salary_estimate": {{
            "range": "$120,000 - $150,000",
            "confidence": "High",
            "factors": ["Experience level", "Skill match", "Market rates"],
            "currency": "USD"
          }},
          "culture_fit": "Excellent - collaborative background, startup experience",
          "technical_depth": "Advanced - deep ML expertise, good for senior role",
          "leadership_potential": "High - demonstrated team leadership",
          "feedback": ["Consider AWS certification", "Highlight project management experience"],
          "action_items": ["Obtain AWS certification", "Update resume with quantifiable achievements"],
          "other": ["Additional insights..."]
}}

Resume:
{resume_text}

Job Description:
{jd}
"""
    
        model_result = analyze_with_model(selected_model, prompt, "jd_match", rag_context)
    
        if not model_result['success']:
            return jsonify({'error': model_result['error']}), 500
        
        analytics = model_result['analytics']
        
        # Calculate keyword density
        jd_keywords = extract_jd_keywords(jd)
        density = keyword_density(resume_text, jd_keywords)
        
        result = {
            'summary': f"Match analysis completed. Score: {analytics.get('score', 'N/A')}",
            'analytics': {
            'score': analytics.get('score'),
            'matched_keywords': analytics.get('matched_keywords'),
            'missing_keywords': analytics.get('missing_keywords'),
                'skill_gaps': analytics.get('skill_gaps', []),
                'career_path_suggestions': analytics.get('career_path_suggestions', []),
                'salary_estimate': analytics.get('salary_estimate', {}),
                'culture_fit': analytics.get('culture_fit'),
                'technical_depth': analytics.get('technical_depth'),
                'leadership_potential': analytics.get('leadership_potential'),
            'feedback': analytics.get('feedback'),
                'action_items': analytics.get('action_items', []),
            'other': analytics.get('other'),
            'keyword_density': density,
            },
            'model_info': {
            'name': selected_model,
            'display_name': AVAILABLE_MODELS[selected_model],
            'confidence': model_result['confidence'],
                'response_time': model_result['response_time'],
                'analysis_type': model_result.get('analysis_type', 'jd_match'),
                'rag_enhanced': model_result.get('rag_enhanced', False)
            },
            'response_time': model_result['response_time']
        }
        
        # Clean up file
        os.remove(filename)
    
    return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'JD matching failed: {str(e)}'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
    data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get resume text from session if available
        resume_text = session.get('resume_text', '')
        
        # Get RAG context for enhanced chat responses
        rag_context = {}
        if resume_text and hasattr(rag_system, 'initialized') and rag_system.initialized:
            try:
                # Get relevant knowledge for the specific question
                knowledge_results = rag_system.search_knowledge(message, n_results=3)
                rag_context['knowledge_base'] = "\n".join([result['text'] for result in knowledge_results])
                
                # Get similar resume insights
                similar_resumes = rag_system.search_similar_resumes(resume_text, n_results=2)
                rag_context['similar_cases'] = "\n".join([f"Similar case: {res['text'][:200]}..." for res in similar_resumes])
    except Exception as e:
                print(f"Warning: Failed to get RAG context for chat: {e}")
        
        if resume_text:
            prompt = f"""
            You are an expert HR AI assistant helping with resume analysis and career advice. 
            The user has uploaded a resume and is asking questions about it.
            
            Use the following HR knowledge base to provide more accurate and helpful advice:
            
            KNOWLEDGE BASE:
            {rag_context.get('knowledge_base', '')}
            
            SIMILAR CASES:
            {rag_context.get('similar_cases', '')}
            
            Resume content:
            {resume_text}
            
            User question: {message}
            
            Please provide helpful, specific advice based on the resume content and HR best practices. 
            Focus on practical suggestions, career guidance, and improvement tips.
            Structure your response clearly with actionable recommendations.
            """
        else:
            prompt = f"""
            You are an expert HR AI assistant helping with resume analysis and career advice.
            The user is asking: {message}
            
            Use the following HR knowledge base to provide more accurate and helpful advice:
            
            KNOWLEDGE BASE:
            {rag_context.get('knowledge_base', '')}
            
            Please provide general career advice and resume tips based on HR best practices. 
            If they haven't uploaded a resume yet, suggest they do so for more specific feedback.
            Structure your response clearly with actionable recommendations.
            """
        
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": "You are a helpful HR AI assistant specializing in resume analysis and career advice."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        ai_response = response.choices[0].message.content
        
        return jsonify({
            'response': ai_response,
            'rag_enhanced': bool(rag_context)
        })
        
    except Exception as e:
        return jsonify({'error': f'Chat failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
