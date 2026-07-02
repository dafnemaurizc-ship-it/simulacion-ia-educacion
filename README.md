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

## Entrenar modelo ML

```bash
uv run python -m simulacion_educativa.ml.train_model
```

## Estructura

- `data/` contiene el dataset de entrada
- `src/simulacion_educativa/` contiene la simulacion y el pipeline ML
- `outputs/` guarda modelos, metricas y resultados generados
