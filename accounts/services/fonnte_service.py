import requests


FONNTE_TOKEN = "r3fTKAsx4LVow6e8yP1J"


def send_whatsapp_otp(
    number,
    otp
):

    message = (
        f"Kode OTP FINDIT AI Anda adalah: {otp}\n\n"
        f"Jangan bagikan kode ini kepada siapa pun."
    )

    url = "https://api.fonnte.com/send"

    payload = {
        "target": number,
        "message": message
    }

    headers = {
        "Authorization": FONNTE_TOKEN
    }

    response = requests.post(
        url,
        data=payload,
        headers=headers
    )

    return response.json()