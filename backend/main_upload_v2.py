"""
Updated /upload endpoint for large dataset support.
Replace the /upload endpoint in backend/main.py with this version.
Also add /tables endpoint for listing uploaded datasets.
"""

# ─── Add these to your imports at top of main.py ──────────────────────────────
# from fastapi import File, UploadFile
# (already there from previous update)

UPLOAD_V2 = '''
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Accepts CSV or Excel files up to 500MB.
    Uses chunked processing for large files.
    """
    try:
        import os as _os
        allowed = [".csv", ".xlsx", ".xls"]
        ext = _os.path.splitext(file.filename)[1].lower()
        if ext not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Use CSV or Excel."
            )

        file_bytes = await file.read()
        size_mb = len(file_bytes) / (1024 * 1024)

        if size_mb > 500:
            raise HTTPException(status_code=400, detail=f"File too large ({size_mb:.0f}MB). Max 500MB.")

        from backend.file_ingestion import ingest_file, index_uploaded_schema
        metadata = ingest_file(file_bytes, file.filename)
        index_uploaded_schema(metadata)

        return {
            "status": "success",
            "table_name": metadata["table_name"],
            "filename": metadata["original_filename"],
            "rows": metadata["row_count"],
            "columns": metadata["columns"],
            "size_mb": metadata["size_mb"],
            "message": f"Successfully processed {metadata['row_count']:,} rows. You can now ask questions about your data.",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tables")
def list_tables():
    """Lists all uploaded datasets currently available."""
    from backend.file_ingestion import list_uploaded_tables
    return {"tables": list_uploaded_tables()}
'''

print(UPLOAD_V2)
