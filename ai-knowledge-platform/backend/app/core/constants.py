"""Application-wide constants and enumerations."""

# User roles
ROLE_ADMIN = "admin"
ROLE_KNOWLEDGE_ADMIN = "knowledge_admin"
ROLE_USER = "user"

# User statuses
USER_STATUS_ACTIVE = "active"
USER_STATUS_INACTIVE = "inactive"

# Knowledge base statuses
KB_STATUS_ENABLED = "enabled"
KB_STATUS_DISABLED = "disabled"
KB_STATUS_DELETED = "deleted"

# Knowledge item statuses
KNOWLEDGE_STATUS_DRAFT = "draft"
KNOWLEDGE_STATUS_AVAILABLE = "available"
KNOWLEDGE_STATUS_UNAVAILABLE = "unavailable"
KNOWLEDGE_STATUS_DELETED = "deleted"

# Knowledge source types
SOURCE_TYPE_MANUAL = "manual"
SOURCE_TYPE_DOCUMENT = "document"
SOURCE_TYPE_AI_EXTRACT = "ai_extract"
SOURCE_TYPE_DIALOGUE = "dialogue"

# Document parse statuses
PARSE_STATUS_UPLOADED = "uploaded"
PARSE_STATUS_PARSING = "parsing"
PARSE_STATUS_PARSED = "parsed"
PARSE_STATUS_FAILED = "failed"
PARSE_STATUS_IMPORTED = "imported"

# Document file types
FILE_TYPE_PDF = "pdf"
FILE_TYPE_DOCX = "docx"
FILE_TYPE_MD = "md"

# Agent statuses
AGENT_STATUS_ENABLED = "enabled"
AGENT_STATUS_DISABLED = "disabled"

# Answer styles
ANSWER_STYLE_CONCISE = "concise"
ANSWER_STYLE_DETAILED = "detailed"
ANSWER_STYLE_PROCEDURAL = "procedural"
ANSWER_STYLE_SERVICE = "service"

# Citation policies
CITATION_POLICY_REQUIRED = "required"
CITATION_POLICY_PREFERRED = "preferred"
CITATION_POLICY_NONE = "none"

# No answer policies
NO_ANSWER_POLICY_PROMPT = "prompt"
NO_ANSWER_POLICY_TRANSFER = "transfer"
NO_ANSWER_POLICY_RECOMMEND = "recommend"

# QA log statuses
QA_STATUS_ANSWERED = "answered"
QA_STATUS_NO_ANSWER = "no_answer"
QA_STATUS_FAILED = "failed"

# Feedback types
FEEDBACK_TYPE_LIKE = "like"
FEEDBACK_TYPE_DISLIKE = "dislike"
FEEDBACK_TYPE_NONE = "none"

# Audit actions
AUDIT_ACTION_CREATE = "create"
AUDIT_ACTION_UPDATE = "update"
AUDIT_ACTION_DELETE = "delete"
AUDIT_ACTION_PUBLISH = "publish"
AUDIT_ACTION_DISABLE = "disable"
AUDIT_ACTION_IMPORT = "import"

# Task queues
QUEUE_DOCUMENT = "document_queue"
QUEUE_EMBEDDING = "embedding_queue"
QUEUE_INDEX = "index_queue"
QUEUE_MAINTENANCE = "maintenance_queue"
