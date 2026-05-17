import os
import time
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv(Path(__file__).resolve().parent.parent / "Taller2" / ".env")

# ─── CONFIGURACIÓN DE PÁGINA ─────────────────────────────────────────────────

st.set_page_config(
    page_title="EcoMarket — Asistente IA",
    page_icon="🌿",
    layout="centered",
)

def _load_css(path: Path) -> None:
    st.markdown(f"<style>{path.read_text()}</style>", unsafe_allow_html=True)

_load_css(Path(__file__).parent / "styles.css")

# ─── CONSTANTES ──────────────────────────────────────────────────────────────

TOOL_META = {
    "consultar_estado_pedido":         {"icon": "📦", "label": "Estado de pedido"},
    "verificar_elegibilidad_devolucion": {"icon": "🔍", "label": "Elegibilidad devolución"},
    "generar_etiqueta_devolucion":     {"icon": "🏷️",  "label": "Generar etiqueta"},
    "buscar_politicas_ecomarket":      {"icon": "📚", "label": "Políticas / FAQ"},
}

# ─── HEADER ──────────────────────────────────────────────────────────────────

st.markdown("""
<div class="eco-header">
    <h1>🌿 EcoMarket — Asistente IA</h1>
    <p>Consulta el estado de tus pedidos, gestiona devoluciones y conoce nuestras políticas</p>
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🌿 EcoMarket Support")
    st.markdown('<span class="status-dot"></span> **Agente activo**', unsafe_allow_html=True)
    st.divider()

    st.markdown("### 🛠 Herramientas disponibles")
    for meta in TOOL_META.values():
        st.markdown(f"{meta['icon']} {meta['label']}")

    st.divider()
    st.markdown("### 📦 Pedidos de prueba")
    st.markdown("""
| # | Estado |
|---|--------|
| ECO1001 | En tránsito |
| ECO1002 | Entregado ✅ |
| ECO1004 | Retrasado ⚠️ |
| ECO1006 | Entregado ✅ |
""")
    st.divider()
    st.caption("Proyecto Final — IA Generativa · ICESI")

# ─── VALIDACIÓN API KEY ───────────────────────────────────────────────────────

if not os.getenv("OPENAI_API_KEY"):
    st.error(
        "⚠️ No se encontró OPENAI_API_KEY. "
        "Crea un archivo `.env` en la carpeta Taller2 con `OPENAI_API_KEY=sk-...`"
    )
    st.stop()

# ─── CARGA DEL AGENTE (cacheado) ─────────────────────────────────────────────

@st.cache_resource(show_spinner="Inicializando el agente y la base de conocimiento RAG...")
def load_agent():
    from agente_ecomarket import get_agent, get_vector_db
    get_vector_db()
    return get_agent()

load_agent()

# ─── ESTADO DE SESIÓN ─────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.lc_history = []
    st.session_state.response_times = []
    st.session_state.tools_count = {k: 0 for k in TOOL_META}

# ─── HELPER: RENDERIZAR PASOS DE TOOLS ───────────────────────────────────────

def render_tool_steps(steps: list, elapsed: float | None = None):
    if not steps:
        return
    n = len(steps)
    header = f"🔧 {n} herramienta{'s' if n > 1 else ''} usada{'s' if n > 1 else ''}"
    if elapsed is not None:
        header += f"  ·  ⏱ {elapsed:.1f}s"

    with st.expander(header):
        st.markdown('<div class="tl-wrap">', unsafe_allow_html=True)
        for i, step in enumerate(steps, 1):
            meta = TOOL_META.get(step["tool"], {"icon": "🔧", "label": step["tool"]})
            output_preview = step["output"][:280] + ("…" if len(step["output"]) > 280 else "")
            st.markdown(
                f'<div class="tl-step">'
                f'<div>'
                f'<span style="font-size:0.75rem;color:#888;margin-right:6px">Paso {i}</span>'
                f'{meta["icon"]} <span class="tl-badge">{step["tool"]}</span>'
                f'<div class="tl-io">'
                f'<b>Entrada:</b> <code>{step["input"]}</code><br>'
                f'<b>Resultado:</b> {output_preview}'
                f'</div>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

# ─── MÉTRICAS EN TIEMPO REAL ─────────────────────────────────────────────────

n_consultas = len([m for m in st.session_state.messages if m["role"] == "user"])
n_tools     = sum(st.session_state.tools_count.values())
avg_time    = (
    f"{sum(st.session_state.response_times) / len(st.session_state.response_times):.1f}s"
    if st.session_state.response_times else "—"
)
top_tool    = (
    max(st.session_state.tools_count, key=st.session_state.tools_count.get)
    if n_tools > 0 else "—"
)
top_icon    = TOOL_META[top_tool]["icon"] if top_tool != "—" else "—"

col1, col2, col3, col4 = st.columns(4)
col1.metric("💬 Consultas",       n_consultas)
col2.metric("🔧 Llamadas a tools", n_tools)
col3.metric("⏱ Tiempo promedio",  avg_time)
col4.metric("🏆 Tool más usada",  top_icon if top_tool == "—" else f"{top_icon} ×{st.session_state.tools_count[top_tool]}" if n_tools > 0 else "—")

st.divider()

# ─── CONSULTAS SUGERIDAS (solo cuando no hay historial) ───────────────────────

if not st.session_state.messages:
    st.markdown("**Prueba con alguna de estas consultas:**")
    suggestions = [
        "¿Cuál es el estado del pedido ECO1004?",
        "Quiero devolver el pedido ECO1002 porque llegó defectuoso",
        "¿Cuál es el plazo para hacer una devolución?",
        "Quiero devolver el pedido ECO1001",
    ]
    cols = st.columns(2)
    for i, s in enumerate(suggestions):
        if cols[i % 2].button(s, key=f"sug_{i}", use_container_width=True):
            st.session_state["_pending"] = s
            st.rerun()

# ─── HISTORIAL DE CHAT ────────────────────────────────────────────────────────

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("steps"):
            render_tool_steps(msg["steps"], msg.get("elapsed"))

# ─── INPUT DEL USUARIO ────────────────────────────────────────────────────────

query = st.chat_input("Escribe tu consulta aquí...")

if "_pending" in st.session_state:
    query = st.session_state.pop("_pending")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Procesando..."):
            from agente_ecomarket import run_query
            t0 = time.time()
            result = run_query(query, st.session_state.lc_history)
            elapsed = round(time.time() - t0, 2)

        response = result["output"]
        st.markdown(response)

        steps_display = result.get("steps", [])
        render_tool_steps(steps_display, elapsed)

        if not result["success"]:
            st.error("Hubo un error. Intenta de nuevo o contacta a soporte@ecomarket.com")

    # Actualizar métricas
    st.session_state.response_times.append(elapsed)
    for step in steps_display:
        if step["tool"] in st.session_state.tools_count:
            st.session_state.tools_count[step["tool"]] += 1

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "steps": steps_display,
        "elapsed": elapsed,
    })
    st.session_state.lc_history.extend([
        HumanMessage(content=query),
        AIMessage(content=response),
    ])

    st.rerun()
