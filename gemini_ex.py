from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key="AIzaSyA9LiIaH7BChIpv43rAfIJN-e_yyhy2ZeU")

response = client.models.generate_content(
    model="gemini-2.5-pro", contents="Explain how AI works in a few words"
)
print(response.text)