"""
Context Engine - Project-wide code understanding and context awareness
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import hashlib

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False


class ContextEngine:
    """
    Context Engine for Legion - provides project-wide code understanding.
    Uses vector databases to index and retrieve relevant code context.
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.cache_dir = self.project_root / ".legion" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # File tracking
        self.indexed_files: Set[str] = set()
        self.file_hashes: Dict[str, str] = {}

        # Vector database
        self.vector_db = None
        self.collection = None
        self._initialize_vector_db()

        # Supported file types for indexing
        self.supported_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.php',
            '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.clj',
            '.hs', '.ml', '.fs', '.elm', '.dart', '.lua', '.r',
            '.sh', '.bash', '.ps1', '.sql', '.html', '.css', '.scss',
            '.xml', '.json', '.yaml', '.yml', '.toml', '.md'
        }

    def _initialize_vector_db(self):
        """Initialize the vector database for code indexing"""
        if not CHROMA_AVAILABLE:
            print("Warning: ChromaDB not available. Context Engine will work in limited mode.")
            return

        try:
            # Initialize ChromaDB client
            db_path = self.cache_dir / "vector_db"
            client = chromadb.PersistentClient(
                path=str(db_path),
                settings=Settings(anonymized_telemetry=False)
            )

            # Create or get collection
            collection_name = "legion_code_context"
            try:
                self.collection = client.get_collection(collection_name)
            except:
                self.collection = client.create_collection(
                    name=collection_name,
                    metadata={"description": "Legion code context and relationships"}
                )

            self.vector_db = client
            print(f"✅ Context Engine initialized with vector database at {db_path}")

        except Exception as e:
            print(f"Warning: Failed to initialize vector database: {e}")
            self.vector_db = None

    def is_indexed(self) -> bool:
        """Check if the project has been indexed"""
        return len(self.indexed_files) > 0

    def index_project(self, force_reindex: bool = False):
        """
        Index the entire project for context awareness.

        Args:
            force_reindex: If True, reindex all files regardless of changes
        """
        print("🔍 Indexing project for context awareness...")

        indexed_count = 0
        updated_count = 0

        for file_path in self._get_project_files():
            if self._should_index_file(file_path, force_reindex):
                try:
                    self._index_file(file_path)
                    if str(file_path) in self.indexed_files:
                        updated_count += 1
                    else:
                        indexed_count += 1
                    self.indexed_files.add(str(file_path))
                except Exception as e:
                    print(f"Warning: Failed to index {file_path}: {e}")

        print(f"✅ Project indexing complete: {indexed_count} new files, {updated_count} updated")

    def _get_project_files(self) -> List[Path]:
        """Get all supported files in the project"""
        files = []
        for ext in self.supported_extensions:
            files.extend(self.project_root.rglob(f"*{ext}"))

        # Exclude common directories
        exclude_patterns = [
            ".git", "__pycache__", "node_modules", ".legion",
            "build", "dist", ".next", ".nuxt", "target", "bin", "obj"
        ]

        filtered_files = []
        for file_path in files:
            if not any(pattern in str(file_path) for pattern in exclude_patterns):
                filtered_files.append(file_path)

        return filtered_files

    def _should_index_file(self, file_path: Path, force_reindex: bool) -> bool:
        """Determine if a file should be indexed"""
        if force_reindex:
            return True

        if not file_path.exists():
            return False

        # Check if file has been modified
        current_hash = self._get_file_hash(file_path)
        previous_hash = self.file_hashes.get(str(file_path))

        if current_hash != previous_hash:
            self.file_hashes[str(file_path)] = current_hash
            return True

        return False

    def _get_file_hash(self, file_path: Path) -> str:
        """Get MD5 hash of file content"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def _index_file(self, file_path: Path):
        """Index a single file into the vector database"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if not content.strip():
                return

            # Split content into meaningful chunks
            chunks = self._split_into_chunks(content, file_path)

            if self.collection:
                # Add chunks to vector database
                documents = []
                metadatas = []
                ids = []

                for i, chunk in enumerate(chunks):
                    chunk_id = f"{file_path.relative_to(self.project_root)}_{i}"
                    documents.append(chunk["content"])
                    metadatas.append({
                        "file_path": str(file_path.relative_to(self.project_root)),
                        "line_start": chunk["line_start"],
                        "line_end": chunk["line_end"],
                        "chunk_type": chunk["type"],
                        "language": self._detect_language(file_path)
                    })
                    ids.append(chunk_id)

                if documents:
                    self.collection.add(
                        documents=documents,
                        metadatas=metadatas,
                        ids=ids
                    )

        except Exception as e:
            print(f"Error indexing file {file_path}: {e}")

    def _split_into_chunks(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Split file content into meaningful chunks for indexing"""
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_line_start = 1
        in_function = False
        in_class = False

        for i, line in enumerate(lines, 1):
            line = line.strip()

            # Detect function/class boundaries
            if self._is_function_start(line, file_path):
                # Save previous chunk if it exists
                if current_chunk:
                    chunks.append({
                        "content": '\n'.join(current_chunk),
                        "line_start": current_line_start,
                        "line_end": i - 1,
                        "type": "function" if in_function else "class" if in_class else "block"
                    })

                current_chunk = [line]
                current_line_start = i
                in_function = "def " in line or "function " in line or "func " in line
                in_class = "class " in line

            elif line == "" and len(current_chunk) > 10:
                # Split on empty lines for long blocks
                if current_chunk:
                    chunks.append({
                        "content": '\n'.join(current_chunk),
                        "line_start": current_line_start,
                        "line_end": i - 1,
                        "type": "function" if in_function else "class" if in_class else "block"
                    })
                    current_chunk = []
                    current_line_start = i + 1

            else:
                current_chunk.append(line)

        # Add final chunk
        if current_chunk:
            chunks.append({
                "content": '\n'.join(current_chunk),
                "line_start": current_line_start,
                "line_end": len(lines),
                "type": "function" if in_function else "class" if in_class else "block"
            })

        return chunks

    def _is_function_start(self, line: str, file_path: Path) -> bool:
        """Detect if a line starts a function or class definition"""
        ext = file_path.suffix.lower()

        if ext == '.py':
            return line.startswith(('def ', 'class ', 'async def '))
        elif ext in ['.js', '.ts']:
            return line.startswith(('function ', 'const ', 'let ', 'var ')) and ('=>' in line or '(' in line)
        elif ext == '.java':
            return line.startswith(('public ', 'private ', 'protected ')) and ('(' in line or ' class ' in line)
        elif ext == '.cpp':
            return line.startswith(('void ', 'int ', 'bool ', 'class ')) and ('(' in line or '{' in line)
        elif ext == '.cs':
            return line.startswith(('public ', 'private ', 'protected ')) and ('(' in line or ' class ' in line)

        return False

    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension"""
        ext_to_lang = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.java': 'java', '.cpp': 'cpp', '.c': 'c', '.cs': 'csharp',
            '.php': 'php', '.rb': 'ruby', '.go': 'go', '.rs': 'rust',
            '.swift': 'swift', '.kt': 'kotlin', '.scala': 'scala',
            '.clj': 'clojure', '.hs': 'haskell', '.ml': 'ocaml',
            '.fs': 'fsharp', '.elm': 'elm', '.dart': 'dart',
            '.lua': 'lua', '.r': 'r', '.sh': 'bash', '.bash': 'bash',
            '.ps1': 'powershell', '.sql': 'sql', '.html': 'html',
            '.css': 'css', '.scss': 'scss', '.xml': 'xml',
            '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml',
            '.toml': 'toml', '.md': 'markdown'
        }
        return ext_to_lang.get(file_path.suffix.lower(), 'unknown')

    def get_relevant_context(self, task: str, current_file: str = "",
                           current_code: str = "", user_preferences: Optional[Dict] = None,
                           n_chunks: int = 5) -> Dict[str, Any]:
        """
        Get relevant context for a task from the indexed project.

        Args:
            task: Description of the task
            current_file: Path to the current file being worked on
            current_code: Current code content
            user_preferences: User preferences for context filtering
            n_chunks: Number of relevant chunks to return

        Returns:
            Dictionary containing relevant context
        """
        if not self.collection:
            return self._get_basic_context(task, current_file, current_code)

        try:
            # Create search query from task and current code
            search_query = f"{task} {current_code[:500]}"  # Limit current code length

            # Search for relevant chunks
            results = self.collection.query(
                query_texts=[search_query],
                n_results=n_chunks * 2,  # Get more results for filtering
                include=['documents', 'metadatas', 'distances']
            )

            # Filter and rank results
            relevant_chunks = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i]

                    # Skip current file chunks unless they're highly relevant
                    if (metadata['file_path'] == current_file and distance > 0.3):
                        continue

                    relevant_chunks.append({
                        "content": doc,
                        "file_path": metadata['file_path'],
                        "line_start": metadata['line_start'],
                        "line_end": metadata['line_end'],
                        "chunk_type": metadata['chunk_type'],
                        "language": metadata['language'],
                        "relevance_score": 1.0 - distance  # Convert distance to relevance
                    })

            # Sort by relevance and take top n_chunks
            relevant_chunks.sort(key=lambda x: x['relevance_score'], reverse=True)
            relevant_chunks = relevant_chunks[:n_chunks]

            return {
                "related_code": [chunk["content"] for chunk in relevant_chunks],
                "related_files": list(set(chunk["file_path"] for chunk in relevant_chunks)),
                "context_chunks": relevant_chunks,
                "current_file": current_file,
                "search_query": search_query
            }

        except Exception as e:
            print(f"Warning: Vector search failed, falling back to basic context: {e}")
            return self._get_basic_context(task, current_file, current_code)

    def _get_basic_context(self, task: str, current_file: str, current_code: str) -> Dict[str, Any]:
        """Fallback context gathering without vector database"""
        return {
            "related_code": [current_code[:1000]] if current_code else [],
            "related_files": [current_file] if current_file else [],
            "context_chunks": [],
            "current_file": current_file,
            "fallback_mode": True
        }

    def get_file_context(self, file_path: str) -> Dict[str, Any]:
        """Get context information for a specific file"""
        full_path = self.project_root / file_path

        if not full_path.exists():
            return {"error": "File not found"}

        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Get related chunks from vector database
            related_chunks = []
            if self.collection:
                results = self.collection.query(
                    query_texts=[content[:500]],
                    where={"file_path": file_path},
                    n_results=10
                )

                if results['documents']:
                    for i, doc in enumerate(results['documents'][0]):
                        metadata = results['metadatas'][0][i]
                        related_chunks.append({
                            "content": doc,
                            "line_start": metadata['line_start'],
                            "line_end": metadata['line_end'],
                            "chunk_type": metadata['chunk_type']
                        })

            return {
                "file_path": file_path,
                "content": content,
                "line_count": len(content.split('\n')),
                "related_chunks": related_chunks,
                "language": self._detect_language(full_path)
            }

        except Exception as e:
            return {"error": f"Failed to read file: {e}"}

    def get_project_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed project"""
        if not self.collection:
            return {"error": "Vector database not available"}

        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "indexed_files": len(self.indexed_files),
                "supported_extensions": list(self.supported_extensions),
                "cache_location": str(self.cache_dir)
            }
        except Exception as e:
            return {"error": f"Failed to get stats: {e}"}