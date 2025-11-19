# 🚚 Valoración de Medios de Transporte -- FastAPI + TensorFlow

Función de COSTES

Valores
-   ω1 Distancia entre el medio y la ubicación del servicio, calculo Haversine (tiempo de respuesta)
-   ω2 Tiempo de espera hasta la carga
-   ω3 Amplitud de jornada posterior a la carga
-   ω4 Compatibilidad de Unidad Productiva (UP), directa no evaluacion de compatibilidad, se resta peso para compesar. 
-   ω5 Tipo de evento operativo, prioriza eventos finales

Pesos
-   ω1 50/100
-   ω2 20/100
-   ω3 20/100
-   ω4 05/100 
-   ω5 05/100

El cálculo se realiza mediante operaciones vectorizadas con TensorFlow, 
devolviendo una puntuación final entre 0 y 100 para cada medio disponible.

## IMPORTANTE !!!!!! **** NOTAS RENDIMIENTO *****
Retiramos restriciones fuertes, tiene mas sentido usar filtros para limitar la entrada que filtrar por pesos (zonas, compatibilidades)
Retiramos calculos externos para no penalizar rendimiento, llamadas externas (PTV, Google) 
Retiramos monitoreo consola
## IMPORTANTE !!!!!! **** CONSUMO DE RECURSOS
Limitar instancias, reciclado.
****Pendiente, mover fuera de TROS 


------------------------------------------------------------------------

## 📦 Requisitos

-   Python **3.11 o superior**
-   Dependencias del proyecto:

```{=html}
<!-- -->
```
    fastapi
    uvicorn
    tensorflow

Instalar dependencias:

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

## ▶️ Ejecución del servidor

Inicia el servidor con recarga automática:

``` bash
uvicorn main:app --reload
```

------------------------------------------------------------------------

## 📡 Endpoints

### GET `/`

Devuelve un mensaje de estado.

### POST `/valorar`

Calcula la valoración de cada medio disponible.

Ejemplo de entrada:

``` json
{
  "servicio": {
    "fecha_hora_carga": "2025-01-10T10:00:00",
    "coordenadas": { "latitud": 40.417, "longitud": -3.703 },
    "UP": "UP01"
  },
  "medios": [
    {
      "matricula": "1111-AAA",
      "fecha_disponibilidad": "2025-01-10T08:30:00",
      "coordenadas": { "latitud": 40.400, "longitud": -3.700 },
      "amplitud_jornada": "2025-01-10T18:00:00",
      "UP": "UP01",
      "tipo_evento": "DESCARGA"
    }
  ]
}
```

------------------------------------------------------------------------


