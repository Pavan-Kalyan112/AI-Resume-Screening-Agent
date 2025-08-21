import os
import json
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime
import pickle

class ResumeRAGSystem:
    def __init__(self, persist_directory: str = "rag_database"):
        """
        Initialize the RAG system for resume screening
        
        Args:
            persist_directory: Directory to persist the vector database
        """
        self.persist_directory = persist_directory
        
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize ChromaDB
            self.client = chromadb.PersistentClient(path=persist_directory)
            
            # Create collections for different types of data
            self.resume_collection = self.client.get_or_create_collection(
                name="resumes",
                metadata={"description": "Resume embeddings and metadata"}
            )
            
            self.jd_collection = self.client.get_or_create_collection(
                name="job_descriptions",
                metadata={"description": "Job description embeddings and metadata"}
            )
            
            self.knowledge_collection = self.client.get_or_create_collection(
                name="screening_knowledge",
                metadata={"description": "HR knowledge base and best practices"}
            )
            
            # Initialize knowledge base
            self._initialize_knowledge_base()
            
            self.initialized = True
        except Exception as e:
            print(f"Warning: RAG system initialization failed: {e}")
            self.initialized = False
            self.client = None
            self.resume_collection = None
            self.jd_collection = None
            self.knowledge_collection = None
            self.embedding_model = None
    
    def _initialize_knowledge_base(self):
        """Initialize the HR knowledge base with best practices"""
        if not self.initialized:
            return
            
        try:
            knowledge_base = [
            {
                "text": "Technical skills should be evaluated based on relevance to the job requirements and proficiency level indicated in the resume.",
                "metadata": {"category": "skill_evaluation", "importance": "high"}
            },
            {
                "text": "Experience should be assessed considering both duration and quality of work, including achievements and responsibilities.",
                "metadata": {"category": "experience_evaluation", "importance": "high"}
            },
            {
                "text": "Education requirements vary by role; technical positions may prioritize skills over formal education, while management roles often require specific degrees.",
                "metadata": {"category": "education_evaluation", "importance": "medium"}
            },
            {
                "text": "Red flags include gaps in employment without explanation, inconsistent information, and lack of quantifiable achievements.",
                "metadata": {"category": "red_flags", "importance": "high"}
            },
            {
                "text": "Cultural fit is important and can be assessed through volunteer work, interests, and communication style in the resume.",
                "metadata": {"category": "cultural_fit", "importance": "medium"}
            },
            {
                "text": "Leadership experience is valuable for senior positions and can be demonstrated through project management, team leadership, or mentorship.",
                "metadata": {"category": "leadership", "importance": "medium"}
            },
            {
                "text": "Certifications and professional development show commitment to continuous learning and staying current in the field.",
                "metadata": {"category": "certifications", "importance": "medium"}
            },
            {
                "text": "Industry-specific experience is often more valuable than general experience, especially for specialized roles.",
                "metadata": {"category": "industry_experience", "importance": "high"}
            },
            {
                "text": "Quantifiable achievements with metrics and numbers are more impressive than generic responsibilities.",
                "metadata": {"category": "achievements", "importance": "high"}
            },
            {
                "text": "Technology stack alignment with job requirements is crucial for technical positions.",
                "metadata": {"category": "tech_stack", "importance": "high"}
            }
        ]
        
                    # Add knowledge to collection if empty
            if self.knowledge_collection.count() == 0:
                for i, knowledge in enumerate(knowledge_base):
                    self.knowledge_collection.add(
                        documents=[knowledge["text"]],
                        metadatas=[knowledge["metadata"]],
                        ids=[f"knowledge_{i}"]
                    )
        except Exception as e:
            print(f"Error initializing knowledge base: {e}")
    
    def add_resume(self, resume_id: str, resume_text: str, metadata: Dict[str, Any]):
        """
        Add a resume to the vector database
        
        Args:
            resume_id: Unique identifier for the resume
            resume_text: Text content of the resume
            metadata: Additional metadata about the resume
        """
        if not self.initialized:
            print("Warning: RAG system not initialized, skipping resume addition")
            return
            
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(resume_text).tolist()
            
            # Add to collection
            self.resume_collection.add(
                documents=[resume_text],
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[resume_id]
            )
        except Exception as e:
            print(f"Error adding resume to RAG system: {e}")
            raise
    
    def add_job_description(self, jd_id: str, jd_text: str, metadata: Dict[str, Any]):
        """
        Add a job description to the vector database
        
        Args:
            jd_id: Unique identifier for the job description
            jd_text: Text content of the job description
            metadata: Additional metadata about the job description
        """
        if not self.initialized:
            print("Warning: RAG system not initialized, skipping job description addition")
            return
            
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(jd_text).tolist()
            
            # Add to collection
            self.jd_collection.add(
                documents=[jd_text],
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[jd_id]
            )
        except Exception as e:
            print(f"Error adding job description to RAG system: {e}")
            raise
    
    def search_similar_resumes(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for resumes similar to the query
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of similar resumes with metadata
        """
        if not self.initialized:
            return []
            
        try:
            query_embedding = self.embedding_model.encode(query).tolist()
            
            results = self.resume_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            return [
                {
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                }
                for i in range(len(results["ids"][0]))
            ]
        except Exception as e:
            print(f"Error searching similar resumes: {e}")
            return []
    
    def search_similar_jobs(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for job descriptions similar to the query
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of similar job descriptions with metadata
        """
        if not self.initialized:
            return []
            
        try:
            query_embedding = self.embedding_model.encode(query).tolist()
            
            results = self.jd_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            return [
                {
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                }
                for i in range(len(results["ids"][0]))
            ]
        except Exception as e:
            print(f"Error searching similar jobs: {e}")
            return []
    
    def get_relevant_knowledge(self, query: str, n_results: int = 3) -> List[str]:
        """
        Retrieve relevant HR knowledge for the query
        
        Args:
            query: Search query
            n_results: Number of knowledge items to return
            
        Returns:
            List of relevant knowledge texts
        """
        if not self.initialized:
            return []
            
        try:
            query_embedding = self.embedding_model.encode(query).tolist()
            
            results = self.knowledge_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            return results["documents"][0]
        except Exception as e:
            print(f"Error getting relevant knowledge: {e}")
            return []
    
    def semantic_resume_match(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """
        Perform semantic matching between resume and job description
        
        Args:
            resume_text: Resume content
            job_description: Job description content
            
        Returns:
            Dictionary with match analysis
        """
        if not self.initialized:
            return {
                "semantic_similarity": 0.0,
                "match_score": 0.0,
                "relevant_knowledge": [],
                "similar_resumes": [],
                "similar_jobs": [],
                "analysis_context": {
                    "total_resumes_in_db": 0,
                    "total_jobs_in_db": 0,
                    "knowledge_items": 0
                }
            }
            
        try:
            # Generate embeddings
            resume_embedding = self.embedding_model.encode(resume_text)
            jd_embedding = self.embedding_model.encode(job_description)
            
            # Calculate cosine similarity
            similarity = np.dot(resume_embedding, jd_embedding) / (
                np.linalg.norm(resume_embedding) * np.linalg.norm(jd_embedding)
            )
            
            # Get relevant knowledge for context
            relevant_knowledge = self.get_relevant_knowledge(
                f"resume matching job description skills experience"
            )
            
            # Find similar resumes and jobs for context
            similar_resumes = self.search_similar_resumes(job_description, n_results=3)
            similar_jobs = self.search_similar_jobs(resume_text, n_results=3)
            
            return {
                "semantic_similarity": float(similarity),
                "match_score": float(similarity * 100),
                "relevant_knowledge": relevant_knowledge,
                "similar_resumes": similar_resumes,
                "similar_jobs": similar_jobs,
                "analysis_context": {
                    "total_resumes_in_db": self.resume_collection.count(),
                    "total_jobs_in_db": self.jd_collection.count(),
                    "knowledge_items": self.knowledge_collection.count()
                }
            }
        except Exception as e:
            print(f"Error in semantic resume match: {e}")
            return {
                "semantic_similarity": 0.0,
                "match_score": 0.0,
                "relevant_knowledge": [],
                "similar_resumes": [],
                "similar_jobs": [],
                "analysis_context": {
                    "total_resumes_in_db": 0,
                    "total_jobs_in_db": 0,
                    "knowledge_items": 0
                }
            }
    
    def get_resume_insights(self, resume_text: str) -> Dict[str, Any]:
        """
        Get insights about a resume using RAG
        
        Args:
            resume_text: Resume content
            
        Returns:
            Dictionary with insights and recommendations
        """
        if not self.initialized:
            return {
                "skill_insights": [],
                "experience_insights": [],
                "red_flags_insights": [],
                "similar_resumes": [],
                "industry_insights": [],
                "database_context": {
                    "total_resumes": 0,
                    "total_jobs": 0
                }
            }
            
        try:
            # Get relevant knowledge
            skill_knowledge = self.get_relevant_knowledge("technical skills evaluation", n_results=2)
            experience_knowledge = self.get_relevant_knowledge("experience assessment", n_results=2)
            red_flags_knowledge = self.get_relevant_knowledge("red flags resume", n_results=2)
            
            # Find similar resumes for comparison
            similar_resumes = self.search_similar_resumes(resume_text, n_results=3)
            
            # Get industry insights
            industry_insights = self.get_relevant_knowledge("industry experience requirements", n_results=1)
            
            return {
                "skill_insights": skill_knowledge,
                "experience_insights": experience_knowledge,
                "red_flags_insights": red_flags_knowledge,
                "similar_resumes": similar_resumes,
                "industry_insights": industry_insights,
                "database_context": {
                    "total_resumes": self.resume_collection.count(),
                    "total_jobs": self.jd_collection.count()
                }
            }
        except Exception as e:
            print(f"Error getting resume insights: {e}")
            return {
                "skill_insights": [],
                "experience_insights": [],
                "red_flags_insights": [],
                "similar_resumes": [],
                "industry_insights": [],
                "database_context": {
                    "total_resumes": 0,
                    "total_jobs": 0
                }
            }
    
    def batch_semantic_analysis(self, resumes: List[Dict[str, Any]], job_description: str) -> List[Dict[str, Any]]:
        """
        Perform semantic analysis on multiple resumes against a job description
        
        Args:
            resumes: List of resume dictionaries with 'id', 'text', and 'metadata'
            job_description: Job description text
            
        Returns:
            List of analysis results for each resume
        """
        results = []
        
        for resume in resumes:
            # Perform semantic matching
            match_result = self.semantic_resume_match(resume['text'], job_description)
            
            # Get resume insights
            insights = self.get_resume_insights(resume['text'])
            
            # Combine results
            analysis_result = {
                "resume_id": resume['id'],
                "resume_metadata": resume['metadata'],
                "semantic_match": match_result,
                "insights": insights,
                "overall_score": match_result['match_score'],
                "recommendations": self._generate_recommendations(match_result, insights)
            }
            
            results.append(analysis_result)
        
        # Sort by overall score
        results.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return results
    
    def _generate_recommendations(self, match_result: Dict[str, Any], insights: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on match results and insights
        
        Args:
            match_result: Semantic match results
            insights: Resume insights
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Score-based recommendations
        if match_result['match_score'] < 30:
            recommendations.append("Low match score - consider if this role is the right fit")
        elif match_result['match_score'] < 60:
            recommendations.append("Moderate match - review specific skill gaps")
        else:
            recommendations.append("Strong match - proceed with detailed evaluation")
        
        # Knowledge-based recommendations
        if insights['skill_insights']:
            recommendations.append("Focus on technical skill alignment with role requirements")
        
        if insights['experience_insights']:
            recommendations.append("Evaluate experience quality and relevance to position")
        
        if insights['red_flags_insights']:
            recommendations.append("Review for potential red flags or inconsistencies")
        
        return recommendations
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG database
        
        Returns:
            Dictionary with database statistics
        """
        if not self.initialized:
            return {
                "resumes_count": 0,
                "jobs_count": 0,
                "knowledge_count": 0,
                "total_embeddings": 0,
                "status": "not_initialized"
            }
            
        try:
            return {
                "resumes_count": self.resume_collection.count(),
                "jobs_count": self.jd_collection.count(),
                "knowledge_count": self.knowledge_collection.count(),
                "total_embeddings": (
                    self.resume_collection.count() + 
                    self.jd_collection.count() + 
                    self.knowledge_collection.count()
                ),
                "status": "initialized"
            }
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {
                "resumes_count": 0,
                "jobs_count": 0,
                "knowledge_count": 0,
                "total_embeddings": 0,
                "status": "error"
            }
    
    def clear_database(self):
        """Clear all data from the RAG database"""
        if not self.initialized:
            print("Warning: RAG system not initialized, cannot clear database")
            return
            
        try:
            self.client.delete_collection("resumes")
            self.client.delete_collection("job_descriptions")
            self.client.delete_collection("screening_knowledge")
            
            # Recreate collections
            self.resume_collection = self.client.create_collection(
                name="resumes",
                metadata={"description": "Resume embeddings and metadata"}
            )
            
            self.jd_collection = self.client.create_collection(
                name="job_descriptions",
                metadata={"description": "Job description embeddings and metadata"}
            )
            
            self.knowledge_collection = self.client.create_collection(
                name="screening_knowledge",
                metadata={"description": "HR knowledge base and best practices"}
            )
            
            # Reinitialize knowledge base
            self._initialize_knowledge_base()
        except Exception as e:
            print(f"Error clearing database: {e}")
            raise

# Global RAG system instance
rag_system = None

def get_rag_system():
    """Get or create the global RAG system instance"""
    global rag_system
    if rag_system is None:
        rag_system = ResumeRAGSystem()
    return rag_system
