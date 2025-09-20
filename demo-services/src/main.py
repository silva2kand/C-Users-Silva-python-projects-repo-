#!/usr/bin/env python3
"""
Lightweight Ingest Service Demo
Demonstrates how the developer console's ingest component can be containerized
"""

import asyncio
import hashlib
import magic
import os
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import aiofiles
import chardet

# Initialize FastAPI app
app = FastAPI(
    title="Developer Console - Ingest Service",
    description="Lightweight file analysis and project ingestion service",
    version="1.0.0"
)

# Data models
class FileAnalysis(BaseModel):
    filename: str
    size: int
    hash_sha256: str
    mime_type: str
    encoding: Optional[str]
    language: Optional[str]
    is_text: bool
    line_count: Optional[int]

class ProjectAnalysis(BaseModel):
    project_name: str
    total_files: int
    total_size: int
    languages: List[str]
    frameworks: List[str]
    files: List[FileAnalysis]
    entry_points: List[str]
    config_files: List[str]

# Language detection patterns
LANGUAGE_PATTERNS = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.go': 'Go',
    '.java': 'Java',
    '.rs': 'Rust',
    '.cpp': 'C++',
    '.c': 'C',
    '.cs': 'C#',
    '.php': 'PHP',
    '.rb': 'Ruby',
    '.swift': 'Swift',
    '.kt': 'Kotlin'
}

# Framework detection patterns
FRAMEWORK_PATTERNS = {
    'package.json': ['Node.js'],
    'requirements.txt': ['Python'],
    'pyproject.toml': ['Python'],
    'Cargo.toml': ['Rust'],
    'go.mod': ['Go'],
    'pom.xml': ['Java', 'Maven'],
    'build.gradle': ['Java', 'Gradle'],
    'composer.json': ['PHP'],
    'Gemfile': ['Ruby'],
    'Package.swift': ['Swift']
}

# Entry point patterns
ENTRY_POINT_PATTERNS = [
    'main.py', 'app.py', 'server.py', '__main__.py',
    'index.js', 'app.js', 'server.js', 'main.js',
    'main.go', 'cmd/main.go',
    'Main.java', 'Application.java',
    'main.rs', 'lib.rs'
]

class IngestService:
    """Core ingest service for file analysis"""
    
    def __init__(self):
        self.magic = magic.Magic(mime=True)
    
    async def analyze_file(self, file_path: Path, content: bytes) -> FileAnalysis:
        """Analyze a single file"""
        # Basic file info
        size = len(content)
        hash_sha256 = hashlib.sha256(content).hexdigest()
        mime_type = self.magic.from_buffer(content)
        
        # Detect encoding for text files
        encoding = None
        is_text = mime_type.startswith('text/') or 'text' in mime_type
        line_count = None
        
        if is_text:
            try:
                detected = chardet.detect(content)
                encoding = detected.get('encoding', 'utf-8')
                text_content = content.decode(encoding, errors='ignore')
                line_count = len(text_content.splitlines())
            except Exception:
                is_text = False
        
        # Detect language
        language = None
        suffix = file_path.suffix.lower()
        if suffix in LANGUAGE_PATTERNS:
            language = LANGUAGE_PATTERNS[suffix]
        
        return FileAnalysis(
            filename=file_path.name,
            size=size,
            hash_sha256=hash_sha256,
            mime_type=mime_type,
            encoding=encoding,
            language=language,
            is_text=is_text,
            line_count=line_count
        )
    
    async def analyze_project(self, files: List[tuple]) -> ProjectAnalysis:
        """Analyze entire project structure"""
        file_analyses = []
        languages = set()
        frameworks = set()
        entry_points = []
        config_files = []
        total_size = 0
        
        for file_path, content in files:
            analysis = await self.analyze_file(file_path, content)
            file_analyses.append(analysis)
            total_size += analysis.size
            
            # Collect languages
            if analysis.language:
                languages.add(analysis.language)
            
            # Detect frameworks
            filename = file_path.name
            if filename in FRAMEWORK_PATTERNS:
                frameworks.update(FRAMEWORK_PATTERNS[filename])
            
            # Detect entry points
            if filename in ENTRY_POINT_PATTERNS:
                entry_points.append(filename)
            
            # Detect config files
            if any(pattern in filename.lower() for pattern in ['config', 'settings', '.env', '.ini', '.yaml', '.yml', '.toml']):
                config_files.append(filename)
        
        # Infer project name (simplified)
        project_name = "unknown_project"
        if files:
            project_name = files[0][0].parent.name or "root_project"
        
        return ProjectAnalysis(
            project_name=project_name,
            total_files=len(file_analyses),
            total_size=total_size,
            languages=list(languages),
            frameworks=list(frameworks),
            files=file_analyses,
            entry_points=entry_points,
            config_files=config_files
        )

# Initialize service
ingest_service = IngestService()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ingest"}

@app.post("/analyze/file", response_model=FileAnalysis)
async def analyze_single_file(file: UploadFile = File(...)):
    """Analyze a single uploaded file"""
    try:
        content = await file.read()
        file_path = Path(file.filename or "unknown")
        analysis = await ingest_service.analyze_file(file_path, content)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/project", response_model=ProjectAnalysis)
async def analyze_project(files: List[UploadFile] = File(...)):
    """Analyze multiple files as a project"""
    try:
        file_data = []
        for file in files:
            content = await file.read()
            file_path = Path(file.filename or "unknown")
            file_data.append((file_path, content))
        
        analysis = await ingest_service.analyze_project(file_data)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project analysis failed: {str(e)}")

@app.get("/capabilities")
async def get_capabilities():
    """Get service capabilities"""
    return {
        "supported_languages": list(LANGUAGE_PATTERNS.values()),
        "supported_frameworks": list(set().union(*FRAMEWORK_PATTERNS.values())),
        "max_file_size": "100MB",
        "max_files_per_project": 1000,
        "features": [
            "file_hashing",
            "mime_type_detection",
            "encoding_detection",
            "language_detection",
            "framework_detection",
            "entry_point_detection",
            "config_file_detection"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )