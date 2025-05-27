import google.generativeai as genai
from time import sleep
import json
from utils.logger import logger

class GeminiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = None
        self.retry_count = 3
        self.base_delay = 5  # Base delay in seconds
        self.max_delay = 60  # Maximum delay in seconds        # Correct model names for free Gemma models
        self.free_models = ['models/gemma-3-1b-it', 'models/gemma-3-4b-it', 'models/gemma-3-12b-it', 'models/gemma-3-27b-it']
        self.current_model_index = 0  # Track which model we're currently using

    def initialize_model(self, model_name='gemini-1.5-flash'):
        """Initialize the Gemini model with retries and fallback to free models"""
        self.preferred_model = model_name
        return self._try_initialize_model(model_name)

    def _try_initialize_model(self, model_name):
        """Try to initialize a specific model with retries"""
        for attempt in range(self.retry_count):
            try:
                self.model = genai.GenerativeModel(model_name)
                logger.info(f"Successfully initialized model: {model_name}")
                return True
            except Exception as e:
                error_str = str(e)
                if ("quota" in error_str.lower() or "404" in error_str) and self._try_next_free_model():
                    return True
                if self._should_retry(e, attempt):
                    continue
                raise

    def _try_next_free_model(self):
        """Try to initialize the next available free model"""
        initial_index = self.current_model_index  # Remember where we started
        while True:
            try:
                if self.current_model_index >= len(self.free_models):
                    self.current_model_index = 0  # Wrap around to the beginning
                
                # If we've tried all models, give up
                if self.current_model_index == initial_index and initial_index != 0:
                    return False
                
                model_name = self.free_models[self.current_model_index]
                self.model = genai.GenerativeModel(model_name)
                logger.info(f"Switched to free model: {model_name}")
                self.current_model_index += 1  # Move to next model for potential future fallbacks
                return True
            except Exception as e:
                logger.warning(f"Failed to initialize free model {self.free_models[self.current_model_index]}: {str(e)}")
                self.current_model_index += 1

    def generate_content(self, prompt):
        """Generate content with automatic retries and rate limiting"""
        if not self.model:
            if not self.initialize_model():
                raise Exception("Failed to initialize any model")

        for attempt in range(self.retry_count):
            try:
                response = self.model.generate_content(prompt)
                return response
            except Exception as e:
                error_str = str(e)
                if ("quota" in error_str.lower() or "404" in error_str) and self._try_next_free_model():
                    # Try again with the new model
                    try:
                        response = self.model.generate_content(prompt)
                        return response
                    except Exception as new_e:
                        logger.error(f"Error with fallback model: {str(new_e)}")
                if self._should_retry(e, attempt):
                    continue
                raise

    def _should_retry(self, error, attempt):
        """Determine if we should retry based on the error and attempt number"""
        if attempt >= self.retry_count - 1:
            return False

        error_str = str(error)
        
        # Check if it's a rate limit error
        if "429" in error_str or "quota" in error_str.lower():
            delay = self._calculate_delay(attempt, error_str)
            logger.warning(f"Rate limit hit. Waiting {delay} seconds before retry...")
            sleep(delay)
            return True
            
        # Other retriable errors
        if any(code in error_str for code in ["500", "502", "503", "504"]):
            delay = self._calculate_delay(attempt)
            logger.warning(f"Server error. Waiting {delay} seconds before retry...")
            sleep(delay)
            return True
            
        return False

    def _calculate_delay(self, attempt, error_str=None):
        """Calculate the delay time for retry with exponential backoff"""
        # Check if there's a retry delay in the error message
        if error_str:
            try:
                # Try to extract retry delay from error message
                if "retry_delay" in error_str:
                    error_dict = json.loads(error_str[error_str.find("{"):error_str.rfind("}")+1])
                    if "retry_delay" in error_dict:
                        return int(error_dict["retry_delay"]["seconds"])
            except:
                pass

        # Default exponential backoff
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        return delay

    def list_models(self):
        """List available models with retry logic"""
        for attempt in range(self.retry_count):
            try:
                return [m.name for m in genai.list_models()]
            except Exception as e:
                if self._should_retry(e, attempt):
                    continue
                raise
