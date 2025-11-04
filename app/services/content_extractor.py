from openai import OpenAI
from typing import Dict
import json
import logging

logger = logging.getLogger(__name__)


class ContentExtractor:
    """Service for extracting article content using OpenAI"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
    def extract_content(self, html: str, url: str) -> Dict:
        """
        Extract article content from HTML
        
        Returns:
            {
                "title": str,
                "body": str,
                "images": [str]
            }
        """
        # Truncate HTML to fit within OpenAI token limits
        # gpt-4o-mini supports 128K tokens (~400KB of text)
        # Use 300KB to be safe and leave room for prompt
        html_sample = html[:300000] if len(html) > 300000 else html
        
        prompt = f"""Extract all visible content from this webpage HTML.

Instructions:
1. Extract the page title
2. Extract ALL visible text content including:
   - All paragraphs and text
   - All numbers, prices, percentages, dates exactly as shown
   - All headlines and news
   - All data from tables
   - All statistics and metrics
3. Extract image URLs

Important: Copy the actual text and numbers you see in the HTML. Do not use placeholders.

Format the body content with markdown for readability.

Return JSON:
{{
  "title": "page title",
  "body": "all content with actual values",
  "images": ["url1", "url2"]
}}

HTML:
{html_sample}"""

        try:
            logger.info("Calling OpenAI for content extraction")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting article content from HTML. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Content extraction successful: title='{result.get('title', '')[:50]}...'")
            return result
            
        except Exception as e:
            logger.error(f"Error in content extraction: {str(e)}")
            return {"title": "", "body": "", "images": []}


