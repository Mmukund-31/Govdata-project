from ai_helper import query_with_reasoning

user_question = "What is the average modal price of rice in Karnataka?"
output = query_with_reasoning(user_question)

print("\n--- RESULT ---")
for key, value in output.items():
    print(f"{key}: {value}\n")
