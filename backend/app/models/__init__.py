"""Importa todos los modelos para que Base.metadata los registre."""
from app.models.user import User, UserRole
from app.models.client import Client
from app.models.project import Project
from app.models.requirement import Requirement
from app.models.tech_spec import TechSpec
from app.models.generation import Generation
from app.models.code_artifact import CodeArtifact
from app.models.dump_analysis import DumpAnalysis
from app.models.code_inspection import CodeInspection
from app.models.test_suite import TestSuite
from app.models.test_protocol import TestProtocol, PROTOCOL_TYPES
from app.models.ai_usage import AIUsage
from app.models.agent_config import AgentConfig
from app.models.job import Job, JOB_TYPES
from app.models.client_knowledge import ClientKnowledge, KNOWLEDGE_KINDS
from app.models.naming_rule import NamingRule, NAMING_OBJECT_TYPES
from app.models.migration import Migration
from app.models.dev_document import DevDocument
from app.models.sap_connection import SapConnection
from app.models.role import Role
from app.models.audit_log import AuditLog

__all__ = [
    "User", "UserRole", "Client", "Project", "Requirement", "TechSpec",
    "Generation", "CodeArtifact", "DumpAnalysis", "CodeInspection",
    "TestSuite", "TestProtocol", "PROTOCOL_TYPES", "AIUsage", "AgentConfig",
    "Job", "JOB_TYPES", "ClientKnowledge", "KNOWLEDGE_KINDS",
    "NamingRule", "NAMING_OBJECT_TYPES", "Migration", "DevDocument", "SapConnection",
    "Role", "AuditLog",
]
