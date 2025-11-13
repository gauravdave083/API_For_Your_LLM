import os
import re
from typing import List, Dict, Any
from django.conf import settings
import PyPDF2
from docx import Document as DocxDocument
import logging

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Service for processing and chunking documents"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or getattr(settings, 'CHUNK_SIZE', 500)
        self.chunk_overlap = chunk_overlap or getattr(settings, 'CHUNK_OVERLAP', 100)
    
    def extract_text_from_file(self, file_path: str, file_type: str) -> str:
        """Extract text content from various file types"""
        try:
            if file_type == '.txt':
                return self._extract_from_txt(file_path)
            elif file_type == '.pdf':
                return self._extract_from_pdf(file_path)
            elif file_type in ['.docx', '.doc']:
                return self._extract_from_docx(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            raise
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from .txt file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read()
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from .pdf file"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from .docx file"""
        doc = DocxDocument(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:\-()]', '', text)
        return text.strip()
    
    def split_text_into_chunks(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Split text into chunks with overlap"""
        if not text:
            return []
        
        # Split by sentences first
        sentences = re.split(r'[.!?]+', text)
        
        chunks = []
        current_chunk = ""
        current_length = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_length = len(sentence)
            
            # If adding this sentence would exceed chunk size
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_metadata = metadata.copy() if metadata else {}
                chunk_metadata.update({
                    'chunk_index': chunk_index,
                    'start_char': len(''.join(chunks)) * self.chunk_size if chunks else 0,
                    'end_char': len(current_chunk),
                })
                
                chunks.append({
                    'text': current_chunk.strip(),
                    'metadata': chunk_metadata,
                    'index': chunk_index
                })
                
                chunk_index += 1
                
                # Start new chunk with overlap
                if self.chunk_overlap > 0:
                    overlap_text = current_chunk[-self.chunk_overlap:]
                    current_chunk = overlap_text + " " + sentence
                    current_length = len(current_chunk)
                else:
                    current_chunk = sentence
                    current_length = sentence_length
            else:
                # Add sentence to current chunk
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
                current_length += sentence_length
        
        # Add the last chunk if it exists
        if current_chunk.strip():
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata.update({
                'chunk_index': chunk_index,
                'start_char': len(''.join(chunks)) * self.chunk_size if chunks else 0,
                'end_char': len(current_chunk),
            })
            
            chunks.append({
                'text': current_chunk.strip(),
                'metadata': chunk_metadata,
                'index': chunk_index
            })
        
        return chunks
    
    def process_document(self, document) -> List[Dict[str, Any]]:
        """Process a document and return chunks"""
        try:
            # Extract text from file
            file_path = document.file.path
            text = self.extract_text_from_file(file_path, document.file_type)
            
            # Clean text
            cleaned_text = self.clean_text(text)
            
            # Update document with extracted content
            document.content = cleaned_text[:1000]  # Store first 1000 chars as preview
            document.save()
            
            # Create metadata
            metadata = {
                'document_id': document.id,
                'title': document.title,
                'file_type': document.file_type,
                'upload_date': document.upload_date.isoformat(),
                'file_size': document.file_size
            }
            
            # Split into chunks
            chunks = self.split_text_into_chunks(cleaned_text, metadata)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing document {document.id}: {str(e)}")
            raise