set -e

REQUIRED_ENV_NAME="mcp"
PID_FILE="pid/server.pid"

source ~/anaconda3/etc/profile.d/conda.sh

start_server(){
  conda activate $REQUIRED_ENV_NAME
  echo "✅ 가상환경 활성화: '$REQUIRED_ENV_NAME'"

  echo "Starting MCP demo with nohup (no log)..."

  # 서버 실행 (백그라운드 실행 )
  nohup streamlit run src/app.py > /dev/null 2>&1&

  echo $! > "$PID_FILE"

  echo "✅ app.py running... (PID: $(cat $PID_FILE))"
}

stop_server() {
  if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
      echo "Stopping app.py PID $PID..."
      kill "$PID"
    else
      echo "⚠️ PID $PID is not running."
    fi
    rm -f "$PID_FILE"
    echo "✅ app.py stopped."
  else
    echo "⚠️ No PID file found. app.py may not be running."
  fi
}

case "$1" in
  start)
    start_server
    ;;
  stop)
    stop_server
    ;;
  *)
    echo "Usage: $0 {start|stop}"
    exit 1
    ;;
  esac