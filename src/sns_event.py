import json


def alumnos_from_sns(event):
    for record in event.get("Records", []):
        sns = record.get("Sns")
        if not isinstance(sns, dict):
            raise ValueError("Se esperaba un registro de SNS")
        alumno = json.loads(sns["Message"])
        if alumno.get("tenant_id") != "UTEC":
            continue
        if not isinstance(alumno.get("alumno_id"), str):
            raise ValueError("Falta alumno_id")
        datos = alumno.get("alumno_datos")
        if not isinstance(datos, dict) or not isinstance(datos.get("nombre"), str):
            raise ValueError("Falta alumno_datos.nombre")
        yield alumno
