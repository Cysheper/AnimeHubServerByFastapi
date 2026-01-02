#!/usr/bin/env fish
# 动漫Hub后端服务启动脚本
# 用法:
#   ./start.fish          前台运行（调试用）
#   ./start.fish -d       后台运行（守护进程模式）
#   ./start.fish stop     停止后台服务
#   ./start.fish status   查看服务状态
#   ./start.fish logs     查看日志

# 设置项目根目录
set -g PROJECT_DIR (dirname (status filename))
cd $PROJECT_DIR

set -g PID_FILE "$PROJECT_DIR/.server.pid"
set -g LOG_FILE "$PROJECT_DIR/server.log"

# 从 .env 文件加载环境变量
if test -f "$PROJECT_DIR/.env"
    for line in (grep -v '^#' "$PROJECT_DIR/.env" | grep -v '^\s*$')
        set -l key (echo $line | cut -d '=' -f 1)
        set -l value (echo $line | cut -d '=' -f 2-)
        set -gx $key $value
    end
end

function log_info
    set_color green
    echo -n "[INFO] "
    set_color normal
    echo $argv
end

function log_warn
    set_color yellow
    echo -n "[WARN] "
    set_color normal
    echo $argv
end

function log_error
    set_color red
    echo -n "[ERROR] "
    set_color normal
    echo $argv
end

function start_server
    set -l mode $argv[1]
    
    log_info "正在启动 动漫Hub 后端服务..."
    
    if test "$mode" = "daemon"
        # 后台运行模式 - 使用 env 传递环境变量
        set -l env_vars
        if test -f "$PROJECT_DIR/.env"
            for line in (grep -v '^#' "$PROJECT_DIR/.env" | grep -v '^\s*$')
                set -a env_vars $line
            end
        end
        
        # 构建环境变量前缀
        if test (count $env_vars) -gt 0
            env $env_vars nohup uv run uvicorn app.main:app --host 0.0.0.0 --port 3001 >$LOG_FILE 2>&1 &
        else
            nohup uv run uvicorn app.main:app --host 0.0.0.0 --port 3001 >$LOG_FILE 2>&1 &
        end
        
        set -l pid $last_pid
        echo $pid >$PID_FILE
        sleep 2
        
        if kill -0 $pid 2>/dev/null
            log_info "服务已在后台启动 (PID: $pid)"
            log_info "API文档地址: http://localhost:3001/docs"
            log_info "日志文件: $LOG_FILE"
            log_info "停止服务: ./start.fish stop"
        else
            log_error "服务启动失败，请查看日志: $LOG_FILE"
            cat $LOG_FILE | tail -10
            exit 1
        end
    else
        # 前台运行模式
        log_info "API文档地址: http://localhost:3001/docs"
        log_info "按 Ctrl+C 停止服务"
        echo ""
        uv run uvicorn app.main:app --host 0.0.0.0 --port 3001 --reload
    end
end

function stop_server
    if test -f $PID_FILE
        set -l pid (cat $PID_FILE)
        if kill -0 $pid 2>/dev/null
            log_info "正在停止服务 (PID: $pid)..."
            kill $pid
            rm -f $PID_FILE
            log_info "服务已停止"
        else
            log_warn "服务未运行"
            rm -f $PID_FILE
        end
    else
        log_warn "未找到 PID 文件，服务可能未运行"
    end
end

function show_status
    if test -f $PID_FILE
        set -l pid (cat $PID_FILE)
        if kill -0 $pid 2>/dev/null
            log_info "服务运行中 (PID: $pid)"
            log_info "API地址: http://localhost:3001"
        else
            log_warn "服务未运行 (PID 文件存在但进程已停止)"
            rm -f $PID_FILE
        end
    else
        log_warn "服务未运行"
    end
end

function show_logs
    if test -f $LOG_FILE
        tail -f $LOG_FILE
    else
        log_error "日志文件不存在"
    end
end

# 解析命令行参数
set -l cmd $argv[1]

switch "$cmd"
    case stop
        stop_server
        exit 0
    case status
        show_status
        exit 0
    case logs
        show_logs
        exit 0
    case -d --daemon
        set -g DAEMON_MODE true
    case ""
        set -g DAEMON_MODE false
    case "*"
        echo "用法: ./start.fish [选项]"
        echo ""
        echo "选项:"
        echo "  (无)        前台运行，可看实时日志"
        echo "  -d          后台运行（守护进程模式）"
        echo "  stop        停止后台服务"
        echo "  status      查看服务状态"
        echo "  logs        查看日志（实时）"
        exit 1
end

# 检查 uv 是否安装
if not command -v uv >/dev/null 2>&1
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
if test "$DAEMON_MODE" = true
    start_server daemon
else
    start_server
end