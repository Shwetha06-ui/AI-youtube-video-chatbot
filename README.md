# 🎥 AI-Powered YouTube Video Chatbot

An end-to-end Generative AI application built with **Streamlit**, **LangChain**, **Google Gemini API**, and **FAISS**. The application allows users to input any YouTube video URL, extract its transcript, process it using a Retrieval-Augmented Generation (RAG) pipeline, view AI-generated summaries/key points, and ask interactive questions grounded strictly in the video transcript.

---

## 📌 Table of Contents

1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [System Architecture](#-system-architecture)
4. [Tech Stack](#-tech-stack)
5. [Project Folder Structure](#-project-folder-structure)
6. [Prerequisites & Installation](#-prerequisites--installation)
7. [API Key Configuration](#-api-key-configuration)
8. [How to Run Locally](#-how-to-run-locally)
9. [How the RAG Pipeline Works](#-how-the-rag-pipeline-works)
10. [GitHub Setup Instructions](#-github-setup-instructions)
11. [Streamlit Community Cloud Deployment](#-streamlit-community-cloud-deployment)
12. [Example Usage](#-example-usage)
13. [Limitations](#-limitations)
14. [Future Improvements](#-future-improvements)

---

## 🌟 Project Overview

Understanding long YouTube educational videos, lectures, or interviews can be time-consuming. The **AI-Powered YouTube Video Chatbot** solves this problem by allowing users to converse with any YouTube video in real time.

By combining transcript extraction with a modern RAG pipeline, users receive answers backed directly by transcript evidence without hallucination.

---

## ✨ Key Features

- 🔗 **YouTube URL Input & Validation**: Supports standard watch links, shortened `youtu.be` links, Shorts, and Embed URLs.
- 📜 **Automatic Transcript Extraction & Cleaning**: Uses `youtube-transcript-api` to pull English or auto-translated transcripts, stripping bracketed sound effects (`[Music]`, `[Applause]`) and extra whitespace.
- 📝 **AI Video Summary & Key Takeaways**: Generates a 2-3 paragraph overview and 5-7 bullet points using Google Gemini.
- 🧠 **RAG Vector Search**: Text chunking via LangChain `RecursiveCharacterTextSplitter` and embedding storage in `FAISS`.
- 💬 **Grounded Q&A Chatbot**: Answers user queries using Gemini LLM strictly from transcript context; politely declines if information isn't present in the video.
- 🔍 **Source Attribution**: Expandable source snippet viewer showing the exact transcript chunks used for each response.
- 🧹 **Chat Control**: Clear chat history button to start fresh conversations.

---

## 🏗️ System Architecture

```
+------------------+      +---------------------------+      +--------------------------+
|  User YouTube    | ---> | Extract Transcript        | ---> | Clean & Chunk Text       |
|  URL Input       |      | (youtube-transcript-api)  |      | (RecursiveTextSplitter)  |
+------------------+      +---------------------------+      +--------------------------+
                                                                          |
                                                                          v
+------------------+      +---------------------------+      +--------------------------+
|  User Asks       | ---> | FAISS Vector Store        | <--- | Gemini Embeddings        |
|  Question        |      | (Similarity Search k=4)   |      | (text-embedding-004)     |
+------------------+      +---------------------------+      +--------------------------+
          |                             |
          v                             v
+-----------------------------------------------------+
|  Prompt Construction (Context + Question + History) |
+-----------------------------------------------------+
                          |
                          v
+-----------------------------------------------------+
|  Google Gemini LLM (gemini-1.5-flash)               |
+-----------------------------------------------------+
                          |
                          v
+-----------------------------------------------------+
|  Grounded Answer + Expandable Source Context        |
+-----------------------------------------------------+
```

---

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **LLM**: [Google Gemini API](https://aistudio.google.com/) (`gemini-1.5-flash`)
- **Embeddings**: Google Gemini Embeddings (`models/text-embedding-004`)
- **Vector Store**: [FAISS](https://github.com/facebookresearch/faiss) (`faiss-cpu`)
- **Framework / Orchestration**: [LangChain](https://www.langchain.com/)
- **Transcript Extraction**: [YouTube Transcript API](https://pypi.org/project/youtube-transcript-api/)
- **Environment Management**: `python-dotenv`
- **Language**: Python 3.10+

---

## 📁 Project Folder Structure

```
youtube-video-chatbot/
│
├── app.py                  # Main Streamlit application frontend
├── requirements.txt        # Project Python dependencies
├── .env                    # Local environment file (API keys - excluded from Git)
├── .env.example            # Environment template file
├── .gitignore              # Files to ignore in Git repository
├── README.md               # Detailed project documentation
│
├── src/                    # Source code package
│   ├── __init__.py         # Package initializer
│   ├── transcript.py       # Transcript extraction & text cleaning
│   ├── embeddings.py       # Chunking & FAISS vector store creation
│   ├── rag.py              # LLM summary generation & RAG Q&A
│   └── utils.py            # URL validation, Video ID extraction, key loader
│
└── data/                   # Data directory placeholder
    └── .gitkeep
```

---

## ⚙️ Prerequisites & Installation

### Prerequisites
- Python 3.10 or higher installed.
- Git installed on your machine.
- A free Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/).

### Installation Steps

1. **Clone or navigate to the project repository**:
   ```bash
   cd D:\youtube-video-chatbot
   ```

2. **Create a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   ```

   Activate virtual environment:
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **Mac/Linux**:
     ```bash
     source venv/bin/activate
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🔑 API Key Configuration

1. Copy `.env.example` to create a `.env` file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and replace `your_gemini_api_key_here` with your actual Google Gemini API Key:
   ```env
   GOOGLE_API_KEY=AIzaSy...
   ```
3. Alternatively, you can enter the API Key directly into the Streamlit sidebar input field while running the app.

---

## 🚀 How to Run Locally

Run the following command in your terminal inside the project root directory:

```bash
streamlit run app.py
```

The application will open automatically in your browser at `http://localhost:8501`.

---

## 🧠 How the RAG Pipeline Works

1. **Extraction**: `src/transcript.py` extracts the full text transcript of the YouTube video using the video ID.
2. **Cleaning**: Noise tags (such as `[Music]` or `[Applause]`) and extra whitespace are stripped out.
3. **Chunking**: `RecursiveCharacterTextSplitter` divides the clean text into overlapping chunks (default chunk size: 1000 characters, overlap: 200 characters).
4. **Embedding Generation**: Text chunks are converted into numerical vector representations using Google Gemini `text-embedding-004`.
5. **FAISS Indexing**: Embeddings are indexed in an in-memory `FAISS` vector database.
6. **Similarity Retrieval**: When a user asks a question, the question is embedded and `FAISS` retrieves the top 4 most relevant transcript chunks.
7. **Grounded Generation**: `gemini-1.5-flash` receives a prompt containing the retrieved context chunks and the user's question with strict instructions to answer *only* based on the context.

---

## 🐙 GitHub Setup Instructions

To push this project to your GitHub repository `https://github.com/Shwetha06-ui/youtube-video-chatbot.git`:

1. Initialize Git in the project directory:
   ```bash
   cd D:\youtube-video-chatbot
   git init
   ```

2. Add all files to tracking:
   ```bash
   git add .
   ```

3. Commit the changes:
   ```bash
   git commit -m "Initial commit: Complete AI-Powered YouTube Video Chatbot"
   ```

4. Set main branch and remote URL:
   ```bash
   git branch -M main
   git remote add origin https://github.com/Shwetha06-ui/youtube-video-chatbot.git
   ```

5. Push to GitHub:
   ```bash
   git push -u origin main
   ```

---

## ☁️ Streamlit Community Cloud Deployment

To deploy your application for free on Streamlit Community Cloud:

1. Push your repository to GitHub (following the steps above).
2. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
3. Click **New App**.
4. Select your repository: `Shwetha06-ui/youtube-video-chatbot`.
5. Set Main file path: `app.py`.
6. Expand **Advanced Settings** -> **Secrets** and add your Gemini API Key:
   ```toml
   GOOGLE_API_KEY = "your_actual_gemini_api_key_here"
   ```
7. Click **Deploy!**

---

## 💡 Example Usage

1. Paste a YouTube URL: e.g. `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
2. Click **Process Video**.
3. View the **AI Summary** and **Key Takeaways**.
4. Ask a question: *"What is the main topic discussed in this video?"*
5. Receive an accurate answer along with clickable transcript context snippets.

---

## ⚠️ Limitations

- **Transcripts Disabled**: Videos without public subtitles or transcripts cannot be processed.
- **Language**: Best optimized for English transcripts.
- **Extremely Long Videos**: Transcripts longer than several hours may hit embedding rate limits.

---

## 🔮 Future Improvements

- Add support for multilingual video translation.
- Export chat history to PDF/Markdown.
- Add support for custom vector store persistence on disk.
- Integrate timestamps into context snippets so clicking a snippet jumps directly to that timestamp in the video.

---

## 📄 License

MIT License - feel free to use and adapt this project for learning and interview demonstrations!
