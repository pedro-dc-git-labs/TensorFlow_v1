from datetime import datetime
from typing import List
import math

import tensorflow as tf
from fastapi import FastAPI
from pydantic import BaseModel, Field


class Coordenadas(BaseModel):
    latitud: float = Field(..., description="Latitud en grados decimales")
    longitud: float = Field(..., description="Longitud en grados decimales")


class Servicio(BaseModel):
    fecha_hora_carga: datetime = Field(..., description="Fecha y hora programada de la carga")
    coordenadas: Coordenadas
    UP: str = Field(..., description="Unidad productiva del servicio")


class MedioEntrada(BaseModel):
    matricula: str = Field(..., description="Identificador del medio de transporte")
    fecha_disponibilidad: datetime = Field(..., description="Momento en que el medio queda disponible")
    coordenadas: Coordenadas
    amplitud_jornada: datetime = Field(..., description="Fin de la amplitud de jornada del conductor")
    UP: str = Field(..., description="Unidad productiva del medio")
    tipo_evento: str = Field(..., description="Tipo de evento asociado al medio")


class ValoracionMedio(BaseModel):
    matricula: str
    omega1: float
    omega2: float
    omega3: float
    omega4: float
    omega5: float
    distancia: float
    valoracion: float


class PeticionValoracion(BaseModel):
    servicio: Servicio
    medios: List[MedioEntrada]


app = FastAPI(title="Valoración de medios de transporte", version="1.0.0")


def _segundos_positivos(delta: float) -> float:
    return max(delta, 0.0)


def _haversine_metros(origen: Coordenadas, destino: Coordenadas) -> float:
    """Calcula la distancia entre dos coordenadas usando la fórmula de Haversine."""

    radio_tierra_m = 6371000.0

    radian_factor = tf.constant(math.pi / 180.0, dtype=tf.float32)
    lat1 = tf.constant(origen.latitud, dtype=tf.float32) * radian_factor
    lat2 = tf.constant(destino.latitud, dtype=tf.float32) * radian_factor
    dlat = lat2 - lat1
    dlon = (destino.longitud - origen.longitud) * radian_factor

    a = tf.sin(dlat / 2) ** 2 + tf.cos(lat1) * tf.cos(lat2) * tf.sin(dlon / 2) ** 2
    c = 2 * tf.atan2(tf.sqrt(a), tf.sqrt(1 - a))
    return float(radio_tierra_m * c)


def _compatibilidad_up(up_servicio: str, up_medio: str) -> float:
    if up_servicio == up_medio:
        return 1.0
    if up_servicio[:2] == up_medio[:2]:
        return 0.4
    return 0.0


def _valor_tipo_evento(tipo_evento: str) -> float:
    eventos_valorados = {"DESCARGA", "ORDEN_ADMINISTRATIVA"}
    return 1.0 if tipo_evento.upper() in eventos_valorados else 0.0


def _calcular_valoraciones(payload: PeticionValoracion) -> List[ValoracionMedio]:
    if not payload.medios:
        return []

    fecha_carga = payload.servicio.fecha_hora_carga

    distancias_metros = [
        _haversine_metros(payload.servicio.coordenadas, medio.coordenadas) for medio in payload.medios
    ]
    distancias = tf.constant(distancias_metros, dtype=tf.float32)
    esperas = tf.constant(
        [
            _segundos_positivos((fecha_carga - medio.fecha_disponibilidad).total_seconds())
            for medio in payload.medios
        ],
        dtype=tf.float32,
    )
    tiempos_post_carga = tf.constant(
        [
            _segundos_positivos((medio.amplitud_jornada - fecha_carga).total_seconds())
            for medio in payload.medios
        ],
        dtype=tf.float32,
    )

    dist_min = tf.reduce_min(tf.maximum(distancias, 1e-6))
    espera_min = tf.reduce_min(tf.maximum(esperas, 1e-6))
    post_carga_min = tf.reduce_min(tf.maximum(tiempos_post_carga, 1e-6))

    omega1 = dist_min / (tf.maximum(distancias, 1e-6))
    omega2 = espera_min / (tf.maximum(esperas, 1e-6))
    omega3 = tiempos_post_carga / post_carga_min
    omega4 = tf.constant(
        [_compatibilidad_up(payload.servicio.UP, medio.UP) for medio in payload.medios], dtype=tf.float32
    )
    omega5 = tf.constant([
        _valor_tipo_evento(medio.tipo_evento) for medio in payload.medios
    ], dtype=tf.float32)

    valoraciones = (
        omega1 * 0.5
        + omega2 * 0.2
        + omega3 * 0.2
        + omega4 * 0.05
        + omega5 * 0.05
    ) * 100.0
    valoraciones = tf.clip_by_value(valoraciones, 0.0, 100.0)

    resultados = []
    for medio, dist, o1, o2, o3, o4, o5, val in zip(
        payload.medios,
        distancias_metros,
        omega1.numpy(),
        omega2.numpy(),
        omega3.numpy(),
        omega4.numpy(),
        omega5.numpy(),
        valoraciones.numpy(),
    ):
        resultados.append(
            ValoracionMedio(
                matricula=medio.matricula,
                omega1=float(o1),
                omega2=float(o2),
                omega3=float(o3),
                omega4=float(o4),
                omega5=float(o5),
                distancia=float(dist),
                valoracion=float(val),
            )
        )
    return resultados


@app.post("/valorar", response_model=List[ValoracionMedio])
async def valorar(payload: PeticionValoracion) -> List[ValoracionMedio]:
    """
    Calcula la valoración de cada medio utilizando TensorFlow siguiendo los criterios de distancia, tiempo
    de espera y amplitud de jornada posterior a la carga.
    """

    return _calcular_valoraciones(payload)


@app.get("/")
async def root() -> dict:
    return {"mensaje": "Servicio de valoración de medios de transporte"}
