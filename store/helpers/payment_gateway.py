class PaymentGateway:
    @staticmethod

    def process_payment(method: str, amount: float) -> bool:

        if method not in ["MULTICAIXA_EXPRESS", "ATM", "REFERENCE"]:
            raise ValueError("Ivalid payment methode")
        
        return True