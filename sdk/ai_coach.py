from transformers import pipeline

class AICoach:
    def __init__(self, model_name="gpt2"):
        """Initialize the AI Coach with a Hugging Face model."""
        print("Loading the language model...")
        self.generator = pipeline("text-generation", model=model_name)

    def generate_tip(self, habit_name: str) -> str:
        """Generate a motivational tip for a specific habit."""
        # Define a context for the model
        prompt = f"Provide a motivational tip for improving the habit: {habit_name}. Be positive and actionable."

        # Generate text using the model
        result = self.generator(prompt, max_length=50, num_return_sequences=1)
        return result[0]["generated_text"].strip()
