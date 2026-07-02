# Simulación IA Educación

Simulador educativo con tres escenarios comparables, entrenamiento de un modelo de riesgo académico y visualización nativa en tiempo real con Salabim.

## Resumen

El proyecto modela una cohorte de estudiantes y permite evaluar tres enfoques pedagógicos:

| Escenario | Enfoque |
|---|---|
| `traditional` | Educación tradicional con baja personalización |
| `technology` | Uso de tecnología educativa |
| `ai` | Educación personalizada con IA |

La aplicación soporta tres formas de uso:

| Modo | Descripción |
|---|---|
| Batch | Ejecuta los escenarios y exporta CSV/metrics |
| Animado | Muestra la evolución en tiempo real con Salabim |
| Launcher | Menú interactivo para elegir una escena o comparar las tres |

## Qué resuelve

- Compara estrategias educativas bajo las mismas condiciones iniciales.
- Entrena y usa un clasificador para estimar riesgo académico.
- Muestra resultados numéricos y visuales sin mezclar la lógica de simulación con la interfaz.

## Arquitectura

| Componente | Rol |
|---|---|
| `cohort_factory.py` | Genera la cohorte sintética base |
| `traditional_scenario.py` | Simulación del escenario tradicional |
| `technology_scenario.py` | Simulación con tecnología educativa |
| `ai_personalized_scenario.py` | Simulación con intervención basada en ML |
| `ml/` | Preparación, entrenamiento y predicción del riesgo |
| `visualization/` | Vista en vivo y dashboard final |
| `launcher.py` | Menú interactivo por terminal |
| `runner.py` | Orquestación compartida de escenarios y exportaciones |

## Cómo ejecutar

Instalación:

```bash
uv sync
```

Ejecución batch:

```bash
uv run python -m simulacion_educativa.main
```

Un escenario con animación:

```bash
uv run python -m simulacion_educativa.main --animate --scenario traditional
```

Comparación de escenas con animación:

```bash
uv run python -m simulacion_educativa.main --animate --scenes traditional technology ai
```

Launcher interactivo:

```bash
uv run python -m simulacion_educativa.main --launcher
```

## Entrenamiento ML

```bash
uv run python -m simulacion_educativa.ml.train_model
```

## Salidas generadas

| Carpeta | Contenido |
|---|---|
| `outputs/results/` | CSV por escenario y comparación general |
| `outputs/models/` | Modelos entrenados y el modelo óptimo |
| `outputs/metrics/` | Métricas por modelo y resumen |

## Diagramas BPMN

- AS-IS: `docs/processes/as-is.bpmn`
- TO-BE: `docs/processes/to-be.bpmn`

Abrilos con Bizagi Modeler mediante importación BPMN 2.0.

## Conclusiones

- El escenario personalizado con IA ofrece los mejores resultados generales en aprobación y deserción.
- El uso de tecnología mejora frente al modelo tradicional, pero no reemplaza la personalización.
- La visualización en vivo ayuda a entender el comportamiento dinámico de la cohorte, no solo el resultado final.

## Recomendaciones

- Usar el launcher para comparar escenarios en demos y presentaciones.
- Ajustar pesos y umbrales con datos reales si se busca validez externa.
- Incorporar más variables académicas y socioeconómicas al modelo ML.
- Agregar pruebas automáticas para mantener estable el flujo batch y el animado.

## Estructura

- `data/` contiene el dataset de entrada
- `src/simulacion_educativa/` contiene la simulación y el pipeline ML
- `docs/processes/` contiene los BPMN AS-IS y TO-BE
- `outputs/` guarda modelos, métricas y resultados generados
