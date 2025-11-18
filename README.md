# TensorFlow_v1

Servicio FastAPI para valorar medios de transporte en función de distancia, disponibilidad y amplitud de jornada utilizando TensorFlow.

## Requisitos

- Python 3.11+
- Dependencias del archivo `requirements.txt`

Instala dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución

Inicia el servidor de desarrollo con Uvicorn:

```bash
uvicorn main:app --reload
```

## Uso

Envía una petición `POST /valorar` con el siguiente cuerpo JSON:

```json
{
  "servicio": {
    "fecha_hora_carga": "2024-07-01T08:00:00",
    "coordenadas": {"latitud": 41.387, "longitud": 2.170}
  },
  "medios": [
    {
      "matricula": "1234-ABC",
      "fecha_disponibilidad": "2024-07-01T06:30:00",
      "distancia_hasta_carga": 12.5,
      "amplitud_jornada": "2024-07-01T18:00:00"
    }
  ]
}
```

La respuesta incluye los valores ω1, ω2, ω3 y la valoración final entre 0 y 100 calculada con TensorFlow.
