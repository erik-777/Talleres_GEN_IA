import os
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

st.markdown("""
<style>
    .eco-header { color: #2E7D32; font-size: 2rem; font-weight: 700; margin-bottom: 0; }
    .eco-sub    { color: #558B2F; font-size: 0.95rem; margin-bottom: 1.2rem; }
    .tool-badge {
        display: inline-block;
        background: #E8F5E9;
        color: #1B5E20;
        border-radius: 12px;
        padding: 2px 10px;
        font-size: 0.8rem;
        margin: 2px;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="eco-header">🌿 EcoMarket — Asistente IA</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="eco-sub">Consulta el estado de tus pedidos, políticas y gestiona devoluciones</p>',
    unsafe_allow_html=True,
)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🛠 Herramientas disponibles")
    st.markdown("""
El agente puede usar:
- **consultar_estado_pedido** — Estado de un pedido ECOxxxx
- **verificar_elegibilidad_devolucion** — ¿Puedo devolver?
- **generar_etiqueta_devolucion** — Genera código de devolución
- **buscar_politicas_ecomarket** — FAQs y políticas generales
    """)
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

agent = load_agent()

# ─── ESTADO DE SESIÓN ─────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []       # para mostrar en UI
    st.session_state.lc_history = []     # para LangChain (HumanMessage / AIMessage)

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
            _tool_names = [s["tool"] for s in msg["steps"]]
            with st.expander(f"🔧 Herramientas usadas: {len(_tool_names)}"):
                for step in msg["steps"]:
                    st.markdown(
                        f'<span class="tool-badge">{step["tool"]}</span>',
                        unsafe_allow_html=True,
                    )
                    st.caption(f"**Input:** `{step['input']}`")
                    st.caption(f"**Resultado:** {step['output'][:300]}{'...' if len(step['output']) > 300 else ''}")
                    st.divider()

# ─── INPUT DEL USUARIO ────────────────────────────────────────────────────────

query = st.chat_input("Escribe tu consulta aquí...")

# Manejar sugerencias pendientes
if "_pending" in st.session_state:
    query = st.session_state.pop("_pending")

if query:
    # Mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Obtener respuesta del agente
    with st.chat_message("assistant"):
        with st.spinner("Procesando..."):
            from agente_ecomarket import run_query
            result = run_query(query, st.session_state.lc_history)

        response = result["output"]
        st.markdown(response)

        # Mostrar herramientas usadas si las hay
        steps_display = result.get("steps", [])
        if steps_display:
            tool_names = [s["tool"] for s in steps_display]
            with st.expander(f"🔧 Herramientas usadas: {len(tool_names)}"):
                for step in steps_display:
                    st.markdown(
                        f'<span class="tool-badge">{step["tool"]}</span>',
                        unsafe_allow_html=True,
                    )
                    st.caption(f"**Input:** `{step['input']}`")
                    st.caption(f"**Resultado:** {step['output'][:300]}{'...' if len(step['output']) > 300 else ''}")
                    st.divider()

        if not result["success"]:
            st.error("Hubo un error. Intenta de nuevo o contacta a soporte@ecomarket.com")

    # Actualizar historial
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "steps": steps_display,
    })
    st.session_state.lc_history.extend([
        HumanMessage(content=query),
        AIMessage(content=response),
    ])
