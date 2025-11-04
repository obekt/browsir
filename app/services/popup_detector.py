from openai import OpenAI
from typing import Dict
import json
import logging

logger = logging.getLogger(__name__)


class PopupDetector:
    """Service for detecting popups and cookie banners using OpenAI"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
    def detect_popups(self, html: str) -> Dict:
        """
        Analyze HTML to detect popups, modals, and cookie banners
        
        Returns:
            {
                "popups_found": bool,
                "elements": [{"type": str, "selector": str, "confidence": float}]
            }
        """
        # Truncate HTML if too large (keep first 50k chars)
        html_sample = html[:50000] if len(html) > 50000 else html
        
        prompt = f"""You are analyzing a webpage HTML to find and dismiss consent/cookie popups so we can access the actual content.

TASK: Find the EXACT button/link to click to dismiss the consent form and access the page content.

STEP 1 - DETECT CONSENT FORM:
Look for text indicating consent/cookies in ANY language:
- English: "cookie", "consent", "privacy", "accept", "agree", "continue"
- Bulgarian: "бисквитки", "съгласие", "поверителност", "приемане"
- Other languages: similar terms

STEP 2 - FIND THE DISMISS BUTTON:
Search the HTML for the ACTUAL button element that dismisses the popup. Look for:
1. Button text containing: "Accept", "Agree", "Continue", "OK", "I Accept", "Приемане на всички", "Съгласен"
2. Button elements: <button>, <a>, <input type="submit">, <div role="button">
3. Extract the EXACT attributes from the HTML:
   - id attribute: button#consent-accept
   - class names: button.btn-primary.accept-btn
   - name attribute: button[name="agree"]
   - data attributes: button[data-action="accept"]
   - aria-label: button[aria-label="Accept cookies"]

STEP 3 - BUILD PRECISE SELECTOR:
Create a CSS selector that will uniquely identify this button:
- Prefer ID if available: "#consent-accept"
- Use specific classes: ".consent-button.primary"
- Combine attributes: "button[name='agree'].btn-primary"
- Use text content as last resort: "button:has-text('Accept')"

IMPORTANT:
- Return the MOST SPECIFIC selector that exists in the HTML
- If multiple buttons exist, choose the "Accept All" or primary action button
- DO NOT return generic selectors like "button[role='button']" - find the ACTUAL button
- Look inside forms, divs, iframes for the button

Return ONLY valid JSON:
{{
  "popups_found": true/false,
  "elements": [
    {{
      "type": "button",
      "selector": "the-exact-css-selector-from-html",
      "button_text": "the actual button text",
      "confidence": 0.0-1.0
    }}
  ]
}}

If no consent form found, return: {{"popups_found": false, "elements": []}}

HTML to analyze:
{html_sample}"""

        try:
            logger.info("Calling OpenAI for popup detection")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing HTML and identifying popup elements. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Popup detection result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in popup detection: {str(e)}")
            return {"popups_found": False, "elements": []}


