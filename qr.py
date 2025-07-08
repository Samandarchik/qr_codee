from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import qrcode
import os
from PIL import Image

app = FastAPI()

class QRRequest(BaseModel):
    text: str

@app.post("/api/generate-qrcode")
def generate_qr_code(request: QRRequest):
    text = request.text.strip()

    if not text:
        raise HTTPException(status_code=400, detail="Text bo'sh bo'lmasligi kerak.")

    # QR code yaratish (High error correction bilan)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # yuqori correction
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # Logotip faylini o'qish
    logo_path = "logo.jpg"
    if not os.path.exists(logo_path):
        raise HTTPException(status_code=404, detail="Logotip (logo.jpg) topilmadi.")

    logo = Image.open(logo_path)

    # Logotip o'lchami (kattaroq qilish uchun factor = 3)
    qr_width, qr_height = qr_img.size
    factor = 3
    logo_size = qr_width // factor
    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

    # ✅ Logotipga oq fon (chegara) qo‘shamiz
    border_size = 20  # px
    logo_with_border = Image.new("RGB", (logo_size + border_size, logo_size + border_size), (255, 255, 255))
    logo_with_border.paste(logo, (border_size // 2, border_size // 2))

    # ✅ QR code ustiga joylashtirish (markazga)
    pos = ((qr_width - logo_with_border.size[0]) // 2, (qr_height - logo_with_border.size[1]) // 2)
    qr_img.paste(logo_with_border, pos)

    # QR code faylini saqlash
    filename_safe = "".join(c if c.isalnum() else "_" for c in text) + ".png"
    if len(filename_safe) > 100:
        filename_safe = filename_safe[:90] + ".png"

    os.makedirs("qrcodes", exist_ok=True)
    file_path = os.path.join("qrcodes", filename_safe)
    qr_img.save(file_path)

    return {
        "message": "Logotipli QR code yaratildi",
        "file_name": filename_safe,
        "text": text,
        "path": file_path
    }
