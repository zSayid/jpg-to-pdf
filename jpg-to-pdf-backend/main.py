# from fastapi import FastAPI, UploadFile, File
# from fastapi.responses import StreamingResponse  # For file streaming response
# from fastapi.middleware.cors import CORSMiddleware
# from typing import List
# from PIL import Image
# import io

# app = FastAPI()

# # Allow CORS for all origins
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Set to your frontend domain in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.post("/upload")
# async def convert_images_to_pdf(files: List[UploadFile] = File(...)):
#     print(f"Received {len(files)} files")
#     images = []

#     for file in files:
#         contents = await file.read()  # Read the file content
#         image = Image.open(io.BytesIO(contents))  # Open image from byte data
#         if image.mode != "RGB":  # Convert image mode if not RGB
#             image = image.convert("RGB")
#         images.append(image)

#     # Create in-memory buffer to hold the PDF file
#     pdf_buffer = io.BytesIO()
    
#     # Save images as a single PDF into the buffer
#     images[0].save(pdf_buffer, save_all=True, append_images=images[1:], format="PDF")
    
#     pdf_buffer.seek(0)  # Go back to the beginning of the buffer to read it

#     return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=output.pdf"})

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse  # For file streaming response
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from PIL import Image
import io
import logging

# Initialize FastAPI application
app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the maximum file size (e.g., 10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@app.post("/upload")
async def convert_images_to_pdf(files: List[UploadFile] = File(...)):
    logging.info(f"Received {len(files)} files")
    
    images = []
    for file in files:
        if file.size > MAX_FILE_SIZE:
            return {"error": f"File {file.filename} exceeds the maximum allowed size."}
        try:
            contents = await file.read()  # Read the file content
            image = Image.open(io.BytesIO(contents))  # Open image from byte data
            if image.mode != "RGB":  # Convert image mode if not RGB
                image = image.convert("RGB")
            images.append(image)
        except Exception as e:
            return {"error": f"Unable to process file {file.filename}: {str(e)}"}

    # Create in-memory buffer to hold the PDF file
    pdf_buffer = io.BytesIO()
    
    try:
        # Save images as a single PDF into the buffer
        images[0].save(pdf_buffer, save_all=True, append_images=images[1:], format="PDF")
        pdf_buffer.seek(0)  # Go back to the beginning of the buffer to read it
    except MemoryError:
        return {"error": "Server ran out of memory while processing the images. Try uploading fewer images or smaller files."}

    # Return the PDF as a streaming response
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=converted_images.pdf"}
    )