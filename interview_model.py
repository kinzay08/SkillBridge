from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

model_id = "google/flan-t5-small"

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSeq2SeqLM.from_pretrained(model_id)

# Pipeline for text2text generation
pipe = pipeline("text2text-generation", model=model, tokenizer=tokenizer)

def generate_answer(question):
    prompt = f"Answer this job interview question professionally:\n{question}"
    result = pipe(prompt, max_new_tokens=100)[0]['generated_text']
    return result
