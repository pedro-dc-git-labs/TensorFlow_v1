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

Envía una petición `POST /valorar` con el siguiente cuerpo JSON (nota que tanto el servicio como los medios incluyen su UP y coordenadas completas):

```json
{
  "servicio": {
    "fecha_hora_carga": "2024-07-01T08:00:00",
    "coordenadas": {"latitud": 41.387, "longitud": 2.170},
    "UP": "BCN-01"
  },
  "medios": [
    {
      "matricula": "1234-ABC",
      "fecha_disponibilidad": "2024-07-01T06:30:00",
      "coordenadas": {"latitud": 41.40, "longitud": 2.19},
      "amplitud_jornada": "2024-07-01T18:00:00",
      "UP": "BCN-01",
      "tipo_evento": "DESCARGA"
    }
  ]
}
```

Ejemplo con varios medios disponibles:

```json
{
  "servicio": {
    "fecha_hora_carga": "2024-07-01T08:00:00",
    "coordenadas": {"latitud": 41.387, "longitud": 2.170},
    "UP": "BCN-01"
  },
  "medios": [
    {
      "matricula": "1234-ABC",
      "fecha_disponibilidad": "2024-07-01T06:30:00",
      "coordenadas": {"latitud": 41.40, "longitud": 2.19},
      "amplitud_jornada": "2024-07-01T18:00:00",
      "UP": "BCN-01",
      "tipo_evento": "DESCARGA"
    },
    {
      "matricula": "5678-DEF",
      "fecha_disponibilidad": "2024-07-01T07:00:00",
      "coordenadas": {"latitud": 41.33, "longitud": 2.11},
      "amplitud_jornada": "2024-07-01T17:30:00",
      "UP": "BCN-02",
      "tipo_evento": "ORDEN_ADMINISTRATIVA"
    },
    {
      "matricula": "9012-GHI",
      "fecha_disponibilidad": "2024-07-01T05:45:00",
      "coordenadas": {"latitud": 41.52, "longitud": 2.03},
      "amplitud_jornada": "2024-07-01T19:00:00",
      "UP": "MAD-03",
      "tipo_evento": "OTRO"
    }
  ]
}
```

La respuesta incluye los valores ω1, ω2, ω3, ω4 y ω5 junto con la distancia estimada por Haversine y la valoración final entre 0 y 100 calculada con TensorFlow.
