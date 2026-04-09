-- BraveStarr 微信指数数据库 Schema

CREATE TABLE IF NOT EXISTS wechat_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword VARCHAR(50) NOT NULL,
    index_value BIGINT NOT NULL,
    change_percent DECIMAL(10, 4),
    trend CHAR(1) CHECK (trend IN ('↑', '↓', '→')),
    category VARCHAR(20) CHECK (category IN ('OpenClaw', 'Agent', 'Skill', 'MCP', 'AI编程', 'RAG', '其他')),
    record_date DATE NOT NULL,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_keyword ON wechat_index(keyword);
CREATE INDEX IF NOT EXISTS idx_record_date ON wechat_index(record_date);
CREATE INDEX IF NOT EXISTS idx_category ON wechat_index(category);
CREATE UNIQUE INDEX IF NOT EXISTS idx_keyword_date ON wechat_index(keyword, record_date);

-- 14个预设关键词
CREATE TABLE IF NOT EXISTS keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword VARCHAR(50) NOT NULL UNIQUE,
    category VARCHAR(20) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入预设关键词
INSERT OR IGNORE INTO keywords (keyword, category) VALUES
('OpenClaw', 'OpenClaw'),
('Claude Code', 'AI编程'),
('Cursor', 'AI编程'),
('Windsurf', 'AI编程'),
('MCP', 'MCP'),
('LangChain', 'RAG'),
('LangGraph', 'RAG'),
('RAG', 'RAG'),
('AI Agent', 'Agent'),
('AutoGPT', 'Agent'),
('Prompt Engineering', '其他'),
('向量数据库', 'RAG'),
('大模型', '其他'),
('AI编程工具', 'AI编程');
