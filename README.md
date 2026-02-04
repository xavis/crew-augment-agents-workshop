# 🤖 Gemini Multi-Agent Workshop (CrewAI) — DevFest Murcia 2026

Este repositorio/notebook muestra cómo montar un **equipo multi‑agente jerárquico** con **CrewAI** usando **Google Gemini 2.5 Flash**, incorporando **herramientas** de búsqueda (Tavily / DuckDuckGo) y una **herramienta de cálculo** para operaciones numéricas.

> Notebook principal: `augmented_agents.ipynb`

---

## 📌 Qué incluye

- **Conector LLM** (Gemini) configurado mediante variables de entorno.
- **Registro de herramientas (tools registry)** en un diccionario `tools`.
- **Agentes** con roles diferenciados:
  - `researcher_1` (Tavily)
  - `researcher_2` (DuckDuckGo)
  - `researcher_calculator` (Calculator)
  - `writer` (redacción/estrategia de contenido)
  - `manager` (gestión y delegación en modo jerárquico)
- **Tareas** (Tasks) parametrizadas con `{topic}`, `{year}` y `{operation}`.
- **Ejecución jerárquica** con `Process.hierarchical`.

---

## 🧠 Arquitectura (visión general)

La idea es separar responsabilidades:

1. **Investigación** (agentes investigadores)
2. **Síntesis y redacción** (writer)
3. **Orquestación, calidad y delegación** (manager)
4. **Cálculo determinista** (calculator) para evitar errores de “math hallucination”.

El flujo típico es:

1. `researcher_1` y `researcher_2` recopilan hallazgos actuales (cada uno con su herramienta).
2. `writer` crea un resumen/entregable final basado en la investigación.
3. `manager` supervisa y, si la librería lo permite en tu versión, delega y asegura coherencia.
4. (Opcional) Un agente con `calculator` resuelve cálculos exactos.

---

## ✅ Requisitos

- Python 3.10+ (recomendado)
- Acceso a claves API:
  - **Google Gemini API** (obligatorio)
  - **Tavily API** (opcional si usas Tavily)
  - Otras (p.ej. Serper) si las amplías

---

## 📦 Instalación de dependencias

En el notebook se instalan:

- `crewai`
- `crewai_tools`
- `langchain-google-genai`
- `tavily-python`
- `langchain-community`
- `duckduckgo-search` / `ddgs`

En local, puedes instalar algo equivalente con:

```bash
pip install crewai crewai_tools langchain-google-genai tavily-python   -U langchain-community duckduckgo-search ddgs
```

> Nota: las versiones pueden variar. Si hay conflictos, fija versiones en `requirements.txt`.

---

## 🔐 Variables de entorno (API Keys)

El notebook configura variables como:

- `MODEL_ID` → por ejemplo: `gemini/gemini-2.5-flash`
- `GEMINI_API_KEY` → clave de Google
- `TAVILY_API_KEY` → clave Tavily (si usas Tavily)
- `SERPER_API_KEY` → (aparece en el notebook; úsala solo si añades Serper)

Ejemplo en bash:

```bash
export MODEL_ID="gemini/gemini-2.5-flash"
export GEMINI_API_KEY="TU_API_KEY"
export TAVILY_API_KEY="TU_API_KEY"   # opcional
```

En Google Colab normalmente se usa `userdata.get(...)` o `os.environ[...]`.

---

## 🔧 Componentes del código (explicado)

### 1) Registro del LLM (Gemini)

El LLM se registra en `tools['gemini_llm']`:

- `model` desde `os.environ["MODEL_ID"]`
- `temperature = 0.7`
- parámetros extra: `max_tokens`, `top_p`, `top_k`, `frequency_penalty`, `presence_penalty`, `timeout`, `seed`

Esto permite reutilizar el mismo conector LLM en todos los agentes.

---

### 2) Herramientas de búsqueda

#### Tavily

Se crea una instancia:

- `tools['tavily'] = TavilySearchTool()`

Ideal para búsquedas rápidas orientadas a respuestas.

#### DuckDuckGo (vía LangChain Tool)

Se define como herramienta decorada con `@tool`:

- `@tool('DuckDuckGoSearch')`
- `tools['ddg'] = duckduckgo_search`

Permite a un agente invocar búsquedas web desde su razonamiento.

---

### 3) Herramienta Calculator

Se define:

- `@tool('Calculator')`
- `tools['calc'] = calculator`

En el notebook, `calculator()` usa `eval(expression)` por simplicidad.

