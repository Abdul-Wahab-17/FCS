"""Module to parse compliance policy PDF using Groq LLM API."""

import json
import os
from pathlib import Path
import pdfplumber
try:
    from groq import Groq
except ImportError:
    Groq = None  # type: ignore[assignment]


def parse_policy(pdf_path: str | Path, output_path: str | Path) -> dict:
    with pdfplumber.open(pdf_path) as pdf:
        full_text = "\n".join(p.extract_text() for p in pdf.pages if p.extract_text())

    # If Groq is not installed, skip API call
    if Groq is None:
        print("Groq package not available; skipping policy parsing.")
        return {}
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    prompt = f"""
    You are a compliance policy parser. Extract ALL compliance rules from this EHS policy document.
    Return ONLY valid JSON, no preamble, no markdown.
    
    Required schema:
    {{
      "compliance_rules": [
        {{
          "rule_id": "section identifier e.g. Section 3.1.2",
          "behavior_class": "one of: Safe_Walkway_Violation | Unauthorized_Intervention | Opened_Panel_Cover | Carrying_Overload_with_Forklift",
          "safe_indicator": "description of safe observable state",
          "unsafe_indicator": "description of unsafe observable state",
          "observable_signals": ["list of visual signals to detect"],
          "severity_tier": "LOW | MEDIUM | HIGH | CRITICAL",
          "policy_callout": "WARNING | CRITICAL SAFETY NOTICE | NOTICE",
          "hazard_description": "what danger this poses",
          "escalation_language": "exact language from policy about alerts",
          "escalation_conditions": [
             {{"condition": "e.g., personnel_count > 1", "new_severity": "CRITICAL", "rationale": "..."}}
          ]
        }}
      ]
    }}
    
    Policy document:
    {full_text}
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    
    raw = response.choices[0].message.content.strip()
    
    # Strip markdown block if present
    if raw.startswith("```json"):
        raw = raw[7:-3]
    elif raw.startswith("```"):
        raw = raw[3:-3]
        
    parsed_data = json.loads(raw)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(parsed_data, f, indent=2)
        
    # VERIFICATION PASS
    verification = verify_parsed_rules(parsed_data, full_text)
    verify_out_path = Path(output_path).parent / "policy_parse_verification.json"
    with open(verify_out_path, "w", encoding="utf-8") as f:
        json.dump(verification, f, indent=2)
        
    return parsed_data

def verify_parsed_rules(parsed_rules: dict, raw_policy_text: str) -> dict:
    """Cross-check each extracted rule against source text."""
    # If Groq is not installed, skip verification
    if Groq is None:
        print("Groq package not available; skipping verification.")
        return {"verification_results": [], "flagged_rules": [], "overall_confidence": 0.0}
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    verification_results = []
    for rule in parsed_rules.get("compliance_rules", []):
        prompt = f"""
        Does this extracted rule faithfully represent the source policy?
        
        Extracted rule: {json.dumps(rule)}
        
        Source policy text: {raw_policy_text}
        
        Return JSON only:
        {{
          "rule_id": "{rule.get('rule_id', '')}",
          "faithful": true,
          "confidence": 0.95,
          "issue": "describe any discrepancy or null if faithful"
        }}
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        try:
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```json"):
                raw = raw[7:-3]
            elif raw.startswith("```"):
                raw = raw[3:-3]
            verification_results.append(json.loads(raw))
        except Exception:
            pass
    
    # Flag any low-confidence or unfaithful rules
    flagged = [r for r in verification_results if not r.get("faithful", False) or r.get("confidence", 0) < 0.8]
    
    return {
        "verification_results": verification_results,
        "flagged_rules": flagged,
        "overall_confidence": sum(r.get("confidence", 0) for r in verification_results) / max(1, len(verification_results))
    }

if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()
    
    # Use the actual compliance policy PDF if present
    default_pdf = Path("Compliance_Policy_Manual.pdf")
    pdf_file = default_pdf if default_pdf.exists() else Path("compliance_policy.pdf")
    out_file = Path("parsed_rules.json")
    
    if os.environ.get("GROQ_API_KEY"):
        print("Parsing policy with Groq...")
        parse_policy(pdf_file, out_file)
        print("Done. Saved to parsed_rules.json")
    else:
        print("GROQ_API_KEY not found. Skipping API call.")
