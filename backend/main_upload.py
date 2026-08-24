"""
Updated /upload endpoint to add to backend/main.py
Add these imports and endpoint to your existing main.py
"""

# ADD these imports at the top of main.py:
# from fastapi import File, UploadFile
# from backend.file_ingestion import ingest_file, index_uploaded_schema

UPLOAD_ENDPOINT = '''
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Accepts a CSV or Excel file, creates a SQLite table from it,
    and indexes the schema into Qdrant for querying.
    """
    try:
        allowed = [".csv", ".xlsx", ".xls"]
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"File type '{ext}' not supported. Use CSV or Excel."
            )

        file_bytes = await file.read()
        if len(file_bytes) > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(status_code=400, detail="File too large. Max 50MB.")

        from backend.file_ingestion import ingest_file, index_uploaded_schema
        metadata = ingest_file(file_bytes, file.filename)
        index_uploaded_schema(metadata)

        return {
            "status": "success",
            "table_name": metadata["table_name"],
            "filename": metadata["original_filename"],
            "rows": metadata["row_count"],
            "columns": metadata["columns"],
            "message": f"File uploaded successfully. You can now ask questions about your data.",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''

print(UPLOAD_ENDPOINT)
