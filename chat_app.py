import sys
from ai_helper import query_with_reasoning


def start_chat():
    print("🤖 Welcome to Project Samarth — AI Policy Assistant")
    print("Ask me anything about Indian agriculture & climate data.")
    print("Type 'exit' or 'quit' to end.\n")

    while True:
        user_question = input("🧑‍💻 You: ").strip()

        if user_question.lower() in ["exit", "quit"]:
            print("\n👋 Exiting chat. See you again!")
            sys.exit(0)

        print("\n🔍 Analyzing your question...")
        try:
            response = query_with_reasoning(user_question)

            if "error" in response:
                print(f"❌ Error: {response['error']}\n")
                continue

            print("\n--- 💬 AI ANSWER ---")
            print(response["summary"])
            print("\n--- 🧠 Gemini Reasoning ---")
            print(response["gemini_reasoning"])
            print("\n--- 🧾 SQL Query Used ---")
            print(response["sql_query"])
            print("\n--- 🧩 Result Preview ---")
            print(response["result_preview"])
            print("\n")

        except Exception as e:
            print(f"⚠️ Something went wrong: {str(e)}\n")


if __name__ == "__main__":
    start_chat()
