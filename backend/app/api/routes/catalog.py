"""Catálogo estático para los selectores del frontend (contexto SAP, tipos de desarrollo)."""
from fastapi import APIRouter

router = APIRouter(prefix="/catalog", tags=["Catálogo"])

SAP_VERSIONS = [
    {"key": "ECC", "label": "SAP ECC"},
    {"key": "S4HANA", "label": "SAP S/4HANA (On-Premise)"},
    {"key": "S4HANA_CLOUD_PRIVATE", "label": "S/4HANA Cloud Private"},
    {"key": "S4HANA_CLOUD_PUBLIC", "label": "S/4HANA Cloud Public"},
]

MODULES = ["FI", "CO", "MM", "SD", "PP", "QM", "PM", "HR", "Basis", "Integracion"]

DEV_TYPES = [
    {"key": "report", "label": "Report (ABAP clásico)", "group": "Clásico"},
    {"key": "report_oo", "label": "Report (ABAP OO)", "group": "Clásico"},
    {"key": "module_pool", "label": "Module Pool / Dynpro", "group": "Clásico"},
    {"key": "alv", "label": "ALV clásico (REUSE_ALV)", "group": "Listados"},
    {"key": "salv", "label": "SALV (CL_SALV)", "group": "Listados"},
    {"key": "smartforms", "label": "Smartforms", "group": "Formularios"},
    {"key": "adobe_forms", "label": "Adobe Forms", "group": "Formularios"},
    {"key": "badi", "label": "BAdI", "group": "Enhancements"},
    {"key": "user_exit", "label": "User-Exit / Customer-Exit", "group": "Enhancements"},
    {"key": "enhancement", "label": "Enhancement (implicit/explicit)", "group": "Enhancements"},
    {"key": "bapi", "label": "BAPI", "group": "Interfaces"},
    {"key": "rfc", "label": "RFC / Función remota", "group": "Interfaces"},
    {"key": "idoc", "label": "IDoc (inbound/outbound)", "group": "Interfaces"},
    {"key": "interface_in", "label": "Interfaz inbound", "group": "Interfaces"},
    {"key": "interface_out", "label": "Interfaz outbound", "group": "Interfaces"},
    {"key": "pipo", "label": "PI/PO Integration", "group": "Integración"},
    {"key": "drc", "label": "DRC / eDocument", "group": "Integración"},
    {"key": "tax_form", "label": "Formulario tributario", "group": "Integración"},
    {"key": "odata", "label": "OData Gateway (SEGW)", "group": "S/4HANA"},
    {"key": "cds", "label": "CDS View", "group": "S/4HANA"},
    {"key": "amdp", "label": "AMDP (SQLScript)", "group": "S/4HANA"},
    {"key": "rap", "label": "RAP (Behavior + BO)", "group": "S/4HANA"},
    {"key": "webdynpro", "label": "WebDynpro ABAP", "group": "UI"},
    {"key": "job", "label": "Job / Programa batch", "group": "Otros"},
    {"key": "validation_fi", "label": "Validación FI/MM/SD", "group": "Otros"},
]

COMPLEXITIES = ["baja", "media", "alta", "critica"]
ENVIRONMENTS = ["DEV", "QAS", "PRD"]
SEVERITIES = ["baja", "media", "alta", "critica"]
PROTOCOL_TYPES = ["unitaria", "tecnica", "funcional", "integracion", "regresion", "performance", "uat"]
EDITOR_OPS = [
    {"key": "explain", "label": "Explicar línea por línea"},
    {"key": "refactor", "label": "Refactorizar (Clean ABAP)"},
    {"key": "to_oo", "label": "Convertir a ABAP OO"},
    {"key": "ecc_to_s4", "label": "Migrar ECC → S/4HANA"},
    {"key": "cleanup", "label": "Limpiar código legacy"},
]
DUMP_TYPES = [
    "OBJECTS_OBJREF_NOT_ASSIGNED", "CX_SY_OPEN_SQL_DB", "DBSQL_DUPLICATE_KEY_ERROR",
    "CONVT_NO_NUMBER", "TIME_OUT", "TSV_TNEW_PAGE_ALLOC_FAILED", "MESSAGE_TYPE_X",
    "CALL_FUNCTION_NOT_FOUND", "LOAD_PROGRAM_NOT_FOUND", "MOVE_TO_LIT_NOTALLOWED_NODATA",
    "GETWA_NOT_ASSIGNED", "ASSERTION_FAILED",
]


@router.get("/")
def get_catalog():
    return {
        "sap_versions": SAP_VERSIONS,
        "modules": MODULES,
        "dev_types": DEV_TYPES,
        "complexities": COMPLEXITIES,
        "environments": ENVIRONMENTS,
        "severities": SEVERITIES,
        "protocol_types": PROTOCOL_TYPES,
        "editor_ops": EDITOR_OPS,
        "dump_types": DUMP_TYPES,
    }
