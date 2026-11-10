import json
import os

import boto3


def handler(event, context):
    if not isinstance(event, dict):
        raise ValueError("El evento debe ser un objeto JSON")

    tenant_id = event.get("tenant_id")
    alumno_id = event.get("alumno_id")
    alumno_datos = event.get("alumno_datos")
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise ValueError("tenant_id debe ser una cadena no vacía")
    if not isinstance(alumno_id, str) or not alumno_id.strip():
        raise ValueError("alumno_id debe ser una cadena no vacía")
    if not isinstance(alumno_datos, dict) or not isinstance(alumno_datos.get("nombre"), str):
        raise ValueError("alumno_datos.nombre debe ser una cadena")

    alumno = {
        "tenant_id": tenant_id,
        "alumno_id": alumno_id,
        "alumno_datos": alumno_datos,
    }
    boto3.resource("dynamodb").Table(os.environ["ALUMNOS_TABLE"]).put_item(Item=alumno)

    published = boto3.client("sns").publish(
        TopicArn=os.environ["NUEVO_ALUMNO_TOPIC_ARN"],
        Subject="Nuevo Alumno",
        Message=json.dumps(alumno, ensure_ascii=False),
        MessageAttributes={
            "tenant_id": {"DataType": "String", "StringValue": tenant_id}
        },
    )
    print(json.dumps({"evento": "NuevoAlumno", "tenant_id": tenant_id,
                      "alumno_id": alumno_id, "message_id": published["MessageId"]}))
    return {"statusCode": 200, "messageId": published["MessageId"]}
