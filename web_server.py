"""
BraveStarr Web Server
提供数据可视化界面
"""

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse, HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import sqlite3
import os
from datetime import datetime, date, timedelta
import json

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "bravestarr.db")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))


def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


async def homepage(request):
    """首页 - 仪表盘"""
    conn = get_db()
    
    # 获取最新日期
    row = conn.execute(
        "SELECT MAX(record_date) as latest_date FROM wechat_index"
    ).fetchone()
    latest_date = row["latest_date"] if row and row["latest_date"] else date.today().isoformat()
    
    # 获取最新排名
    ranking = conn.execute(
        """
        SELECT keyword, index_value, change_percent, trend, category
        FROM wechat_index
        WHERE record_date = ?
        ORDER BY index_value DESC
        """,
        (latest_date,)
    ).fetchall()
    
    # 获取分类统计
    category_stats = conn.execute(
        """
        SELECT category, AVG(index_value) as avg_value, COUNT(*) as count
        FROM wechat_index
        WHERE record_date = ?
        GROUP BY category
        ORDER BY avg_value DESC
        """,
        (latest_date,)
    ).fetchall()
    
    conn.close()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "latest_date": latest_date,
        "ranking": [dict(r) for r in ranking],
        "category_stats": [dict(c) for c in category_stats]
    })


async def api_trend(request):
    """API: 获取趋势数据"""
    keyword = request.query_params.get("keyword")
    days = int(request.query_params.get("days", 30))
    
    conn = get_db()
    
    if keyword:
        rows = conn.execute(
            """
            SELECT keyword, index_value, change_percent, trend, category, record_date
            FROM wechat_index
            WHERE keyword = ? AND record_date >= date('now', '-{} days')
            ORDER BY record_date ASC
            """.format(days),
            (keyword,)
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT keyword, index_value, change_percent, trend, category, record_date
            FROM wechat_index
            WHERE record_date >= date('now', '-{} days')
            ORDER BY record_date ASC, keyword
            """.format(days)
        ).fetchall()
    
    conn.close()
    
    return JSONResponse([dict(row) for row in rows])


async def api_ranking(request):
    """API: 获取排名"""
    record_date = request.query_params.get("date")
    category = request.query_params.get("category")
    
    conn = get_db()
    
    if record_date is None:
        row = conn.execute(
            "SELECT MAX(record_date) as latest FROM wechat_index"
        ).fetchone()
        record_date = row["latest"] if row and row["latest"] else date.today().isoformat()
    
    query = """
        SELECT keyword, index_value, change_percent, trend, category, record_date
        FROM wechat_index
        WHERE record_date = ?
    """
    params = [record_date]
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    query += " ORDER BY index_value DESC"
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    
    return JSONResponse({
        "record_date": record_date,
        "category_filter": category,
        "data": [dict(row) for row in rows]
    })


async def api_keywords(request):
    """API: 获取关键词列表"""
    conn = get_db()
    rows = conn.execute(
        "SELECT keyword, category, description FROM keywords WHERE is_active = 1 ORDER BY category, keyword"
    ).fetchall()
    conn.close()
    
    return JSONResponse([dict(row) for row in rows])


async def api_stats(request):
    """API: 获取统计信息"""
    conn = get_db()
    
    total_records = conn.execute(
        "SELECT COUNT(*) as count FROM wechat_index"
    ).fetchone()["count"]
    
    total_keywords = conn.execute(
        "SELECT COUNT(DISTINCT keyword) as count FROM wechat_index"
    ).fetchone()["count"]
    
    date_range = conn.execute(
        "SELECT MIN(record_date) as earliest, MAX(record_date) as latest FROM wechat_index"
    ).fetchone()
    
    conn.close()
    
    return JSONResponse({
        "total_records": total_records,
        "total_keywords": total_keywords,
        "date_range": dict(date_range) if date_range else {}
    })


async def trends_page(request):
    """趋势页面"""
    return templates.TemplateResponse("trends.html", {"request": request})


async def ranking_page(request):
    """排名页面"""
    return templates.TemplateResponse("ranking.html", {"request": request})


# 创建应用
routes = [
    Route("/", homepage),
    Route("/trends", trends_page),
    Route("/ranking", ranking_page),
    Route("/api/trend", api_trend),
    Route("/api/ranking", api_ranking),
    Route("/api/keywords", api_keywords),
    Route("/api/stats", api_stats),
]

app = Starlette(debug=True, routes=routes)

# 静态文件
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


if __name__ == "__main__":
    import uvicorn
    print("🚀 BraveStarr Web Server 启动于 http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
