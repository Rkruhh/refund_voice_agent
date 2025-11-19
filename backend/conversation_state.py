import re

class ConversationState:
    def __init__(self):
        self.email = None
        self.last4 = None
        self.order_number = None

    # -------------------------
    # Email extraction
    # -------------------------
    def extract_email(self, text):
        t = text.lower()

        # Convert spoken forms
        t = t.replace(" at ", "@")
        t = t.replace(" dot ", ".")
        t = t.replace(" underscore ", "_")
        t = t.replace(" dash ", "-")

        # Regex detect
        match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", t)
        return match.group(0) if match else None

    # -------------------------
    # Last 4 extraction
    # -------------------------
    def extract_last4(self, text):
        t = text.lower()

        spoken_to_digit = {
            "zero": "0", "0": "0",
            "one": "1", "won": "1", "1": "1",
            "two": "2", "to": "2", "too": "2", "tu": "2", "2": "2",
            "three": "3", "tree": "3", "3": "3",
            "four": "4", "for": "4", "fore": "4",
            "photo": "4", "fodo": "4", "fodo": "4",
            "fouro": "4", "fodo": "4", "fodo": "4", "4": "4",
            "five": "5", "fife": "5", "5": "5",
            "six": "6", "sex": "6", "6": "6",
            "seven": "7", "sevan": "7", "7": "7",
            "eight": "8", "ate": "8", "ait": "8", "8": "8",
            "nine": "9", "nein": "9", "9": "9"
        }

        # Convert spoken → digits
        for word, digit in spoken_to_digit.items():
            t = t.replace(word, digit)

        digits = "".join(ch for ch in t if ch.isdigit())
        print(f"[DEBUG] Raw last4 text: '{text}' → parsed digits: '{digits}'")

        if len(digits) >= 4:
            return digits[-4:]  # take last 4 if too many
        return None

    # -------------------------
    # Order extraction
    # -------------------------
    def extract_order(self, text):
        t = text.lower()
        if "one" in t or "1" in t:
            return 1
        if "two" in t or "2" in t:
            return 2
        return None

    # -------------------------
    # Main processor
    # -------------------------
    def process(self, text):

        # Email
        if self.email is None:
            email = self.extract_email(text)
            if email:
                self.email = email
                return "email_captured"

        # Last 4
        if self.last4 is None:
            last4 = self.extract_last4(text)
            if last4:
                self.last4 = last4
                return "last4_captured"

        # Order
        if self.order_number is None:
            number = self.extract_order(text)
            if number:
                self.order_number = number
                return "order_captured"

        return None

    def is_ready(self):
        return bool(self.email and self.last4 and self.order_number)
