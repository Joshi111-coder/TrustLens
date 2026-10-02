from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.schemas import (
    AnalyzeRequest, 
    AnalyzeResponse, 
    HistoryItemSummary, 
    LanguageItem, 
    TranslateRequest
)
from app.services.ai_service import analyze_financial_content
from app.services.ocr_service import extract_text_from_image_bytes
from app.services.language_service import (
    SUPPORTED_LANGUAGES, 
    translate_analysis_findings, 
    get_language_info
)
from app.database.database import save_analysis, get_history, get_analysis_by_id

router = APIRouter(tags=["Analysis"])

@router.get("/languages", response_model=List[LanguageItem])
def get_supported_languages():
    """Returns all 22 scheduled Indian languages plus English."""
    return SUPPORTED_LANGUAGES

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_text(request: AnalyzeRequest):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    target_lang = request.language or "en"
    analysis_result = analyze_financial_content(request.text.strip(), language=target_lang)
    save_analysis(analysis_result)
    return analysis_result

@router.post("/analyze-image", response_model=AnalyzeResponse)
async def analyze_image(
    file: UploadFile = File(...),
    language: Optional[str] = Form("en")
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a valid image format.")
    
    try:
        contents = await file.read()
        extracted_text = extract_text_from_image_bytes(contents, filename=file.filename or "upload.png")
        
        if not extracted_text or not extracted_text.strip():
            extracted_text = "No distinct financial text could be extracted from this image. Please ensure high clarity."

        target_lang = language or "en"
        analysis_result = analyze_financial_content(extracted_text, language=target_lang)
        save_analysis(analysis_result)
        return analysis_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process screenshot: {str(e)}")

@router.post("/translate", response_model=AnalyzeResponse)
def translate_result(request: TranslateRequest):
    """
    Translates an existing analysis result into the user's selected language
    without modifying the underlying deterministic risk score or classification.
    """
    target_lang = request.language or "en"
    
    # 1. If analysis_id is provided, fetch existing record from DB
    if request.analysis_id:
        record = get_analysis_by_id(request.analysis_id)
        if not record:
            raise HTTPException(status_code=404, detail="Analysis record not found.")
        translated = translate_analysis_findings(record, target_lang)
        save_analysis(translated)
        return translated

    # 2. If result object is provided directly, translate in-memory
    if request.result:
        translated = translate_analysis_findings(request.result, target_lang)
        return translated

    raise HTTPException(status_code=400, detail="Either analysis_id or result object must be provided.")

@router.get("/history", response_model=List[HistoryItemSummary])
def get_analysis_history(limit: int = 50):
    return get_history(limit=limit)

@router.get("/history/{analysis_id}", response_model=AnalyzeResponse)
def get_historical_analysis(analysis_id: str):
    record = get_analysis_by_id(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis record not found.")
    return record
