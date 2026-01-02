#!/usr/bin/env fish
# 动漫Hub后端服务启动脚本

# 设置项目根目录
set -l PROJECT_DIR (dirname (status filename))
cd $PROJECT_DIR

# OSS 配置 (阿里云对象存储)
# 请替换为你的实际密钥，或者在环境中预先设置这些变量
if not set -q OSS_ACCESS_KEY_ID
    set -gx OSS_ACCESS_KEY_ID "LTAI5t9LSTbuB7VrbbGTfQ3t"
end
if not set -q OSS_ACCESS_KEY_SECRET
    set -gx OSS_ACCESS_KEY_SECRET "6bS34yo6okGb4LjOhZpCBf905g4Olt"
end

# 颜色输出
set -l GREEN '\033[0;32m'
set -l YELLOW '\033[1;33m'
set -l RED '\033[0;31m'
set -l NC '\033[0m'

function log_info
    echo -e "$GREEN[INFO]$NC $argv"
end

function log_warn
    echo -e "$YELLOW[WARN]$NC $argv"
end

function log_error
    echo -e "$RED[ERROR]$NC $argv"
end

# 检查 uv 是否安装
if not command -v uv &> /dev/null
    log_error "uv 未安装，请先安装 uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
end

# 同步依赖
log_info "正在同步项目依赖..."
uv sync
if test $status -ne 0
    log_error "依赖同步失败"
    exit 1
end

# 检查数据库是否存在，如果不存在则初始化
if not test -f "$PROJECT_DIR/anime_hub.db"
    log_warn "数据库不存在，正在初始化..."
    uv run python -m scripts.init_db
    if test $status -ne 0
        log_error "数据库初始化失败"
        exit 1
    end
    log_info "数据库初始化完成"
end

# 启动服务器
log_info "正在启动 动漫Hub 后端服务..."
log_info "API文档地址: http://localhost:8080/docs"
log_info "按 Ctrl+C 停止服务"
echo ""

uv run uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
