"""API: FastAPI app for Angkot verification.

Initializes `ObjectDetector` (YOLO) and `AngkotVerifier` (LLM) and exposes
an endpoint `/verify-angkot` that accepts image uploads and verifies
whether the image matches a target angkot route based on color and text
criteria
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
from src.vision.detector import ObjectDetector
from src.llm.verifier import AngkotVerifier
from typing import Optional
import logging

# Setup Logging agar error terlihat di terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Inisialisasi Model
try:
    detector = ObjectDetector()
    verifier = AngkotVerifier()
except Exception as e:
    logger.error(f"FATAL: Failed to load AI model. {e}")
    # Jika model gagal load saat start, aplikasi tidak boleh jalan
    raise RuntimeError("Model Initialization Failed")

@app.get("/")
def read_root():
    return {"status": "AI Service Ready"}

@app.post("/verify-angkot", status_code=status.HTTP_200_OK)
async def verify_angkot(
    file: UploadFile = File(...),
    route_name: str = Form(...),
    primary_color: str = Form(...),
    secondary_color: str = Form(""), 
    keywords: str = Form("")
):
    """
    Endpoint Verifikasi Angkot.
    Returns:
    - 200: Proses sukses (bisa Match atau Ignored).
    - 400: File gambar rusak/kosong.
    - 502: Error koneksi ke OpenRouter.
    - 500: Error internal server.
    """
    
    # 1. VALIDASI INPUT (400 Bad Request)
    try:
        image_bytes = await file.read()
        if len(image_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Empty image file."
            )
    except Exception as e:
        logger.error(f"Upload Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Failed to read uploaded file."
        )

    try:
        # 2. TAHAP YOLO (Gatekeeper)
        # Jika YOLO gagal memproses gambar (bukan karena tidak ada mobil, tapi error cv2), itu 500.
        found, msg, img_cv = detector.detect_potential_vehicle(image_bytes)
        
        if not found:
            # Ini BUKAN error, tapi hasil valid bahwa tidak ada objek.
            # Tetap return 200 OK.
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "ignored",
                    "message": "No target vehicle detected.",
                    "action": "STAY_SILENT"
                }
            )
        
        if keywords.strip():
            # Jika ada isinya "05, CICAHEUM", potong jadi list ["05", "CICAHEUM"]
            keywords_list = [k.strip() for k in keywords.split(",")]
        else:
            # Jika kosong, jadi list kosong []
            keywords_list = []

        # 3. PERSIAPAN DATA
        manual_route_data = {
            "route_name": route_name,
            "visual_cues": {
                "primary_color": primary_color,
                "secondary_color": secondary_color if secondary_color else "None", 
                "keywords": keywords_list 
            },
            "route_code": "USER_REQ",
            "stops": []
        }

        # 4. TAHAP LLM (The Judge)
        temp_filename = "temp_capture.jpg"
        with open(temp_filename, "wb") as f:
            f.write(image_bytes)
            
        logger.info(f"Sending to LLM: {route_name}")
        
        llm_result = verifier.verify(temp_filename, manual_route_data)
        
        # Cek apakah LLM mengembalikan Error (misal: API Key salah, Saldo habis, OpenRouter down)
        reason = llm_result.get("reason", "")
        if "API Error" in reason or "System Error" in reason:
            logger.error(f"LLM Error: {reason}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY, 
                detail=f"Failed to process AI: {reason}"
            )

        # 5. KEPUTUSAN SUKSES (200 OK)
        is_match = llm_result.get("final_decision", False)
        action = "VIBRATE" if is_match else "IGNORE"
        
        return {
            "status": "processed",
            "yolo_detection": msg,
            "request_context": {
                "target": route_name,
                "colors": f"{primary_color} & {secondary_color}"
            },
            "llm_analysis": llm_result,
            "action": action
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Internal Server Error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")