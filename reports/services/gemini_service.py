import requests
import base64
import json


# =========================
# GEMINI API KEY
# =========================
API_KEY = "AIzaSyB8Qe0mbxscRgZjSLIZyuORzrxWsZhtrTc"


# =========================
# ANALYZE IMAGE
# =========================
def analyze_image(image_file):

    try:

        #
        # READ IMAGE
        #

        image_bytes = image_file.read()

        image_base64 = base64.b64encode(
            image_bytes
        ).decode('utf-8')

        mime_type = image_file.content_type

        #
        # GEMINI ENDPOINT
        #

        url = (
            "https://generativelanguage.googleapis.com/"
            "v1beta/models/gemini-3-flash-preview:generateContent"
        )

        #
        # PROMPT
        #

        prompt = """

        Analisis gambar barang lost and found ini.

        Jawab HANYA JSON VALID.

        Format:

        {
            "nama_barang":"...",
            "kategori":"...",
            "warna":"...",
            "merek":"...",
            "deskripsi":"..."
        }

        RULE:
        - tanpa markdown
        - tanpa penjelasan tambahan
        - kategori hanya:
          Elektronik,
          Handphone,
          Laptop,
          Tas,
          Dompet,
          Kunci,
          Dokumen,
          Aksesoris,
          Botol Minum,
          Helm,
          Lainnya

        """

        #
        # PAYLOAD
        #

        payload = {

            "contents": [

                {

                    "parts": [

                        {
                            "text": prompt
                        },

                        {

                            "inline_data": {

                                "mime_type": mime_type,

                                "data": image_base64

                            }

                        }

                    ]

                }

            ]

        }

        #
        # REQUEST GEMINI
        #

        response = requests.post(

            url,

            headers={

                "x-goog-api-key": API_KEY,

                "Content-Type": "application/json"

            },

            json=payload,

            timeout=60

        )

        #
        # RESPONSE
        #

        result = response.json()

        print(result)

        #
        # ERROR GEMINI
        #

        if "error" in result:

            return {

                "error":
                result["error"]["message"]

            }

        #
        # GET AI TEXT
        #

        text_response = result[
            "candidates"
        ][0][
            "content"
        ][
            "parts"
        ][0][
            "text"
        ]

        #
        # CLEAN JSON
        #

        clean_text = (
            text_response
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        #
        # PARSE JSON
        #

        parsed = json.loads(
            clean_text
        )

        #
        # RETURN RESULT
        #

        return parsed

    except Exception as e:

        print(e)

        return {

            "error": str(e)

        }