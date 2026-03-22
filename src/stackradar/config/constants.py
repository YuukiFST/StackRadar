"""Constantes globais do StackRadar."""

# Host HTTPS onde as rotas /api/pcsx/* estão publicadas
EIGHTFOLD_API_HOST = "mercadolibre.eightfold.ai"

# Parâmetro `domain` exigido pela API (marca / tenant)
EIGHTFOLD_BUSINESS_DOMAIN = "mercadolibre.com"

CAREERS_BASE_URL = f"https://{EIGHTFOLD_API_HOST}/careers"

# Busca na API: restringe resultados no servidor (menos páginas).
DEFAULT_SEARCH_QUERY = "software"

# Filtro adicional no cliente: título deve conter esta substring (case-insensitive)
TITLE_MUST_CONTAIN = "software"

DEFAULT_TECH_LIST = [
    "Go (Golang)",
    "Java",
    "Kotlin",
    "Python",
    "JavaScript",
    "Node.js",
    "Spring Boot",
    "React",
    "AWS",
    "GCP",
    "Docker",
    "MySQL",
    "Redis",
    "NoSQL",
    "Elasticsearch",
    "Kafka",
    "RabbitMQ",
    "Datadog",
    "New Relic",
    "Grafana",
    "Kibana",
    "Microsserviços",
    "APIs REST",
    "SOLID",
    "Clean Architecture",
    "Design Patterns",
    "Event Driven",
    "Claude",
    "Copilot",
    "Cursor",
    "Gemini",
    "GPT",
]

OLLAMA_DEFAULT_MODEL = "qwen3.5:9b"
OLLAMA_DEFAULT_BASE_URL = "http://127.0.0.1:11434"
GROQ_DEFAULT_MODEL = "llama-3.1-8b-instant"

# RAG
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
CHROMA_COLLECTION = "job_chunks"
RAG_TOP_K = 8
