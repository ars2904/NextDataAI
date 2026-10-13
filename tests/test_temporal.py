"""Test script for temporal context, dynamic date, knowledge cutoff, and real-time capabilities."""
import httpx

client = httpx.Client(base_url="http://127.0.0.1:8000")

questions = [
    "What is today's date?",
    "What year is it?",
    "What is your knowledge cutoff?",
    "Can you access real-time information?"
]

print("=" * 60)
print("TESTING GENERAL QUESTIONS MODE")
print("=" * 60)

for q in questions:
    res = client.post("/api/chat", json={"message": q, "mode": "general"})
    data = res.json()
    print(f"QUERY: {q}")
    print(f"REPLY: {data.get('reply')}")
    print("-" * 60)

print("\n" + "=" * 60)
print("TESTING COMPANY QUESTIONS MODE")
print("=" * 60)

for q in ["What is today's date?", "What is your knowledge cutoff?", "What are your data privacy and security policies?"]:
    res = client.post("/api/chat", json={"message": q, "mode": "company"})
    data = res.json()
    print(f"QUERY: {q}")
    print(f"REPLY: {data.get('reply')}")
    print(f"SOURCES: {[s['document'] for s in data.get('sources', [])]}")
    print("-" * 60)
