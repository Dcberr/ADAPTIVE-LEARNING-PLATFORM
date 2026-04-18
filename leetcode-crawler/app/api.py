
from fastapi import FastAPI, HTTPException, Query, Path
from typing import Optional

from uvicorn import logging
from app.db.connection import get_connection
from app.db import repository
from app.dto.problem_dto import ProblemDTO, ProblemListResponseDTO
from app.pipeline.pipeline import run_pipeline

app = FastAPI(
    title="LeetCode API",
    description="API để lấy dữ liệu LeetCode problems từ database",
    version="1.0.0"
)

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.post("/api/crawler/run")
def run_crawler_endpoint(
    limit: int = Query(5, ge=1, le=500, description="Số lượng problems cần crawl (1-500)")
):
    """
    Chạy crawler để lấy dữ liệu LeetCode problems
    
    - **limit**: Số lượng problems cần crawl (mặc định: 5, tối đa: 500)
    
    Endpoint này sẽ chạy crawler và lưu các problems vào database.
    Những problems đã tồn tại sẽ được bỏ qua.
    """
    try:
        run_pipeline(limit=limit)
        return {
            "status": "success",
            "message": f"Crawler is done. Has crawled {limit} problems."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi chạy crawler: {str(e)}")


@app.get("/api/problems", response_model=ProblemListResponseDTO)
def get_problems(
    page: int = Query(1, ge=1, description="Trang (bắt đầu từ 1)"),
    limit: int = Query(10, ge=1, le=100, description="Số lượng items per page")
):
    """
    Lấy danh sách tất cả LeetCode problems
    
    - **page**: Số trang (mặc định: 1)
    - **limit**: Số items trên 1 trang (mặc định: 10, tối đa: 100)
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        problems, total = repository.get_all_problems(cur, page, limit)
        
        cur.close()
        conn.close()
        
        return ProblemListResponseDTO(
            total=total,
            page=page,
            limit=limit,
            data=[ProblemDTO(**p) for p in problems]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/problems/difficulty/{difficulty}", response_model=ProblemListResponseDTO)
def get_problems_by_difficulty(
    difficulty: str = Path(..., description="Độ khó: Easy, Medium, Hard"),
    page: int = Query(1, ge=1, description="Trang (bắt đầu từ 1)"),
    limit: int = Query(10, ge=1, le=100, description="Số lượng items per page")
):
    """
    Lấy LeetCode problems theo độ khó
    
    - **difficulty**: Easy, Medium, hoặc Hard
    """
    try:
        # Validate difficulty
        valid_difficulties = ["Easy", "Medium", "Hard"]
        if difficulty not in valid_difficulties:
            raise HTTPException(
                status_code=400,
                detail=f"Difficulty phải là một trong: {', '.join(valid_difficulties)}"
            )
        
        conn = get_connection()
        cur = conn.cursor()
        
        problems, total = repository.get_problems_by_difficulty(cur, difficulty, page, limit)
        
        cur.close()
        conn.close()
        
        return ProblemListResponseDTO(
            total=total,
            page=page,
            limit=limit,
            data=[ProblemDTO(**p) for p in problems]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/problems/id/{question_id}", response_model=ProblemDTO)
def get_problem_by_id(question_id: int):
    """
    Lấy chi tiết một problem theo question ID
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        problem = repository.get_problem_by_id(cur, question_id)
        
        cur.close()
        conn.close()
        
        if not problem:
            raise HTTPException(status_code=404, detail="Problem không tìm thấy")
        
        return ProblemDTO(**problem)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/problems/slug/{title_slug}", response_model=ProblemDTO)
def get_problem_by_slug(title_slug: str):
    """
    Lấy chi tiết một problem theo title slug
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        problem = repository.get_problem_by_title_slug(cur, title_slug)
        
        cur.close()
        conn.close()
        
        if not problem:
            raise HTTPException(status_code=404, detail="Problem không tìm thấy")
        
        return ProblemDTO(**problem)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
