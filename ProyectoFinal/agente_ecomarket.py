import os
import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

BASE_DIR = Path(__file__).resolve().parent
TALLER2_DIR = BASE_DIR.parent / "Taller2"
load_dotenv(TALLER2_DIR / ".env")

# ─── RUTAS ──────────────────────────────────────────────────────────────────
KNOWLEDGE_BASE_DIR = TALLER2_DIR / "knowledge_base"
DB_DIR = BASE_DIR / "chroma_db"
ORDERS_FILE = TALLER2_DIR / "legacy_data" / "orders.json"
RETURN_POLICIES_FILE = TALLER2_DIR / "legacy_data" / "return_policies.json"

# Mapeo producto → categoría de política
PRODUCT_CATEGORY_MAP = {
    "botella": "botellas",
    "cepillo": "cepillos",
    "cubiertos": "cubiertos reutilizables",
    "shampoo": "productos de higiene",
    "jabón": "productos de higiene",
    "jabon": "productos de higiene",
    "esponja": "productos perecederos",
    "higiene": "productos de higiene",
    "contenedor": "contenedores de vidrio",
    "vaso": "cubiertos reutilizables",
}

# ─── HELPERS INTERNOS ────────────────────────────────────────────────────────

def _load_orders() -> list:
    if not ORDERS_FILE.exists():
        return []
    with open(ORDERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _load_policies() -> list:
    if not RETURN_POLICIES_FILE.exists():
        return []
    with open(RETURN_POLICIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _get_order(tracking_number: str) -> dict | None:
    for order in _load_orders():
        if order["tracking_number"].upper() == tracking_number.upper():
            return order
    return None

def _get_policy_for_product(product_name: str) -> dict | None:
    product_lower = product_name.lower()
    for keyword, category in PRODUCT_CATEGORY_MAP.items():
        if keyword in product_lower:
            for policy in _load_policies():
                if policy["category"] == category:
                    return policy
    return None

# ─── RAG (singleton) ─────────────────────────────────────────────────────────

_vector_db = None

def get_vector_db():
    global _vector_db
    if _vector_db is not None:
        return _vector_db

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Reutiliza la DB persistida si ya existe
    if DB_DIR.exists() and any(DB_DIR.iterdir()):
        _vector_db = Chroma(
            persist_directory=str(DB_DIR),
            embedding_function=embeddings,
        )
        return _vector_db

    if not KNOWLEDGE_BASE_DIR.exists():
        print(f"ADVERTENCIA: No se encontró knowledge_base en {KNOWLEDGE_BASE_DIR}")
        return None

    loader = DirectoryLoader(
        str(KNOWLEDGE_BASE_DIR), glob="**/*.md", loader_cls=TextLoader
    )
    documents = loader.load()
    if not documents:
        print("ADVERTENCIA: knowledge_base vacía.")
        return None

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    _vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(DB_DIR),
    )
    return _vector_db

# ─── TOOLS DEL AGENTE ────────────────────────────────────────────────────────

@tool
def consultar_estado_pedido(numero_seguimiento: str) -> str:
    """Consulta el estado actual de un pedido usando su número de seguimiento (formato ECOxxxx).
    Devuelve estado, producto, cliente, fecha estimada de entrega y enlace de tracking.
    Úsala cuando el cliente pregunte por el estado o ubicación de un pedido."""
    order = _get_order(numero_seguimiento)
    if not order:
        return f"No se encontró ningún pedido con el número '{numero_seguimiento}'."

    lines = [
        f"Pedido {order['tracking_number']}:",
        f"  - Cliente:           {order['customer_name']}",
        f"  - Producto:          {order['product']}",
        f"  - Estado:            {order['status']}",
        f"  - Entrega estimada:  {order['estimated_delivery']}",
        f"  - Enlace tracking:   {order['tracking_link']}",
    ]
    if order.get("delay_reason"):
        lines.append(f"  - Motivo del retraso: {order['delay_reason']}")
    return "\n".join(lines)


@tool
def verificar_elegibilidad_devolucion(numero_seguimiento: str) -> str:
    """Verifica si un pedido es elegible para devolución según las políticas de EcoMarket.
    Comprueba que el pedido esté en estado 'Entregado' y que el producto cumpla la política
    de su categoría. Siempre llama esta herramienta ANTES de generar una etiqueta de devolución."""
    order = _get_order(numero_seguimiento)
    if not order:
        return f"Pedido '{numero_seguimiento}' no encontrado. No es posible verificar elegibilidad."

    if order["status"].lower() != "entregado":
        return (
            f"Pedido {numero_seguimiento} ({order['product']}) NO es elegible. "
            f"Estado actual: '{order['status']}'. Solo se pueden devolver pedidos ya entregados."
        )

    policy = _get_policy_for_product(order["product"])
    if not policy:
        return (
            f"Pedido {numero_seguimiento} ({order['product']}) fue entregado. "
            "Sin política específica encontrada: se aplica política general de 30 días "
            "en empaque original sin uso. ELEGIBLE."
        )

    if not policy["return_allowed"]:
        return (
            f"Pedido {numero_seguimiento} ({order['product']}) NO es elegible. "
            f"Razón: {policy['conditions']}"
        )

    return (
        f"Pedido {numero_seguimiento} ({order['product']}) ES ELEGIBLE para devolución. "
        f"Cliente: {order['customer_name']}. "
        f"Condiciones: {policy['conditions']}"
    )


@tool
def generar_etiqueta_devolucion(numero_seguimiento: str, motivo_devolucion: str) -> str:
    """Genera una etiqueta de devolución para un pedido elegible.
    Requiere el número de seguimiento y el motivo declarado por el cliente.
    SOLO llamar DESPUÉS de confirmar elegibilidad con verificar_elegibilidad_devolucion.
    Devuelve un código único de devolución, fecha de vencimiento e instrucciones."""
    order = _get_order(numero_seguimiento)
    if not order:
        return f"No se puede generar etiqueta: pedido '{numero_seguimiento}' no encontrado."

    label_code = f"RET-{uuid.uuid4().hex[:8].upper()}"
    expiry = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")

    return (
        f"ETIQUETA DE DEVOLUCIÓN GENERADA\n"
        f"{'─' * 42}\n"
        f"Código de devolución : {label_code}\n"
        f"Pedido original      : {numero_seguimiento}\n"
        f"Producto             : {order['product']}\n"
        f"Cliente              : {order['customer_name']}\n"
        f"Motivo declarado     : {motivo_devolucion}\n"
        f"Válida hasta         : {expiry}\n"
        f"{'─' * 42}\n"
        f"Instrucciones: Pegue esta etiqueta en el paquete sellado. Puede depositarlo "
        f"en cualquier punto EcoMarket o solicitar recolección a domicilio en "
        f"ecomarket.com/devoluciones/{label_code}"
    )


@tool
def buscar_politicas_ecomarket(consulta: str) -> str:
    """Busca información en la base de conocimiento de EcoMarket: políticas de devolución,
    preguntas frecuentes, categorías de productos y condiciones especiales.
    Úsala para responder preguntas generales sobre políticas, envíos o tiempos de reembolso."""
    vdb = get_vector_db()
    if not vdb:
        return "No se pudo acceder a la base de conocimiento de EcoMarket."

    docs = vdb.similarity_search(consulta, k=3)
    if not docs:
        return "No se encontró información relevante en la base de conocimiento."

    return "\n\n---\n\n".join(doc.page_content for doc in docs)

# ─── AGENTE ──────────────────────────────────────────────────────────────────

TOOLS = [
    consultar_estado_pedido,
    verificar_elegibilidad_devolucion,
    generar_etiqueta_devolucion,
    buscar_politicas_ecomarket,
]

SYSTEM_PROMPT = """Eres el Agente de Atención al Cliente de EcoMarket, una tienda de productos ecológicos y sostenibles.

Tienes acceso a las siguientes herramientas:
- consultar_estado_pedido: para saber el estado/ubicación de un pedido
- verificar_elegibilidad_devolucion: para saber si un pedido puede devolverse
- generar_etiqueta_devolucion: para crear la etiqueta que el cliente necesita para devolver
- buscar_politicas_ecomarket: para responder preguntas generales sobre políticas, FAQs, plazos

FLUJO OBLIGATORIO PARA DEVOLUCIONES:
1. Llama a verificar_elegibilidad_devolucion con el número de pedido
2. Si el resultado dice que ES ELEGIBLE → pregunta el motivo al cliente (si no lo ha dado) y llama a generar_etiqueta_devolucion
3. Si NO ES ELEGIBLE → explica amablemente la razón y ofrece alternativas (contacto humano)

REGLAS:
- Responde siempre en español, con tono empático y profesional
- No inventes información; basa tus respuestas únicamente en lo que devuelven las herramientas
- Si no puedes resolver el problema, ofrece escalar a un agente humano en soporte@ecomarket.com
- Para cualquier pregunta de política o FAQ, usa buscar_politicas_ecomarket"""


def create_agent():
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    return create_react_agent(llm, TOOLS, prompt=SYSTEM_PROMPT)


_agent = None


def get_agent():
    global _agent
    if _agent is None:
        _agent = create_agent()
    return _agent


def _extract_steps(messages: list) -> list:
    """Extrae los pares (tool_name, input, output) del historial de mensajes."""
    steps = []
    pending: dict[str, dict] = {}

    for msg in messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                pending[tc["id"]] = {"tool": tc["name"], "input": tc["args"]}
        elif isinstance(msg, ToolMessage) and msg.tool_call_id in pending:
            entry = pending.pop(msg.tool_call_id)
            entry["output"] = msg.content
            steps.append(entry)

    return steps


def run_query(query: str, chat_history: list | None = None) -> dict:
    """Ejecuta una consulta en el agente. Devuelve output y pasos intermedios."""
    agent = get_agent()
    history = chat_history or []
    try:
        result = agent.invoke({"messages": history + [HumanMessage(content=query)]})
        output = result["messages"][-1].content
        steps = _extract_steps(result["messages"])
        return {"success": True, "output": output, "steps": steps}
    except Exception as e:
        return {
            "success": False,
            "output": f"Ocurrió un error: {str(e)}. Contacta a soporte@ecomarket.com.",
            "steps": [],
        }


# ─── DEMO EN TERMINAL ────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: Define OPENAI_API_KEY en el archivo .env del Taller2")
    else:
        print("Inicializando base de conocimiento RAG...")
        get_vector_db()
        print("Agente listo.\n")

        test_queries = [
            "¿Cuál es el estado de mi pedido ECO1004?",
            "Quiero devolver el pedido ECO1002, ¿puedo?",
            "Quiero devolver el pedido ECO1002, llegó defectuoso",
            "Quiero devolver el pedido ECO1001",
            "¿Cuál es el plazo general para devoluciones?",
        ]

        for q in test_queries:
            print(f"\n{'=' * 60}")
            print(f"USUARIO: {q}")
            result = run_query(q)
            if result["steps"]:
                print(f"  [Tools: {', '.join(s['tool'] for s in result['steps'])}]")
            print(f"AGENTE: {result['output']}")
