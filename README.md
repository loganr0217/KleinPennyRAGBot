# KleinPenny RAG-Chatbot for Search

This repository contains the **KleinPenny RAG-Chatbot**, a RAG chatbot designed to assist users in rapidly finding properties from the KleinPenny rental agency in Athens, Ohio, that match their specific descriptions. The chatbot is built with Retrieval-Augmented Generation (RAG), used LangChain, OpenAI, and PineCone, and includes chat history capabilities to enhance the user experience. Note that the chat history is global and resets every time the Flask server restarts. Follow the steps below to set up, run, and test the application.

---

## Project Features

- **Property Search:** Helps users quickly locate rental properties by interacting with the chatbot.
- **Chat History:** Tracks conversation context to provide more relevant answers during a session. History is refreshed globally whenever the Flask server restarts.
- **Testing Support:** Includes tools to test chatbot functionality with DeepEval.

---

## Setup Instructions
1. **Create mySecrets.py File**
   - Create a file named mySecrets.py
   - Add the following code and replace with your own keys:
   ```bash
     class Secrets:
         OPENAI_API_KEY = "{Your OpenAI API Key}"
         PINECONE_API_KEY = "{Your Pinecone API Key}"
         LANGCHAIN_API_KEY = "{Your LangChain API Key}"
     ```
   - Save the file 
2. **Set Up Python Virtual Environment**
   - Create a virtual environment to manage dependencies:
     ```bash
     python3 -m venv venv
     ```
   - Activate the virtual environment:
     - On Linux/macOS:
       ```bash
       source venv/bin/activate
       ```
     - On Windows:
       ```bash
       .\venv\Scripts\activate
       ```

3. **Install Dependencies**
   - Install the required dependencies using the following command:
     ```bash
     pip install -r requirements.txt
     ```

4. **Initialize the Application**
   - Run the initialization script:
     ```bash
     python3 init.py
     ```
   - If successful, the script will print a success message.

4. **Start the Flask Server**
   - Run the following command to start the Flask server:
     ```bash
     python3 app.py
     ```
5. **Interact with the Chatbot**
   - Run the following command to start the gradio Chatbot UI
    ```bash
      python3 chatbotUI.py
     ```
     
6. **Use the Chatbot Endpoint Yourself**
   - Use the `/ask` endpoint to interact with the chatbot by asking a question
   - Use the `/askFull` endpoint to get a more complete response including the following: [answer, context, propertyTitles]
   - You can send questions using tools like cURL, Postman, or a Python script.

7. **Evaluate with DeepEval**
   - Optionally, test the chatbot’s performance using DeepEval by running the following command:
     ```bash
     python3 test.py
     ```
   - This will run automated tests and display evaluation results.

---

You're ready to use and test the KleinPenny RAG-Chatbot! If you encounter any issues, refer to the documentation or contact me for support.
