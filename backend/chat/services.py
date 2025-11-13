import os
import logging
import time
from typing import List, Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class BaseLLMService:
    """Base class for LLM services"""
    
    def __init__(self):
        self.model_type = getattr(settings, 'LLM_MODEL_TYPE', 'gpt4all')
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response from LLM"""
        raise NotImplementedError
    
    def is_available(self) -> bool:
        """Check if LLM service is available"""
        raise NotImplementedError


class GPT4AllService(BaseLLMService):
    """Service for GPT4All local LLM"""
    
    def __init__(self):
        super().__init__()
        self.model = None
        self.model_path = getattr(settings, 'GPT4ALL_MODEL_PATH', 'models')
        self._load_model()
    
    def _load_model(self):
        """Load GPT4All model"""
        try:
            from gpt4all import GPT4All
            
            # Ensure model directory exists
            os.makedirs(self.model_path, exist_ok=True)
            
            # Try to load a default model
            model_names = [
                'mistral-7b-openorca.Q4_0.gguf',
                'orca-mini-3b-gguf2-q4_0.gguf',
                'nous-hermes-llama2-13b.q4_0.bin'
            ]
            
            for model_name in model_names:
                try:
                    logger.info(f"Attempting to load GPT4All model: {model_name}")
                    self.model = GPT4All(model_name, model_path=self.model_path)
                    logger.info(f"Successfully loaded GPT4All model: {model_name}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to load model {model_name}: {str(e)}")
                    continue
            
            if self.model is None:
                logger.error("Failed to load any GPT4All model")
                
        except ImportError:
            logger.error("GPT4All not installed. Install with: pip install gpt4all")
        except Exception as e:
            logger.error(f"Error loading GPT4All model: {str(e)}")
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using GPT4All"""
        try:
            if self.model is None:
                return "Error: GPT4All model not available"
            
            # Construct full prompt with context
            if context:
                full_prompt = f"""Context information:
{context}

Question: {prompt}

Answer based on the context provided above:"""
            else:
                full_prompt = prompt
            
            # Generate response
            response = self.model.generate(
                full_prompt,
                max_tokens=512,
                temp=0.7,
                top_k=40,
                top_p=0.4,
                repeat_penalty=1.18,
                repeat_last_n=64,
                n_batch=8,
                n_predict=None,
                streaming=False
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating GPT4All response: {str(e)}")
            return f"Error generating response: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if GPT4All is available"""
        return self.model is not None


class OllamaService(BaseLLMService):
    """Service for Ollama local LLM"""
    
    def __init__(self):
        super().__init__()
        self.base_url = getattr(settings, 'OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model_name = getattr(settings, 'OLLAMA_MODEL_NAME', 'llama2')
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using Ollama"""
        try:
            import requests
            
            # Construct full prompt with context
            if context:
                full_prompt = f"""Context information:
{context}

Question: {prompt}

Answer based on the context provided above:"""
            else:
                full_prompt = prompt
            
            # Make request to Ollama API
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_k": 40,
                        "top_p": 0.4,
                        "repeat_penalty": 1.18
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return f"Error: Ollama API returned {response.status_code}"
                
        except ImportError:
            logger.error("Requests library not installed")
            return "Error: Requests library required for Ollama"
        except requests.RequestException as e:
            logger.error(f"Error connecting to Ollama: {str(e)}")
            return f"Error connecting to Ollama: {str(e)}"
        except Exception as e:
            logger.error(f"Error generating Ollama response: {str(e)}")
            return f"Error generating response: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/version", timeout=5)
            return response.status_code == 200
        except:
            return False


class RAGService:
    """Service for Retrieval Augmented Generation"""
    
    def __init__(self, llm_service: BaseLLMService = None):
        self.llm_service = llm_service or self._get_default_llm_service()
        self.max_context_chunks = 5
        self.context_chunk_separator = "\n\n---\n\n"
    
    def _get_default_llm_service(self) -> BaseLLMService:
        """Get default LLM service based on settings"""
        model_type = getattr(settings, 'LLM_MODEL_TYPE', 'gpt4all')
        
        if model_type == 'ollama':
            service = OllamaService()
            if service.is_available():
                return service
            logger.warning("Ollama not available, falling back to GPT4All")
        
        return GPT4AllService()
    
    def generate_rag_response(self, query: str, context_chunks: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate response using RAG approach"""
        try:
            start_time = time.time()
            
            # Get relevant context if not provided
            if context_chunks is None:
                context_chunks = self._get_relevant_context(query)
            
            # Prepare context string
            context_text = self._prepare_context_text(context_chunks)
            
            # Generate response
            response = self.llm_service.generate_response(query, context_text)
            
            generation_time = time.time() - start_time
            
            return {
                'response': response,
                'context_chunks': context_chunks,
                'generation_time_ms': generation_time * 1000,
                'llm_service': self.llm_service.__class__.__name__,
                'context_used': len(context_chunks) > 0
            }
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {str(e)}")
            return {
                'response': f"Error generating response: {str(e)}",
                'context_chunks': [],
                'generation_time_ms': 0,
                'llm_service': self.llm_service.__class__.__name__,
                'context_used': False,
                'error': str(e)
            }
    
    def _get_relevant_context(self, query: str) -> List[Dict[str, Any]]:
        """Get relevant context chunks for the query"""
        try:
            from embeddings.services import VectorStoreService
            
            vector_store = VectorStoreService()
            similar_chunks = vector_store.search_similar(query, k=self.max_context_chunks)
            
            return similar_chunks
            
        except Exception as e:
            logger.error(f"Error getting relevant context: {str(e)}")
            return []
    
    def _prepare_context_text(self, context_chunks: List[Dict[str, Any]]) -> str:
        """Prepare context text from chunks"""
        if not context_chunks:
            return ""
        
        context_parts = []
        for i, chunk in enumerate(context_chunks[:self.max_context_chunks], 1):
            context_part = f"Document: {chunk.get('document_title', 'Unknown')}\n"
            context_part += f"Content: {chunk.get('chunk_text', '')}"
            context_parts.append(context_part)
        
        return self.context_chunk_separator.join(context_parts)
    
    def get_llm_status(self) -> Dict[str, Any]:
        """Get LLM service status"""
        return {
            'service_type': self.llm_service.__class__.__name__,
            'is_available': self.llm_service.is_available(),
            'model_type': getattr(settings, 'LLM_MODEL_TYPE', 'gpt4all')
        }