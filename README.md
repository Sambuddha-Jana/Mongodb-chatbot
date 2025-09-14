# Mongodb-chatbot
A basic project to understand the implementation of a NO-SQL database while running LLM locally

1) We first make a account in ollama.com
2) From the library choose which model you want to learn locally in your system
3) We start the ollama server, ollama serve
4) we pull the model(download it ), ollama pull xyx
5) in ollama list, you can see your downloaded model
6) Using pymongo create the whole logic with the llm model, how the responses should be, what you are expecting etc
7) IMP-> create a .env file to keep the connection string, database name and collection name private
8) Save the responses of the chat in the database
9) Later use the chats for creating a memory with your chatbot for future conversations
