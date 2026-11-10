import json
import os

import boto3

from src.sns_event import alumnos_from_sns


def handler(event, context):
    table = boto3.resource("dynamodb").Table(os.environ["SEGURIDAD_TABLE"])
    processed = 0
    for alumno in alumnos_from_sns(event):
        table.put_item(Item={
            "tenant_id": alumno["tenant_id"],
            "alumno_id": alumno["alumno_id"],
            "alumno_nombre": alumno["alumno_datos"]["nombre"],
        })
        processed += 1
    print(json.dumps({"suscriptor": "Seguridad", "procesados": processed}))
    return {"statusCode": 200, "procesados": processed}
