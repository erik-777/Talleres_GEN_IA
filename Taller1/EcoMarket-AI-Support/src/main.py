import json
from pathlib import Path

from prompts import ORDER_PROMPT_TEMPLATE, RETURN_PROMPT_TEMPLATE


BASE_DIR = Path(__file__).resolve().parent.parent
ORDERS_FILE = BASE_DIR / "data" / "orders.json"
POLICIES_FILE = BASE_DIR / "data" / "return_policies.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_order_by_tracking(tracking_number, orders):
    for order in orders:
        if order["tracking_number"] == tracking_number:
            return order
    return None


def get_policy_by_category(category, policies):
    for policy in policies:
        if policy["category"].lower() == category.lower():
            return policy
    return None


def simulate_order_response(tracking_number):
    orders = load_json(ORDERS_FILE)
    order = get_order_by_tracking(tracking_number, orders)

    if not order:
        return (
            f"No encontré información para el pedido {tracking_number}. "
            "Por favor verifica el número de seguimiento o contacta a soporte humano."
        )

    response = (
        f"Hola. Revisé el pedido {order['tracking_number']}.\n"
        f"Estado actual: {order['status']}.\n"
        f"Producto: {order['product']}.\n"
        f"Fecha estimada de entrega: {order['estimated_delivery']}.\n"
        f"Puedes seguirlo aquí: {order['tracking_link']}.\n"
    )

    if order["status"].lower() == "retrasado":
        response += (
            f"Lamentamos la demora. Motivo reportado: {order['delay_reason']}"
        )

    return response


def simulate_return_response(product_name, category, package_status, reason):
    policies = load_json(POLICIES_FILE)
    policy = get_policy_by_category(category, policies)

    if not policy:
        return (
            f"No encontré una política específica para la categoría '{category}'. "
            "Tu caso debe ser revisado por un agente humano."
        )

    if policy["return_allowed"]:
        return (
            f"La devolución del producto '{product_name}' sí está permitida.\n"
            f"Condiciones: {policy['conditions']}\n"
            "Siguiente paso: comparte tu número de pedido y evidencia del estado del producto para iniciar el proceso."
        )

    return (
        f"Lamento informarte que la devolución del producto '{product_name}' no está permitida.\n"
        f"Motivo: {policy['conditions']}\n"
        "Si consideras que existe un error o una condición excepcional, el caso puede ser revisado por soporte humano."
    )


if __name__ == "__main__":
    print("=== Consulta de pedido ===")
    print(simulate_order_response("ECO1004"))
    print("\n=== Consulta de devolución ===")
    print(simulate_return_response(
        product_name="Shampoo sólido natural",
        category="productos de higiene",
        package_status="abierto",
        reason="No cumplió mis expectativas"
    ))