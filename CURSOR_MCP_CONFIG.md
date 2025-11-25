# Cursor MCP 설정 가이드

## MCP 서버 연결 방법

이 OneSignal MCP 서버는 **stdio 모드**로 실행되므로, Cursor 설정 파일에 명령어를 추가해야 합니다.

## 설정 파일 위치

Cursor의 MCP 설정 파일은 다음 위치에 있습니다:
- **macOS**: `~/Library/Application Support/Cursor/User/globalStorage/mcp.json`
- 또는 Cursor 설정에서 직접 추가

## 설정 예시

Cursor의 MCP 설정 파일(`mcp.json`)에 다음을 추가하세요:

```json
{
  "mcpServers": {
    "onesignal": {
      "command": "/Users/sunwoo/project/onesignal-mcp/venv/bin/python",
      "args": [
        "/Users/sunwoo/project/onesignal-mcp/onesignal_server.py"
      ],
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

또는 상대 경로를 사용하려면:

```json
{
  "mcpServers": {
    "onesignal": {
      "command": "python",
      "args": [
        "/Users/sunwoo/project/onesignal-mcp/onesignal_server.py"
      ],
      "cwd": "/Users/sunwoo/project/onesignal-mcp",
      "env": {
        "LOG_LEVEL": "INFO",
        "VIRTUAL_ENV": "/Users/sunwoo/project/onesignal-mcp/venv"
      }
    }
  }
}
```

## .env 파일 설정

OneSignal API를 사용하려면 프로젝트 루트에 `.env` 파일을 생성하세요:

```env
ONESIGNAL_APP_ID=your_app_id
ONESIGNAL_API_KEY=your_api_key
ONESIGNAL_ORG_API_KEY=your_org_api_key  # 선택사항
LOG_LEVEL=INFO
```

## HTTP/SSE 모드로 실행 (선택사항)

HTTP 서버로 실행하려면 코드를 수정하거나 다음과 같이 실행:

```python
# onesignal_server.py 마지막 부분 수정
if __name__ == "__main__":
    mcp.run(transport="sse")  # 또는 "streamable-http"
```

그러면 `http://localhost:8000`에서 접근 가능합니다.

## 확인 방법

1. Cursor를 재시작하세요
2. Cursor에서 MCP 서버가 연결되었는지 확인
3. OneSignal 관련 도구들이 사용 가능한지 확인

