from transformers import pipeline

generator = pipeline("text2text-generation", model="google/flan-t5-base")

prompt = "Rewrite this as a personal memoir passage: The day I got my first job, I felt like I was finally independent."
result = generator(prompt, max_length=200, do_sample=False)

print(result[0]['generated_text'])