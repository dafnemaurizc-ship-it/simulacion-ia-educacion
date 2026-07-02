## Simulacion IA Educacion

Proyecto de simulacion educativa con tres escenarios:

- educacion tradicional
- uso de tecnologia educativa
- educacion personalizada con IA

## Requisitos

- Python 3.10+
- uv

## Instalacion

```bash
uv sync
```

## Ejecutar simulacion

```bash
uv run python -m simulacion_educativa.main
```

## Ejecutar con animacion

```bash
uv run python -m simulacion_educativa.main --animate --scenario traditional
```

## Launcher interactivo

```bash
uv run python -m simulacion_educativa.main --launcher
```

El launcher permite elegir una escena, ver su animacion completa y luego el dashboard final antes de volver al menu.

Tambien incluye la opcion `4` para comparar las 3 escenas desde el mismo menu.

Para seleccionar varias escenas en orden:

```bash
uv run python -m simulacion_educativa.main --animate --scenes traditional technology ai
```

Escenarios disponibles: `traditional`, `technology`, `ai`.

Al finalizar, se muestra un dashboard comparativo con los resultados de las escenas ejecutadas.

## Entrenar modelo ML

```bash
uv run python -m simulacion_educativa.ml.train_model
```

## Estructura

- `data/` contiene el dataset de entrada
- `src/simulacion_educativa/` contiene la simulacion y el pipeline ML
- `outputs/` guarda modelos, metricas y resultados generados
