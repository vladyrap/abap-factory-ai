"""Recetas: plantillas de requerimiento listas para usar (sin IA).

El consultor elige una receta y completa 1-2 campos; el sistema arma la descripción
y el contexto. Reduce a casi cero lo que tiene que escribir o saber.
"""
from fastapi import APIRouter, Depends
from app.api.deps import get_current_user

router = APIRouter(prefix="/recipes", tags=["Recetas"])

RECIPES = [
    {
        "key": "alv_report",
        "name": "Report ALV con filtros",
        "dev_type": "salv", "sap_version": "S4HANA",
        "fields": [{"key": "tabla", "label": "Tabla/origen", "placeholder": "BKPF"},
                   {"key": "filtros", "label": "Filtros", "placeholder": "sociedad y rango de fechas"}],
        "template": "Report ALV (CL_SALV_TABLE) que liste {tabla} con filtros por {filtros}, "
                    "con totales y exportación a Excel.",
    },
    {
        "key": "odata_read",
        "name": "Servicio OData de lectura",
        "dev_type": "odata", "sap_version": "S4HANA",
        "fields": [{"key": "entidad", "label": "Entidad de negocio", "placeholder": "OrdenCompra"}],
        "template": "Servicio OData (SEGW) de solo lectura para exponer la entidad {entidad} "
                    "con paginación y filtros estándar.",
    },
    {
        "key": "cds_view",
        "name": "CDS View analítica",
        "dev_type": "cds", "sap_version": "S4HANA",
        "fields": [{"key": "origen", "label": "Tabla/vista origen", "placeholder": "ACDOCA"},
                   {"key": "metricas", "label": "Métricas", "placeholder": "monto por centro de costo"}],
        "template": "CDS View de consumo sobre {origen} que exponga {metricas}, con asociaciones "
                    "a textos y annotations de UI básicas.",
    },
    {
        "key": "idoc_inbound",
        "name": "IDoc inbound con validación",
        "dev_type": "idoc", "sap_version": "ECC",
        "fields": [{"key": "tipo", "label": "Tipo de IDoc", "placeholder": "ORDERS05"}],
        "template": "Procesamiento inbound del IDoc {tipo} con función de validación, manejo de "
                    "errores y registro en el log de aplicación (BAL).",
    },
    {
        "key": "bapi_wrapper",
        "name": "RFC que envuelve una BAPI",
        "dev_type": "rfc", "sap_version": "ECC",
        "fields": [{"key": "bapi", "label": "BAPI a envolver", "placeholder": "BAPI_SALESORDER_CREATEFROMDAT2"}],
        "template": "Módulo de función RFC que envuelve {bapi}, evalúa el RETURN (BAPIRET2) y hace "
                    "BAPI_TRANSACTION_COMMIT/ROLLBACK según resultado.",
    },
    {
        "key": "batch_job",
        "name": "Programa de fondo (job)",
        "dev_type": "report", "sap_version": "S4HANA",
        "fields": [{"key": "proceso", "label": "Proceso", "placeholder": "cierre de documentos vencidos"}],
        "template": "Programa ejecutable para job de fondo que realice {proceso}, con variante de "
                    "selección, log de ejecución y manejo de bloqueos (ENQUEUE/DEQUEUE).",
    },
]


@router.get("/", dependencies=[Depends(get_current_user)])
def list_recipes():
    return RECIPES
