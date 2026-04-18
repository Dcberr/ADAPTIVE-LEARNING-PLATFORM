#!/usr/bin/env python
"""
Script to run the LeetCode API server
Run: python -m scripts.run_api
or: uvicorn app.api:app --reload
"""

import uvicorn
import sys

if __name__ == "__main__":
    # Chạy FastAPI server
    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=8002,
        reload=True,  # Auto reload khi có thay đổi code
        log_level="info"
    )
