Concept
The core concept behind this POC is to leverage OCR (Optical Character Recognition) to extract text from PDF documents, store the extracted text data into a vector database, and make it queryable through a script. This allows users to interact with the stored data by asking questions, and the system will retrieve the most relevant responses from the vector database.

This approach provides a solution for working with unstructured data in documents, making it easier to extract insights and answers from large volumes of text without manually searching through the documents.

How It Works
OCR Extraction: The PDF files are processed through an OCR engine, extracting all visible text from the document.
Data Storage: The extracted text is then stored in a vector database, where each piece of text is converted into a vector representation for efficient searching.
Querying the Data: Once the data is stored in the vector database, users can query it by asking questions. The script will process the question, convert it into a vector, and retrieve the most relevant pieces of text from the database.
