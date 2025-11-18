from datetime import datetime
from typing import List

import tensorflow as tf
from fastapi import FastAPI
from pydantic import BaseModel, Field


class Coordenadas(BaseModel):
    latitud: float = Field(..., description="Latitud en grados decimales")
    longitud: float = Field(..., description="Longitud en grados decimales")


class Servicio(BaseModel):
    fecha_hora_carga: datetime = Field(..., description="Fecha y hora programada de la carga")
    coordenadas: Coordenadas


class MedioEntrada(BaseModel):
    matricula: str = Field(..., description="Identificador del medio de transporte")
    fecha_disponibilidad: datetime = Field(..., description="Momento en que el medio queda disponible")
    distancia_hasta_carga: float = Field(..., description="Distancia en kilómetros hasta el punto de carga")
    amplitud_jornada: datetime = Field(..., description="Fin de la amplitud de jornada del conductor")


class ValoracionMedio(BaseModel):
    matricula: str
    omega1: float
    omega2: float
    omega3: float
    valoracion: float


class PeticionValoracion(BaseModel):
    servicio: Servicio
    medios: List[MedioEntrada]


app = FastAPI(title="Valoración de medios de transporte", version="1.0.0")


def _segundos_positivos(delta: float) -> float:
    return max(delta, 0.0)


def _calcular_valoraciones(payload: PeticionValoracion) -> List[ValoracionMedio]:
    if not payload.medios:
        return []

    fecha_carga = payload.servicio.fecha_hora_carga

    distancias = tf.constant([medio.distancia_hasta_carga for medio in payload.medios], dtype=tf.float32)
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

    valoraciones = (omega1 * 0.5 + omega2 * 0.1 + omega3 * 0.4) * 100.0
    valoraciones = tf.clip_by_value(valoraciones, 0.0, 100.0)

    resultados = []
    for medio, o1, o2, o3, val in zip(payload.medios, omega1.numpy(), omega2.numpy(), omega3.numpy(), valoraciones.numpy()):
        resultados.append(
            ValoracionMedio(
                matricula=medio.matricula,
                omega1=float(o1),
                omega2=float(o2),
                omega3=float(o3),
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
