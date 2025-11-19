import json

def load_orders():
    with open("backend/order_data.json", "r") as f:
        return json.load(f)

def process_refund(email, last4, order_number):
    data = load_orders()

    for cust in data["customers"]:
        if cust["email"].lower() == email.lower() and cust["last4"] == last4:
            for order in cust["orders"]:
                if order["order_number"] == order_number:
                    
                    if order["eligible"]:
                        return {
                            "status": "approved",
                            "refund_id": "RFND-" + order["order_id"],
                            "amount": order["total"]
                        }
                    else:
                        return {
                            "status": "denied",
                            "reason": "Order not eligible for refund"
                        }

    return {
        "status": "error",
        "reason": "Customer or order not found"
    }
