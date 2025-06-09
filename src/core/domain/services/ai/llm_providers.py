from src.core.infrastructure.clients.ai.clodflare import get_cloudflare_worker_image_response
from src.core.infrastructure.clients.ai.gemini import get_google_gemini_text_response
from src.core.infrastructure.clients.ai.gpt import get_openai_gpt_text_response, get_openai_dalle_image_response
from src.core.infrastructure.clients.ai.openrouter import get_openrouter_deepseek_text_response
from src.core.infrastructure.clients.ai.utils.normalize_and_validate import (
    normalize_llm_chatgpt_response,
    normalize_llm_gemini_response
)

LLM_TEXT_PROVIDERS = {
    'openai': {
        'get_response': get_openai_gpt_text_response,
        'normalize_response': normalize_llm_chatgpt_response,
        'extract_text': lambda r: r.choices[0].message.content.strip(),
        'get_model': lambda r: r.model,
    },
    'gemini': {
        'get_response': get_google_gemini_text_response,
        'normalize_response': normalize_llm_gemini_response,
        'extract_text': lambda r: r['candidates'][0]['content']['parts'][0]['text'].strip(),
        'get_model': lambda r: r.get('modelVersion'),
    },
    'deepseek': {
        'get_response': get_openrouter_deepseek_text_response,
        'normalize_response': normalize_llm_chatgpt_response,
        'extract_text': lambda r: r.choices[0].message.content.strip(),
        'get_model': lambda r: r.model,
    },
}

LLM_IMAGE_PROVIDERS = {
    'openai': {
        'get_response': get_openai_dalle_image_response,
        'get_model': lambda r: r.model,
    },
    'cloudflare': {
        'get_response': get_cloudflare_worker_image_response,
        'get_model': lambda r: r.get('modelVersion'),
    },
}
