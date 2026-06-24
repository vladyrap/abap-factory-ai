"""Schemas de los módulos de IA: requerimientos, generación, dumps, inspección, tests, editor."""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field
from app.core.config import settings

_MAX = settings.MAX_INPUT_CHARS

# Campo de texto grande (código/dump/texto libre) con tope de tamaño.
BigText = Field(..., max_length=_MAX)


# ─── Contexto SAP (selector) ─────────────────────────────────────────────────
class SapContext(BaseModel):
    sap_version: str = "S4HANA"
    module: Optional[str] = None
    dev_type: Optional[str] = None
    complexity: str = "media"
    standard: Optional[str] = None
    restrictions: Optional[str] = None
    naming_convention: Optional[str] = None
    transport_request: Optional[str] = None
    sap_package: Optional[str] = None
    mandante: Optional[str] = None
    environment: Optional[str] = None


# ─── Requerimientos ──────────────────────────────────────────────────────────
class RequirementCreate(BaseModel):
    project_id: int
    title: str
    description: Optional[str] = None
    sap_version: str = "S4HANA"
    module: Optional[str] = None
    dev_type: Optional[str] = None
    complexity: str = "media"
    standard: Optional[str] = None
    restrictions: Optional[str] = None
    naming_convention: Optional[str] = None
    transport_request: Optional[str] = None
    sap_package: Optional[str] = None
    extra_context: dict = {}


class RequirementResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str] = None
    sap_version: str
    module: Optional[str] = None
    dev_type: Optional[str] = None
    complexity: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Generación de código ────────────────────────────────────────────────────
class GenerateRequest(BaseModel):
    description: str = BigText
    sap_context: SapContext
    project_id: Optional[int] = None
    requirement_id: Optional[int] = None
    client_id: Optional[int] = None
    agent_override: Optional[str] = None
    save: bool = True
    auto_optimize: bool = False     # self-healing: genera y refina hasta target_score
    target_score: int = 80


class CodeArtifactResponse(BaseModel):
    id: int
    project_id: Optional[int] = None
    name: str
    dev_type: Optional[str] = None
    language: str
    code: str
    explanation: Optional[str] = None
    version: int
    status: str
    quality_score: Optional[float] = None
    lint_findings: list[Any] = []
    confidence_notes: list[Any] = []
    created_at: datetime

    class Config:
        from_attributes = True


class GenerateResponse(BaseModel):
    artifact: Optional[CodeArtifactResponse] = None
    object_name: str
    language: str
    code: str
    explanation: str
    agent_key: str
    provider: str
    model: str
    confidence_notes: list[Any] = []
    lint: Optional[dict] = None         # resultado del linter estático
    quality_score: Optional[float] = None
    passed: Optional[bool] = None       # alcanzó el target (self-healing)
    timeline: list[Any] = []            # iteraciones del self-healing
    used_knowledge: bool = False


class ValidateRequest(BaseModel):
    source_code: str = BigText


class RefineRequest(BaseModel):
    artifact_id: int
    instruction: str                    # "agrégale filtro por sociedad", "pásalo a SALV"


class ExtractRequest(BaseModel):
    raw_text: str = BigText
    project_id: Optional[int] = None


# ─── Migración ECC → S/4 / Cloud ─────────────────────────────────────────────
class MigrateRequest(BaseModel):
    source_code: str = BigText
    target: str = "S4HANA"      # S4HANA | S4HANA_CLOUD_PUBLIC | BTP_ABAP
    project_id: Optional[int] = None
    save: bool = True


# ─── Documento técnico (objeto por objeto + paso a paso) ─────────────────────
class DevDocRequest(BaseModel):
    description: str = BigText
    sap_context: SapContext
    project_id: Optional[int] = None
    requirement_id: Optional[int] = None
    client_id: Optional[int] = None
    save: bool = True


# ─── Nomenclaturas dinámicas ─────────────────────────────────────────────────
class NamingRuleCreate(BaseModel):
    client_id: int
    object_type: str
    pattern: str
    example: Optional[str] = None
    description: Optional[str] = None


class NamingPreviewRequest(BaseModel):
    pattern: str
    variables: dict = {}


# ─── Orquestador: Requerimiento → Solución ───────────────────────────────────
class SolutionRequest(BaseModel):
    requirement_text: str = BigText
    existing_code: Optional[str] = Field(None, max_length=_MAX)  # para fix/migración/ajuste o dump
    sap_context: Optional[SapContext] = None
    project_id: Optional[int] = None
    client_id: Optional[int] = None
    save: bool = True
    full_delivery: bool = False   # encadena spec + pruebas ABAP Unit + documento paso a paso


# ─── Conexión SAP / abapGit ──────────────────────────────────────────────────
class SapConnectionUpdate(BaseModel):
    kind: str = "abapgit"
    repo_url: Optional[str] = None
    branch: Optional[str] = "main"
    sap_package: Optional[str] = None
    transport_request: Optional[str] = None
    adt_base_url: Optional[str] = None


class ArtifactUpdate(BaseModel):
    """Edición de un artefacto: crea una nueva versión encadenada (parent_id)."""
    code: Optional[str] = None
    explanation: Optional[str] = None
    name: Optional[str] = None


# ─── Especificación técnica ──────────────────────────────────────────────────
class SpecRequest(BaseModel):
    description: str
    sap_context: SapContext
    project_id: Optional[int] = None
    requirement_id: Optional[int] = None
    save: bool = True


# ─── Dumps ───────────────────────────────────────────────────────────────────
class DumpRequest(BaseModel):
    raw_dump: str = BigText
    project_id: Optional[int] = None
    sap_context: Optional[SapContext] = None
    save: bool = True


class DumpResponse(BaseModel):
    id: Optional[int] = None
    dump_type: Optional[str] = None
    severity: Optional[str] = None
    program: Optional[str] = None
    include: Optional[str] = None
    line: Optional[str] = None
    sap_object: Optional[str] = None
    root_cause: Optional[str] = None
    solution: Optional[str] = None
    fixed_code: Optional[str] = None
    checklist: list[Any] = []
    suggested_tests: list[Any] = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Code Inspector ──────────────────────────────────────────────────────────
class InspectRequest(BaseModel):
    source_code: str = BigText
    sap_context: Optional[SapContext] = None
    project_id: Optional[int] = None
    code_artifact_id: Optional[int] = None
    save: bool = True


# ─── Tests ───────────────────────────────────────────────────────────────────
class UnitTestRequest(BaseModel):
    source_code: str = BigText
    sap_context: Optional[SapContext] = None
    project_id: Optional[int] = None
    code_artifact_id: Optional[int] = None
    save: bool = True


class ProtocolRequest(BaseModel):
    description: str
    protocol_type: str = "funcional"
    name: Optional[str] = None
    sap_context: Optional[SapContext] = None
    project_id: Optional[int] = None
    requirement_id: Optional[int] = None
    save: bool = True


# ─── Editor ──────────────────────────────────────────────────────────────────
class EditorRequest(BaseModel):
    operation: str  # explain | refactor | to_oo | ecc_to_s4 | cleanup
    source_code: str = BigText
    project_id: Optional[int] = None


# ─── Agentes ─────────────────────────────────────────────────────────────────
class AgentConfigUpdate(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    system_prompt: Optional[str] = None
    is_active: Optional[bool] = None
