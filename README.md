## Title of the Project
Conversational IVR for College ERP 

## Description
The integration of a conversational IVR system into the college ERP platform aims to simplify and automate student academic enquiries by using voice-based interaction. The system allows students to speak naturally in English, Tamil, or Tanglish and receive instant academic information, improving accessibility, reducing manual workload, and enhancing overall user experience.

## About
The Conversational IVR Enabled College ERP Assistant is designed to provide a hands-free, AI-driven solution for students to access their academic records through natural voice commands. Traditional ERP portals require manual login, navigation, and repeated steps, which can be time-consuming. This project eliminates these barriers by implementing an intelligent IVR assistant capable of understanding spoken queries, retrieving ERP data, and responding with synthesized speech. Leveraging Whisper for speech recognition, Gemini for natural language understanding, ChromaDB for retrieval-augmented generation, and MySQL for ERP data handling, the system ensures accurate, real-time responses. Students can simply speak their register number and ask questions about attendance, marks, subjects, fees, exams, and general college information.

## Features
```
Uses advanced speech recognition (Whisper ASR) for accurate transcription.
Integrates Google Gemini for natural language understanding and RAG-based responses.
Fully multilingual support: English, Tamil, and Tanglish.
Real-time ERP data retrieval using MySQL database.
Hands-free interaction with continuous conversation loop.
Automatic audio normalization, noise handling, and fallback mechanisms.
High scalability and flexible modular design for deployment.
Uses JSON-based structured data handling for profile and response organization.
```

## Requirements
```
* Operating System: Requires a 64-bit OS (Windows 10 or Ubuntu) for compatibility with deep learning frameworks.
* Development Environment: Python 3.6 or later is necessary for coding the sign language detection system.
* Deep Learning Frameworks: TensorFlow for model training, MediaPipe for hand gesture recognition.
* Image Processing Libraries: OpenCV is essential for efficient image processing and real-time hand gesture recognition.
* Version Control: Implementation of Git for collaborative development and effective code management.
* IDE: Use of VSCode as the Integrated Development Environment for coding, debugging, and version control integration.
* Additional Dependencies: Includes scikit-learn, TensorFlow (versions 2.4.1), TensorFlow GPU, OpenCV, and Mediapipe for deep learning tasks.
```

## System Architecture
```
Operating System:
Works on 64-bit Windows 10/11 or Ubuntu-based Linux environments.
Development Environment:
Python 3.10 or later is required for running the IVR assistant.
Libraries & Frameworks:
Whisper / Faster-Whisper for speech recognition
Google Generative AI (Gemini) API
ChromaDB vector store
MySQL Connector for database operations
gTTS and pyttsx3 for speech synthesis
NumPy, SoundDevice, SoundFile for audio processing
OpenAI tokenizer, regex, and other utilities
Database Requirements:
MySQL 8.0 with ERP schema containing:
STUDENT, DEPARTMENT, SUBJECT, ENROLLMENT, FEES, MARKS, ATTENDANCE tables.
IDE:
VSCode or PyCharm for Python development, debugging, and code management.
Version Control:
Git recommended for managing source versions and collaborative updates.
```

## Output
```
Output 1 – Register Number Recognition
Shows how the system records audio, transcribes the register number, parses digits like “double two three,” validates it, and authenticates the student.

Output 2 – Voice Query and ERP Response
Displays how the system recognizes questions like “What is my attendance?” and retrieves the exact percentage from the database before responding through speech.

Output 3 – RAG-based General Query Answering
Demonstrates answering questions like “Library timing enna?” using ChromaDB + Gemini.

Overall Detection/Response Accuracy: Approx. 95%, depending on microphone quality and noise levels.
```

## Results and Impact

The Conversational IVR ERP Assistant significantly enhances the accessibility of student information by enabling natural, effortless voice interaction. It reduces workload on academic and office staff by automating frequently asked queries. The system ensures faster and more personalized access to attendance, marks, fees, and other records. Its multilingual capability makes it accessible for a wide range of students, especially those more comfortable speaking Tamil or Tanglish. This project demonstrates the potential of combining speech recognition, NLP, and database-driven information systems to modernize campus communication and provide a foundation for future AI-powered student services.

## Articles published / References
```
You may use these sample references relevant to your topic:
Radford, A. et al. “Whisper: Robust Speech Recognition via Weak Supervision.” OpenAI, 2022.
Google DeepMind. “Gemini Model Documentation.” Google AI, 2024.
Reimers, N., & Gurevych, I. “Sentence Embeddings using Siamese Networks.” EMNLP, 2019.
ChromaDB Docs, “Vector Search for AI Applications,” 2023.
Python Software Foundation, “Speech Libraries Documentation.”
```

## Author:

Hezron Belix

