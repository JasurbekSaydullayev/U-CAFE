def check_phone_number(phone_number: str):
    if not phone_number[1:].isdigit() or len(phone_number) != 13 or not phone_number.startswith('+998'):
        return False
    return True
