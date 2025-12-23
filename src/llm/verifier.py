"""Verifier: judge whether a record is 'Angkot' or not using heuristics / LLM"""

import os
import json
import yaml
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AngkotVerifier:
    def __init__(self):
        # --- KONFIGURASI OPENROUTER ---
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1", 
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "https://voiye.codelabspace.or.id/", 
                "X-Title": "Voiye",
            }
        )
        
        # Load Prompt Template
        config_path = os.path.join("config", "prompt_templates.yaml")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Template not found in {config_path}")
            
        with open(config_path, "r") as f:
            self.templates = yaml.safe_load(f)

    def _encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def verify(self, image_path, route_data):
        """
        route_data harus memiliki struktur dictionary:
        {
            "route_name": "...",
            "route_code": "...",
            "visual_cues": {
                "primary_color": "...",
                "secondary_color": "...",
                "keywords": [...]
            }
        }
        """
        
        # 1. Ekstrak Data
        visual = route_data.get('visual_cues', {})
        
        raw_keywords = visual.get('keywords', [])
        if isinstance(raw_keywords, list):
            keywords_str = ", ".join(raw_keywords)
        else:
            keywords_str = str(raw_keywords)

        prompt_context = {
            "route_code": route_data.get('route_code', '-'),
            "route_name": route_data.get('route_name', 'Unknown'),
            "primary_color": visual.get('primary_color', 'Warna dominan apa saja'),
            "secondary_color": visual.get('secondary_color', '-'),
            "keywords": keywords_str 
        }

        # 2. Siapkan Prompt
        user_prompt = self.templates['angkot_verification']['user_template'].format(**prompt_context)
        system_prompt = self.templates['angkot_verification']['system']
        base64_image = self._encode_image(image_path)

        # 3. Kirim ke LLM
        try:
            response = self.client.chat.completions.create(
                model="openai/gpt-4o-mini", 
                
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0,
                
                response_format={"type": "json_object"} 
            )

            result_text = response.choices[0].message.content
            return json.loads(result_text)

        except Exception as e:
            print(f"Error Verifier: {e}")
            return {
                "final_decision": False, 
                "visual_analysis": {}, 
                "reason": f"API Error: {str(e)}"
            }