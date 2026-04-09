# from infra.groq_sdk.connection import GroqConnection
# from dotenv import load_dotenv
# import os

# load_dotenv()

# def main() -> None:
#     client = GroqConnection(api_key=os.getenv("GROK_API_KEY")).get_client()

#     response = client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         messages=[
#             {
#                 "role": "user",
#                 "content": "Explique a importancia de modelos de linguagem rapidos.",
#             }
#         ],
#     )

#     print(response.choices[0].message.content)


# if __name__ == "__main__":
#     main()
