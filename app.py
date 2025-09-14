import os #importing the os module
print(os.environ.get("MONGODB_URI"))

import uuid #to later use to generate random unique identifier
from datetime import datetime, timezone #for date and time to be logged into the database
from dotenv import load_dotenv #to read the variables from the .env file
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ServerSelectionTimeoutError

#from ollama library 
from langchain_ollama import ChatOllama 

from langchain.schema import HumanMessage, AIMessage

#loading the environment variables which are kept separately in a different .env folder which the client cannot access
load_dotenv()


MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB", "chatbot_db")
COLL_NAME = os.getenv("MONGODB_COLLECTION", "chat_history")

if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI not available in .env file")

#connecting to mongodb atlas 
client = MongoClient(MONGODB_URI)

try:
    client.admin.command("ping")  # Quick test to confirm connection
    print("✅ Connected to MongoDB Atlas successfully!")
except ServerSelectionTimeoutError as e:
    raise SystemExit(f"❌ Cannot connect to MongoDB Atlas: {e}")

db = client[DB_NAME]
collection = db[COLL_NAME]


# Create useful indexes (one-time)
collection.create_index([("session_id", ASCENDING), ("timestamp", ASCENDING)])

#choose the model you want to use
chat = ChatOllama(model="gemma2:2b")

# -------------------------------
# 4. Start chat session (Reuse same session)
# -------------------------------
session_file = "session.txt"

if os.path.exists(session_file):
    with open(session_file, "r") as f:
        session_id = f.read().strip()
    print("\n-- Welcome back! Resuming previous session.")
else:
    session_id = str(uuid.uuid4())
    with open(session_file, "w") as f:
        f.write(session_id)
    print("\n-- Welcome! Starting a new session.")

print(f"-- Session ID: {session_id}")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("👋 Goodbye!")
        break

    now = datetime.now(timezone.utc)

    #saving the user message in the database
    collection.insert_one({
        "session_id": session_id,
        "role": "user",
        "content": user_input,
        "model": None,
        "timestamp": now,
    })

    #trying to build the memory 
    recent_messages = list(
        collection.find({"session_id": session_id})
        .sort("timestamp", 1)   # oldest to newest
        .limit(100)              # to fetch the last 100 conversations
    )

   #building the conversation history with the model
    conversation = []
    for msg in recent_messages:
        if msg["role"] == "user":
            conversation.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "bot":
            # Keep bot messages in context as well
            conversation.append(AIMessage(content=msg["content"]))

    #to respond the chat given by the user, the llm responds
    response = chat.invoke(conversation)
    bot_text = response.content

    #saving the bot response in mongo db
    collection.insert_one({
        "session_id": session_id,
        "role": "bot",
        "content": bot_text,
        "model": "gemma2:2b",
        "timestamp": datetime.now(timezone.utc),
    })

   #to display the bot response
    print("Bot:", bot_text)


