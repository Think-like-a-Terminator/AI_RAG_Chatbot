🤖 **AI Chatbot Powered by OpenAI's RAG & Google Cloud Datastore**

This project contains a RAG-powered AI chatbot on Webex Teams, designed using OpenAI’s RAG tool functionality (assistants and vector stores), deployed on Google Cloud Compute Engine with a NoSQL Datastore backend for saving conversation states. This Webex chatbot offers dynamic, context-aware responses with the help of a cutting-edge LLM and cloud infrastructure.  This chatbot supports Microsoft's standard JSON Card format, HTML, or Markdown Text to send custom designed cards or messages to users. It uses the webex_bot library to simplify the bot's interactions and assumes you already stored your knowledge base documents/files in Open AI's vector store and have an Assistant ID.


🌟 **What Is Retrieval-Augmented Generation (RAG)?**

RAG combines the best of two worlds: retrieval-based and generation-based models. Chatbots either pull predefined answers from a document or database (retrieval-based) or generate responses dynamically (generation-based). RAG supercharges this by retrieving relevant information from external sources, then feeding it to a large language model (LLM) like GPT to generate intelligent, context-aware responses.

Information Retrieval: The chatbot pulls relevant documents, answers, or context from a knowledge base or database.

Response Generation: The LLM uses the retrieved information to generate accurate, contextually relevant responses, leading to highly dynamic and adaptable interactions.


**🔧 How Does It Work?**

This chatbot does more than provide generic responses. Here's how the integration of RAG, LLM, and Google Cloud Datastore delivers an advanced AI conversation experience:


**RAG Workflow:**

Query Processing: When the user sends a message, the system processes it, then retrieves relevant data from external or pre-defined resources, in this case OpenAI's vector store.

Knowledge Retrieval: Using RAG, the chatbot fetches the most appropriate knowledge pieces to ground the conversation.

Response Generation: The retrieved knowledge is then combined with the user query, and a relevant response is generated using ChatGPT.

Answer Delivery: The chatbot sends a contextually accurate, dynamic reply that feels more intelligent than traditional bots.


**Google Cloud Datastore for State Management:**

For a chatbot to provide seamless conversations, it needs to remember context across multiple interactions. This is where Google Cloud Datastore, a highly scalable NoSQL database, comes in. We use Datastore to:

Store Conversation States: The current state of a user’s conversation (context, past responses, user preferences) is stored, ensuring continuity in multi-turn conversations.

Retrieve User Data: When a user sends a new message, the chatbot retrieves their stored conversation state to maintain a coherent and personalized dialogue flow.

Scale Seamlessly: Datastore supports large-scale applications, so whether you’re handling hundreds or millions of users, conversation states are saved efficiently.


**Deployment on Google Cloud Compute Engine**

We leverage Google Cloud Compute Engine (GCE) to run our AI chatbot on a Linux Virtual Machine (VM) for powerful, scalable cloud infrastructure. Here’s why GCE makes it a perfect fit:

Cost-Effectiveness: Linux VMs on Google Cloud are optimized for performance and cost, allowing us to run the chatbot's messages and AI model efficiently.

Reliability: GCE provides robust availability and minimal downtime, ensuring the chatbot is available to users 24/7.


**🚀 Getting Started**

Clone the Repository:
git clone https://github.com/Think-like-a-Terminator/AI_RAG_Chatbot.git

Install Dependencies:
pip install -r requirements.txt

Set up a Datastore instance in your Google Cloud Project.

Spin up a Linux VM on Google Cloud Compute Engine (Can also run on your local windows machine if you have all the requirements installed).

In the file aibot.py, enter your OpenAI's Assistant ID and your google cloud datastore json key file.

Run the Chatbot:
python app.py


**🛠️ Key Features**

Intelligent Conversations: By combining retrieval and generation, the chatbot provides smarter, more personalized responses extracted from your knowledge base.

Webex Card Messages:  Create clean custom-designed Cards to send to users or have the chatbot auto respond with.

Stateful Dialogs: Using Google Cloud Datastore, the chatbot remembers user interactions across sessions, maintaining a natural conversation flow.

Scalable Cloud Deployment: Running on Google Cloud Compute Engine ensures the chatbot can handle large-scale usage without performance degradation.