⚠️ **Recomendación de seguridad:** si vas a exponer esto en producción, evita `eval` y usa un parser seguro (por ejemplo `ast.literal_eval` para casos simples, o `sympy` / un evaluador matemático restringido).

---

## 🧑‍🤝‍🧑 Agentes (Agents)

### `researcher_1` — Tavily

- **Rol:** Senior Research Analyst 1  
- **Tools:** `[tools['tavily']]`
- **Objetivo:** “Find the latest breakthroughs in {topic}”

### `researcher_2` — DuckDuckGo

- **Rol:** Senior Research Analyst 2  
- **Tools:** `[tools['ddg']]`

### `researcher_calculator` — Calculator

- **Rol:** Senior Research Analyst  
- **Tools:** `[tools['calc']]`
- **allow_delegation = True** (útil en jerarquía si se usa como manager o sub‑manager)

> Tip: si quieres un “researcher_calculator” realmente híbrido (buscar + calcular), dale ambas herramientas:
> `tools = [tools['ddg'], tools['calc']]` o `tools = [tools['tavily'], tools['calc']]`.

### `writer`

- **Rol:** Technical Content Strategist  
- Convierte investigación en un reporte “compelling”.

### `manager`

- **Rol:** Project Manager  
- `allow_delegation = VERBOSE` en el notebook
  - Si `VERBOSE = True`, también habilita delegación.
  - (Si prefieres claridad) usa directamente `allow_delegation = True`.

---

## ✅ Tareas (Tasks)

Se crean varias tareas y se guardan en `tasks[]`.

Ejemplos importantes:

1. Investigación (por `researcher_1`):
   - `Research the top 3 developments in {topic} for the year {year}.`
2. Investigación (por `researcher_2`):
   - Igual, pero con DuckDuckGo.
3. Síntesis (por `writer`):
   - `Create a summary based on the research provided...`
4. Tareas de cálculo / análisis numérico (hay dos variantes):
   - Una asignada a `researcher_2`
   - Otra asignada a `researcher_calculator`
5. `math_task`:
   - Calcula `{operation}` (p.ej. `2 + 56 / 22`)

---

## ▶️ Cómo ejecutar

### Ejecución 1: equipo de investigación + writer

Se monta:

- `agents = [researcher_1, researcher_2, writer]`
- `tasks = [tasks[0], tasks[1], tasks[2]]`
- `manager_agent = manager`
- `process = Process.hierarchical`

Inputs de ejemplo:

```python
{
  "topic": "Autonomous Robotics",
  "year": 2025
}
```

### Ejecución 2: cálculo

Se monta:

- `agents = [researcher_calculator, writer]`
- `tasks = [math_task]`

Inputs de ejemplo:

```python
{
  "topic": "Math operations",
  "operation": "2 + 56 / 22"
}
```

---

## 🧪 Ideas para extender el workshop

- Añadir un **critic/reviewer agent** para revisión final (tono, estructura, factualidad).
- Guardar salidas en:
  - Markdown (`.md`)
  - PDF
  - Google Docs
- Añadir **citas** y enlaces automáticos en el reporte final.
- Sustituir `eval` por una evaluación segura.
- Añadir **memoria** (contexto persistente) si tu framework lo soporta.

---

## 🩹 Troubleshooting (problemas comunes)

- **No encuentra `GEMINI_API_KEY`**  
  Verifica que está exportada o disponible en `userdata` (Colab).

- **Errores instalando dependencias**  
  Prueba a:
  - Reiniciar runtime
  - Fijar versiones
  - Instalar en un entorno limpio (venv)

- **DuckDuckGo devuelve pocos resultados / rate limits**  
  Cambia estrategia de búsqueda (más específica) o usa Tavily.

- **Resultados “inventados”**  
  Asegura que:
  - El agente investigador usa herramientas (`tools = [...]`)
  - Pides explícitamente fuentes en la descripción de la tarea

---

## 🔗 Links útiles (documentación oficial)

- CrewAI (docs): https://docs.crewai.com/
- CrewAI Tools: https://github.com/crewAIInc/crewAI-tools
- Google Gemini (visión general): https://ai.google.dev/
- LangChain (docs): https://python.langchain.com/docs/
- Tavily (docs): https://docs.tavily.com/
- DuckDuckGo Search (paquete): https://pypi.org/project/duckduckgo-search/
- ddgs (paquete): https://pypi.org/project/ddgs/

---

## 📄 Licencia

Añade aquí la licencia del proyecto (MIT, Apache-2.0, etc.) o indica “solo para fines educativos” si aplica.
