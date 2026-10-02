from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class LanguageItem(BaseModel):
    code: str
    name: str
    native_name: str

class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Financial message or claim to analyze")
    language: Optional[str] = Field("en", description="Target language code (e.g. en, gu, hi, ta, mr)")

class RedFlagItem(BaseModel):
    rule_id: str  # e.g., "RF01", "RF02"
    title: str
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    matched_text: Optional[str] = None
    explanation: str
    verification_action: Optional[str] = None
    icon: Optional[str] = "AlertTriangle"

class ClaimItem(BaseModel):
    claim: str
    status: str  # "VERIFIED", "NOT VERIFIED", "NEEDS VERIFICATION", "VERIFY ON OFFICIAL SOURCE"
    explanation: str
    source: str
    source_url: Optional[str] = None

class WhyFlaggedStep(BaseModel):
    step_number: str
    title: str
    description: str

class TrustedSourceItem(BaseModel):
    name: str
    topic: str
    verification_status: str
    url: Optional[str] = None
    summary: Optional[str] = None
    advice: Optional[str] = None

class ActionItem(BaseModel):
    dos: List[str] = []
    donts: List[str] = []

class AnalyzeResponse(BaseModel):
    id: str
    risk_level: str  # "LOW RISK", "NEEDS VERIFICATION", "HIGH RISK"
    risk_score: int  # 0 to 100
    summary: str
    red_flags: List[RedFlagItem]
    claims: List[ClaimItem]
    recommended_actions: List[str]
    action_dos: List[str] = []
    action_donts: List[str] = []
    why_flagged: List[WhyFlaggedStep] = []
    trusted_sources: List[TrustedSourceItem] = []
    raw_text: Optional[str] = None
    created_at: Optional[str] = None
    language: Optional[str] = "en"
    language_name: Optional[str] = "English"

class TranslateRequest(BaseModel):
    language: str = Field(..., description="Target language code (e.g. gu, ta, hi)")
    analysis_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

class HistoryItemSummary(BaseModel):
    id: str
    created_at: str
    message_preview: str
    risk_level: str
    risk_score: int
    red_flags_count: int

class HealthResponse(BaseModel):
    status: str
    version: str
    ai_enabled: bool
    ai_provider: str
    ai4bharat_enabled: bool
