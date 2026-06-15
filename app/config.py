import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Server configurations
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")

# Storage paths
CHROMA_PATH = os.getenv("CHROMA_DB_PATH", os.path.abspath("storage/db"))
UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.abspath("storage/uploads"))

# Collection configuration
COLLECTION_NAME = "text_collection"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# Chunker configuration
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# Ollama configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "phi3:mini")

# Ensure storage directories exist
os.makedirs(CHROMA_PATH, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Similarity Thresholds
CLIP_MIN_SCORE = float(os.getenv("CLIP_MIN_SCORE", 0.25))
TEXT_MIN_SCORE = float(os.getenv("TEXT_MIN_SCORE", 0.50))
VQA_MIN_SCORE = float(os.getenv("VQA_MIN_SCORE", 0.25))

# VQA configuration
VISION_MODEL = os.getenv("VISION_MODEL", "llava:7b")
VISION_URL = os.getenv("VISION_URL", "http://localhost:11434")
MAX_VQA_IMAGES = int(os.getenv("MAX_VQA_IMAGES", 3))
ENABLE_VISUAL_REASONING = os.getenv("ENABLE_VISUAL_REASONING", "True").lower() == "true"

# Scoring Weights
VISUAL_WEIGHT = 0.80
CATEGORY_BOOST_WEIGHT = 0.20
FUSION_TEXT_WEIGHT = 0.60
FUSION_VISUAL_WEIGHT = 0.40

# Milestone 7 Enhancements Configuration
ENABLE_VQA_CACHE = os.getenv("ENABLE_VQA_CACHE", "True").lower() == "true"
MAX_VQA_CANDIDATES = int(os.getenv("MAX_VQA_CANDIDATES", 3))
HIGH_CONFIDENCE_THRESHOLD = float(os.getenv("HIGH_CONFIDENCE_THRESHOLD", 0.75))
MEDIUM_CONFIDENCE_THRESHOLD = float(os.getenv("MEDIUM_CONFIDENCE_THRESHOLD", 0.50))
ENABLE_EXPLANATIONS = os.getenv("ENABLE_EXPLANATIONS", "True").lower() == "true"
ENABLE_VISUAL_CITATIONS = os.getenv("ENABLE_VISUAL_CITATIONS", "True").lower() == "true"
ENABLE_MULTI_IMAGE_REASONING = os.getenv("ENABLE_MULTI_IMAGE_REASONING", "True").lower() == "true"

# Milestone 8 Unified Evidence RAG Configuration
ENABLE_EVIDENCE_GRAPH = os.getenv("ENABLE_EVIDENCE_GRAPH", "True").lower() == "true"
TEXT_WEIGHT = float(os.getenv("TEXT_WEIGHT", 0.40))
VISUAL_WEIGHT = float(os.getenv("VISUAL_WEIGHT", 0.30))
AUDIO_WEIGHT = float(os.getenv("AUDIO_WEIGHT", 0.20))
SOURCE_QUALITY_WEIGHT = float(os.getenv("SOURCE_QUALITY_WEIGHT", 0.10))
MIN_EVIDENCE_SCORE = float(os.getenv("MIN_EVIDENCE_SCORE", 0.25))
MAX_EVIDENCE_ITEMS = int(os.getenv("MAX_EVIDENCE_ITEMS", 10))
ENABLE_GROUNDING_VALIDATION = os.getenv("ENABLE_GROUNDING_VALIDATION", "True").lower() == "true"

# Milestone 9 Conversational Memory Configuration
ENABLE_MEMORY = os.getenv("ENABLE_MEMORY", "True").lower() == "true"
MAX_CHAT_HISTORY = int(os.getenv("MAX_CHAT_HISTORY", 50))
MAX_SHORT_TERM_MEMORY = int(os.getenv("MAX_SHORT_TERM_MEMORY", 10))
ENABLE_MEMORY_SUMMARIZATION = os.getenv("ENABLE_MEMORY_SUMMARIZATION", "True").lower() == "true"
ENABLE_ENTITY_MEMORY = os.getenv("ENABLE_ENTITY_MEMORY", "True").lower() == "true"
ENABLE_PREFERENCE_MEMORY = os.getenv("ENABLE_PREFERENCE_MEMORY", "True").lower() == "true"
ENABLE_MEMORY_RETRIEVAL = os.getenv("ENABLE_MEMORY_RETRIEVAL", "True").lower() == "true"
MEMORY_WEIGHT = float(os.getenv("MEMORY_WEIGHT", 0.25))
SHORT_TERM_WEIGHT = float(os.getenv("SHORT_TERM_WEIGHT", 0.35))
LONG_TERM_WEIGHT = float(os.getenv("LONG_TERM_WEIGHT", 0.20))
ENTITY_WEIGHT = float(os.getenv("ENTITY_WEIGHT", 0.20))
SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", 60))
SUMMARY_INTERVAL = int(os.getenv("SUMMARY_INTERVAL", 5))

# Milestone 10 Agentic RAG Configuration
ENABLE_AGENTIC_RAG = os.getenv("ENABLE_AGENTIC_RAG", "True").lower() == "true"
MAX_AGENT_STEPS = int(os.getenv("MAX_AGENT_STEPS", 6))
MAX_REPLANNING_STEPS = int(os.getenv("MAX_REPLANNING_STEPS", 2))
MAX_OBSERVATION_MEMORY = int(os.getenv("MAX_OBSERVATION_MEMORY", 20))
MAX_TASK_MEMORY = int(os.getenv("MAX_TASK_MEMORY", 50))
AGENT_TIMEOUT_SECONDS = int(os.getenv("AGENT_TIMEOUT_SECONDS", 45))
TOOL_TIMEOUT_SECONDS = int(os.getenv("TOOL_TIMEOUT_SECONDS", 30))
ENABLE_REFLECTION = os.getenv("ENABLE_REFLECTION", "True").lower() == "true"
ENABLE_REPLANNING = os.getenv("ENABLE_REPLANNING", "True").lower() == "true"
ENABLE_AGENT_EXPLANATIONS = os.getenv("ENABLE_AGENT_EXPLANATIONS", "True").lower() == "true"
ENABLE_TRACE_CACHE = os.getenv("ENABLE_TRACE_CACHE", "True").lower() == "true"

OBSERVATION_WEIGHT = float(os.getenv("OBSERVATION_WEIGHT", 0.30))
TASK_WEIGHT = float(os.getenv("TASK_WEIGHT", 0.20))
MEMORY_WEIGHT_AGENT = float(os.getenv("MEMORY_WEIGHT_AGENT", 0.20))
EVIDENCE_WEIGHT = float(os.getenv("EVIDENCE_WEIGHT", 0.30))
LOW_CONFIDENCE_THRESHOLD = float(os.getenv("LOW_CONFIDENCE_THRESHOLD", 0.50))

# Milestone 11 Knowledge Graph Configuration
ENABLE_KNOWLEDGE_GRAPH = os.getenv("ENABLE_KNOWLEDGE_GRAPH", "True").lower() == "true"
ENABLE_RELATION_EXTRACTION = os.getenv("ENABLE_RELATION_EXTRACTION", "True").lower() == "true"
ENABLE_MULTI_HOP_REASONING = os.getenv("ENABLE_MULTI_HOP_REASONING", "True").lower() == "true"
ENABLE_TEMPORAL_EDGES = os.getenv("ENABLE_TEMPORAL_EDGES", "True").lower() == "true"
ENABLE_GRAPH_CACHE = os.getenv("ENABLE_GRAPH_CACHE", "True").lower() == "true"
ENABLE_GRAPH_EXPLANATIONS = os.getenv("ENABLE_GRAPH_EXPLANATIONS", "True").lower() == "true"
ENABLE_COMMUNITY_DETECTION = os.getenv("ENABLE_COMMUNITY_DETECTION", "True").lower() == "true"
ENABLE_RELATION_DECAY = os.getenv("ENABLE_RELATION_DECAY", "True").lower() == "true"
ENABLE_INCREMENTAL_GRAPH_UPDATES = os.getenv("ENABLE_INCREMENTAL_GRAPH_UPDATES", "True").lower() == "true"
ENABLE_GRAPH_MIGRATIONS = os.getenv("ENABLE_GRAPH_MIGRATIONS", "True").lower() == "true"
GRAPH_SCHEMA_VERSION = int(os.getenv("GRAPH_SCHEMA_VERSION", 1))

MAX_GRAPH_DEPTH = int(os.getenv("MAX_GRAPH_DEPTH", 3))
MAX_GRAPH_NEIGHBORS = int(os.getenv("MAX_GRAPH_NEIGHBORS", 10))
MAX_ENTITY_NEIGHBORS = int(os.getenv("MAX_ENTITY_NEIGHBORS", 20))
MAX_COMMUNITY_SIZE = int(os.getenv("MAX_COMMUNITY_SIZE", 50))
MAX_PATHS = int(os.getenv("MAX_PATHS", 20))
MAX_TOTAL_VISITED = int(os.getenv("MAX_TOTAL_VISITED", 100))

GRAPH_WEIGHT = float(os.getenv("GRAPH_WEIGHT", 0.25))
EVIDENCE_WEIGHT_KG = float(os.getenv("EVIDENCE_WEIGHT_KG", 0.35))
MEMORY_WEIGHT_KG = float(os.getenv("MEMORY_WEIGHT_KG", 0.20))
AGENT_WEIGHT_KG = float(os.getenv("AGENT_WEIGHT_KG", 0.20))

MIN_RELATION_CONFIDENCE = float(os.getenv("MIN_RELATION_CONFIDENCE", 0.50))
RELATION_DECAY_FACTOR = float(os.getenv("RELATION_DECAY_FACTOR", 0.95))
ENTITY_DECAY_FACTOR = float(os.getenv("ENTITY_DECAY_FACTOR", 0.98))
GRAPH_CACHE_SIZE = int(os.getenv("GRAPH_CACHE_SIZE", 100))
GRAPH_PRUNE_INTERVAL = int(os.getenv("GRAPH_PRUNE_INTERVAL", 50))

# Milestone 12 Self-Learning Configuration
ENABLE_SELF_LEARNING = os.getenv("ENABLE_SELF_LEARNING", "True").lower() == "true"
ENABLE_PATTERN_DISCOVERY = os.getenv("ENABLE_PATTERN_DISCOVERY", "True").lower() == "true"
ENABLE_CORRECTION_ENGINE = os.getenv("ENABLE_CORRECTION_ENGINE", "True").lower() == "true"
ENABLE_FEEDBACK_MEMORY = os.getenv("ENABLE_FEEDBACK_MEMORY", "True").lower() == "true"
ENABLE_LEARNING_CACHE = os.getenv("ENABLE_LEARNING_CACHE", "True").lower() == "true"
ENABLE_PATTERN_DECAY = os.getenv("ENABLE_PATTERN_DECAY", "True").lower() == "true"
ENABLE_PATTERN_PRUNER = os.getenv("ENABLE_PATTERN_PRUNER", "True").lower() == "true"
ENABLE_LEARNING_EXPLANATIONS = os.getenv("ENABLE_LEARNING_EXPLANATIONS", "True").lower() == "true"
ENABLE_ACTIVE_LEARNING = os.getenv("ENABLE_ACTIVE_LEARNING", "True").lower() == "true"
ENABLE_QUERY_CLUSTERING = os.getenv("ENABLE_QUERY_CLUSTERING", "True").lower() == "true"
ENABLE_FAILURE_PATTERN_TRACKING = os.getenv("ENABLE_FAILURE_PATTERN_TRACKING", "True").lower() == "true"
ENABLE_LEARNING_MIGRATIONS = os.getenv("ENABLE_LEARNING_MIGRATIONS", "True").lower() == "true"

LEARNING_SCHEMA_VERSION = int(os.getenv("LEARNING_SCHEMA_VERSION", 1))

MAX_LEARNING_NODES = int(os.getenv("MAX_LEARNING_NODES", 5000))
MAX_PATTERN_MEMORY = int(os.getenv("MAX_PATTERN_MEMORY", 1000))
MAX_CORRECTION_MEMORY = int(os.getenv("MAX_CORRECTION_MEMORY", 1000))
MAX_FEEDBACK_MEMORY = int(os.getenv("MAX_FEEDBACK_MEMORY", 2000))
MAX_FAILURE_PATTERNS = int(os.getenv("MAX_FAILURE_PATTERNS", 1000))

LEARNING_CACHE_SIZE = int(os.getenv("LEARNING_CACHE_SIZE", 100))

PATTERN_DECAY_FACTOR = float(os.getenv("PATTERN_DECAY_FACTOR", 0.97))
CORRECTION_DECAY_FACTOR = float(os.getenv("CORRECTION_DECAY_FACTOR", 0.99))
FAILURE_PATTERN_DECAY_FACTOR = float(os.getenv("FAILURE_PATTERN_DECAY_FACTOR", 0.95))

MIN_PATTERN_CONFIDENCE = float(os.getenv("MIN_PATTERN_CONFIDENCE", 0.50))
MIN_CORRECTION_CONFIDENCE = float(os.getenv("MIN_CORRECTION_CONFIDENCE", 0.60))
MIN_FEEDBACK_CONFIDENCE = float(os.getenv("MIN_FEEDBACK_CONFIDENCE", 0.50))

PATTERN_PRUNE_INTERVAL = int(os.getenv("PATTERN_PRUNE_INTERVAL", 50))

MAX_LEARNING_DEPTH = int(os.getenv("MAX_LEARNING_DEPTH", 3))
MAX_PATTERN_CHAIN = int(os.getenv("MAX_PATTERN_CHAIN", 10))

# Balanced Retrieval Weights
LEARNING_WEIGHT = float(os.getenv("LEARNING_WEIGHT", 0.20))
GRAPH_WEIGHT = float(os.getenv("GRAPH_WEIGHT", 0.20))
MEMORY_WEIGHT = float(os.getenv("MEMORY_WEIGHT", 0.20))
AGENT_WEIGHT = float(os.getenv("AGENT_WEIGHT", 0.20))
EVIDENCE_WEIGHT = float(os.getenv("EVIDENCE_WEIGHT", 0.20))

# Milestone 13 Multi-Agent Swarm Configuration
ENABLE_MULTI_AGENT_SWARM = os.getenv("ENABLE_MULTI_AGENT_SWARM", "True").lower() == "true"
ENABLE_AGENT_DELEGATION = os.getenv("ENABLE_AGENT_DELEGATION", "True").lower() == "true"
ENABLE_AGENT_NEGOTIATION = os.getenv("ENABLE_AGENT_NEGOTIATION", "True").lower() == "true"
ENABLE_SWARM_CONSENSUS = os.getenv("ENABLE_SWARM_CONSENSUS", "True").lower() == "true"
ENABLE_SHARED_MEMORY = os.getenv("ENABLE_SHARED_MEMORY", "True").lower() == "true"
ENABLE_MESSAGE_BROKER = os.getenv("ENABLE_MESSAGE_BROKER", "True").lower() == "true"
ENABLE_AGENT_MONITORING = os.getenv("ENABLE_AGENT_MONITORING", "True").lower() == "true"

SWARM_SCHEMA_VERSION = int(os.getenv("SWARM_SCHEMA_VERSION", 1))
MAX_SWARM_STEPS = int(os.getenv("MAX_SWARM_STEPS", 10))
SWARM_TIMEOUT_SECONDS = int(os.getenv("SWARM_TIMEOUT_SECONDS", 60))

MAX_AGENT_DEPTH = int(os.getenv("MAX_AGENT_DEPTH", 3))
MAX_MESSAGE_CHAIN = int(os.getenv("MAX_MESSAGE_CHAIN", 20))
MAX_AGENT_CACHE_SIZE = int(os.getenv("MAX_AGENT_CACHE_SIZE", 100))

ENABLE_PLANNING_AGENT = os.getenv("ENABLE_PLANNING_AGENT", "True").lower() == "true"
ENABLE_RETRIEVAL_AGENT = os.getenv("ENABLE_RETRIEVAL_AGENT", "True").lower() == "true"
ENABLE_KG_AGENT = os.getenv("ENABLE_KG_AGENT", "True").lower() == "true"
ENABLE_LEARNING_AGENT = os.getenv("ENABLE_LEARNING_AGENT", "True").lower() == "true"
ENABLE_VQA_AGENT = os.getenv("ENABLE_VQA_AGENT", "True").lower() == "true"
ENABLE_GROUNDING_AGENT = os.getenv("ENABLE_GROUNDING_AGENT", "True").lower() == "true"
ENABLE_CRITIC_AGENT = os.getenv("ENABLE_CRITIC_AGENT", "True").lower() == "true"
