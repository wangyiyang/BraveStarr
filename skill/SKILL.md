# BraveStarr MCP Skill

微信指数数据收集与管理 Skill，通过 BraveStarr MCP Server 操作。

## 用途

- 录入每日微信指数数据
- 查询关键词趋势
- 批量管理指数记录

## 前提条件

1. BraveStarr MCP Server 必须运行
2. Docker 容器启动：`docker run -d -p 8000:8000 brave-starr:latest`
3. 数据库路径：`~/Documents/Github/BraveStarr/bravestarr.db`

## 数据库结构

**表名**: `wechat_index`

| 字段 | 类型 | 说明 |
|------|------|------|
| keyword | TEXT | 关键词 |
| index_value | INTEGER | 指数值 |
| change_percent | REAL | 环比变化百分比 |
| trend | TEXT | 趋势 (↑ ↓ →) |
| category | TEXT | 分类 (OpenClaw/Agent/Skill/MCP/AI编程/RAG/其他) |
| record_date | TEXT | 记录日期 (YYYY-MM-DD) |
| note | TEXT | 备注 |

**约束**: (keyword, record_date) 唯一，冲突时自动更新

## 使用方法

### 直接操作数据库

```bash
# 查询今日数据
cd ~/Documents/Github/BraveStarr
sqlite3 bravestarr.db "SELECT * FROM wechat_index WHERE record_date = '2026-04-09'"

# 插入数据
sqlite3 bravestarr.db "INSERT OR REPLACE INTO wechat_index (keyword, index_value, change_percent, trend, category, record_date) VALUES (...)"
```

### 通过 MCP 调用

```bash
# 使用 mcporter 调用
mcporter call bravestarr brave_starr_add_records \
  --entries '[{"keyword": "龙虾", "index_value": 61742159, "change_percent": 22.34, "trend": "↑", "category": "其他", "record_date": "2026-04-09"}]'
```

## 分类选项

- OpenClaw
- Agent
- Skill
- MCP
- AI编程
- RAG
- 其他

## 常见任务

### 录入单日数据

```bash
# 批量插入（示例）
sqlite3 bravestarr.db << 'EOF'
INSERT INTO wechat_index (keyword, index_value, change_percent, trend, category, record_date) VALUES
('龙虾', 61742159, 22.34, '↑', '其他', '2026-04-09'),
('OpenClaw', 11721932, -0.05, '↓', 'OpenClaw', '2026-04-09')
ON CONFLICT(keyword, record_date) DO UPDATE SET
    index_value = excluded.index_value,
    change_percent = excluded.change_percent,
    trend = excluded.trend,
    updated_at = CURRENT_TIMESTAMP;
EOF
```

### 查询趋势

```sql
-- 某词30天趋势
SELECT record_date, index_value, trend 
FROM wechat_index 
WHERE keyword = '龙虾' 
ORDER BY record_date DESC 
LIMIT 30;

-- 今日全部数据
SELECT keyword, index_value, change_percent, trend 
FROM wechat_index 
WHERE record_date = date('now')
ORDER BY index_value DESC;
```

## 注意事项

- category 字段有 CHECK 约束，必须是预定义值之一
- 重复录入会自动更新（UPSERT 行为）
- 日期格式严格使用 YYYY-MM-DD
