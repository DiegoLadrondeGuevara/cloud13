import json
import os
import unittest
from unittest.mock import MagicMock, patch

from src import crear_alumno, crear_alumno_canvas, crear_alumno_seguridad


ALUMNO = {
    "tenant_id": "UTEC",
    "alumno_id": "2020777990",
    "alumno_datos": {"nombre": "Carla Espinoza"},
}


def sns_event(alumno):
    return {"Records": [{"Sns": {"Message": json.dumps(alumno)}}]}


class HandlerTests(unittest.TestCase):
    @patch.dict(os.environ, {"ALUMNOS_TABLE": "t_alumnos", "NUEVO_ALUMNO_TOPIC_ARN": "topic"})
    @patch("src.crear_alumno.boto3.client")
    @patch("src.crear_alumno.boto3.resource")
    def test_publisher_persists_then_publishes_filter_attribute(self, resource, client):
        client.return_value.publish.return_value = {"MessageId": "msg-1"}
        response = crear_alumno.handler(ALUMNO, None)
        self.assertEqual(response["messageId"], "msg-1")
        resource.return_value.Table.assert_called_once_with("t_alumnos")
        resource.return_value.Table.return_value.put_item.assert_called_once_with(Item=ALUMNO)
        published = client.return_value.publish.call_args.kwargs
        self.assertEqual(published["MessageAttributes"]["tenant_id"]["StringValue"], "UTEC")
        self.assertEqual(json.loads(published["Message"]), ALUMNO)

    @patch.dict(os.environ, {"CANVAS_TABLE": "t_alumnos_canvas"})
    @patch("src.crear_alumno_canvas.boto3.resource")
    def test_canvas_receives_utec(self, resource):
        response = crear_alumno_canvas.handler(sns_event(ALUMNO), None)
        self.assertEqual(response["procesados"], 1)
        resource.return_value.Table.return_value.put_item.assert_called_once_with(Item={
            "tenant_id": "UTEC", "alumno_id": "2020777990", "alumno_nombre": "Carla Espinoza"
        })

    @patch.dict(os.environ, {"SEGURIDAD_TABLE": "t_alumnos_seguridad"})
    @patch("src.crear_alumno_seguridad.boto3.resource")
    def test_security_receives_utec(self, resource):
        response = crear_alumno_seguridad.handler(sns_event(ALUMNO), None)
        self.assertEqual(response["procesados"], 1)
        resource.return_value.Table.return_value.put_item.assert_called_once()

    @patch.dict(os.environ, {"SEGURIDAD_TABLE": "t_alumnos_seguridad"})
    @patch("src.crear_alumno_seguridad.boto3.resource")
    def test_security_skips_non_utec_even_if_filter_is_bypassed(self, resource):
        other = {**ALUMNO, "tenant_id": "UNIV2"}
        response = crear_alumno_seguridad.handler(sns_event(other), None)
        self.assertEqual(response["procesados"], 0)
        resource.return_value.Table.return_value.put_item.assert_not_called()

    @patch("src.crear_alumno.boto3.resource")
    def test_invalid_publisher_input_does_not_write(self, resource):
        with self.assertRaises(ValueError):
            crear_alumno.handler({"tenant_id": "UTEC"}, None)
        resource.assert_not_called()


if __name__ == "__main__":
    unittest.main()
