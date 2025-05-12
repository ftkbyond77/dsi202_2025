from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os
import logging

logger = logging.getLogger(__name__)

# Global variables to store model and tokenizer
model = None
tokenizer = None

def load_model():
    global model, tokenizer
    
    if model is None or tokenizer is None:
        logger.info("Loading chatbot model and tokenizer...")
        try:
            cache_dir = os.environ.get('TRANSFORMERS_CACHE', '/usr/src/app/treevaq/model_cache')
            logger.info(f"Using cache directory: {cache_dir}")  # Add this line
            os.makedirs(cache_dir, exist_ok=True)
            
            logger.info("Downloading tokenizer...")  # Add this
            tokenizer = AutoTokenizer.from_pretrained("gpt2", cache_dir=cache_dir)
            logger.info("Tokenizer downloaded successfully")  # Add this
            
            logger.info("Downloading model...")  # Add this
            model = AutoModelForCausalLM.from_pretrained("gpt2", cache_dir=cache_dir)
            logger.info("Model downloaded successfully")  # Add this
            
            device = torch.device("cpu")
            model.to(device)
            logger.info(f"Model loaded successfully on {device}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    return model, tokenizer

def generate_response(prompt, max_length=100, temperature=0.7):
    """
    Generate text based on the provided prompt
    
    Args:
        prompt (str): Input text to generate response for
        max_length (int): Maximum length of generated text
        temperature (float): Sampling temperature (higher = more random)
        
    Returns:
        str: Generated text response
    """
    try:
        # Ensure model is loaded
        model, tokenizer = load_model()
        
        # Get device model is on
        device = next(model.parameters()).device
        
        # Encode the prompt
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        
        # Generate text
        with torch.no_grad():
            outputs = model.generate(
                inputs["input_ids"],
                max_length=max_length,
                temperature=temperature,
                do_sample=True,
                top_p=0.92,
                top_k=50,
                repetition_penalty=1.1,
                num_return_sequences=1
            )
        
        # Decode the generated text
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Format the response to be chat-friendly
        # Strip the original prompt if it appears in the beginning
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt):].lstrip()
            
        return generated_text
    
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return "Sorry, I'm having trouble generating a response right now."