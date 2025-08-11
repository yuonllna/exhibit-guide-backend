import qrcode

def generate_qr_code(data: str, save_path: str) -> str:
    img = qrcode.make(data)
    img.save(save_path)
    return save_path