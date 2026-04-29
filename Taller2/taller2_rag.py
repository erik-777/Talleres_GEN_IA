import os
import json
from pathlib import Path
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate

# 1. Configuración de Rutas y Variables
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
DB_DIR = BASE_DIR / "chroma_db"
ORDERS_FILE = BASE_DIR / "legacy_data" / "orders.json"

# 2. Funciones de Soporte (Workshop 1 Logic)
def get_order_details(tracking_number):
    """Busca los detalles de un pedido en la base de datos JSON (Taller 1)."""
    if not ORDERS_FILE.exists():
        return None
    
    with open(ORDERS_FILE, "r", encoding="utf-8") as f:
        orders = json.load(f)
        
    for order in orders:
        if order["tracking_number"].upper() == tracking_number.upper():
            return order
    return None

# 3. Inicialización del Sistema RAG
def initialize_rag_system():
    print("--- Inicializando Sistema RAG Integrado---")
    
    if not KNOWLEDGE_BASE_DIR.exists():
        KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)

    loader = DirectoryLoader(KNOWLEDGE_BASE_DIR, glob="**/*.md", loader_cls=TextLoader)
    documents = loader.load()
    
    if not documents:
        print("Advertencia: No se encontraron documentos en la base de conocimiento.")
        return None

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(DB_DIR)
    )
    return vector_db

# 4. Configuración de la Cadena de Respuesta
def setup_qa_chain(vector_db):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    
    template = """
    Eres un asistente de atención al cliente experto de EcoMarket.
    Tu objetivo es ayudar a los clientes usando la información de la base de conocimiento o datos de pedidos.

    CONTEXTO RECUPERADO (Políticas, FAQs, Catálogo):
    {context}

    INSTRUCCIONES:
    1. Si el usuario pregunta por un pedido (ej: ECO1001), verifica si los DATOS DE PEDIDO están presentes abajo.
    2. Si los DATOS DE PEDIDO están presentes, usa esa información para responder siguiendo el tono de EcoMarket.
    3. Si el usuario pregunta algo general, usa el CONTEXTO RECUPERADO.
    4. Si no tienes la información en ninguno de los dos casos, di que no sabes y ofrece ayuda humana.

    {order_info_block}

    PREGUNTA DEL USUARIO: 
    {question}

    RESPUESTA:"""
    
    return llm, template

# 5. Lógica de Ejecución Integrada
def process_query(query, vector_db, llm, template):
    # Detección simple de número de seguimiento (Workshop 1)
    import re
    tracking_match = re.search(r"ECO\d+", query.upper())
    order_info_block = ""
    
    if tracking_match:
        tracking_number = tracking_match.group(0)
        order = get_order_details(tracking_number)
        if order:
            order_info_block = f"""
            DATOS DE PEDIDO ENCONTRADOS:
            - Tracking: {order['tracking_number']}
            - Estado: {order['status']}
            - Producto: {order['product']}
            - Entrega Estimada: {order['estimated_delivery']}
            - Link: {order['tracking_link']}
            """
        else:
            order_info_block = f"\nDATOS DE PEDIDO: No se encontró el pedido {tracking_number} en el sistema.\n"

    # Recuperación RAG
    docs = vector_db.similarity_search(query, k=3)
    context = "\n".join([doc.page_content for doc in docs])
    
    # Generación de respuesta
    prompt = template.format(
        context=context,
        question=query,
        order_info_block=order_info_block
    )
    
    response = llm.invoke(prompt)
    return response.content

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: Configura OPENAI_API_KEY.")
    else:
        vdb = initialize_rag_system()
        if vdb:
            llm, template = setup_qa_chain(vdb)
            
            test_queries = [
                "¿Cuál es el estado de mi pedido ECO1004?", # De Taller 1
                "¿Puedo devolver un cepillo de dientes si ya lo abrí?", # De Taller 1 (integrado a RAG)
                "¿Cuál es el plazo general para devoluciones?", # De Taller 2
                "¿Tienen envíos a Cali?" # De Taller 2
            ]
            
            for q in test_queries:
                print(f"\n>>> USUARIO: {q}")
                res = process_query(q, vdb, llm, template)
                print(f">>> ASISTENTE: {res}")
