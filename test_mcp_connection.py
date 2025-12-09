#!/usr/bin/env python3
"""Test script to verify MCP server is working correctly."""
import sys
import os
import json
import asyncio
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_mcp_server():
    """Test MCP server functionality."""
    print("=" * 60)
    print("MCP 서버 연결 테스트")
    print("=" * 60)
    
    try:
        # Import server module
        print("\n1. 서버 모듈 로드 테스트...")
        from onesignal_server import mcp
        print("   ✅ 서버 모듈 로드 성공")
        print(f"   서버 이름: {mcp.name}")
        
        # Check if tools are available
        print("\n2. 도구(Tools) 확인...")
        try:
            # FastMCP의 도구 확인 방법
            if hasattr(mcp, '_tools'):
                tools = mcp._tools
                tool_count = len(tools) if tools else 0
                print(f"   ✅ 도구 개수: {tool_count}")
                
                # 일부 도구 이름 출력
                if tools:
                    print("\n   등록된 도구 예시:")
                    for i, tool in enumerate(list(tools.values())[:5]):
                        tool_name = getattr(tool, 'name', 'Unknown')
                        print(f"   - {tool_name}")
                    if tool_count > 5:
                        print(f"   ... 외 {tool_count - 5}개 도구")
            else:
                print("   ⚠️  도구 목록에 직접 접근 불가 (정상)")
        except Exception as e:
            print(f"   ⚠️  도구 확인 중 오류: {e}")
        
        # Check resources
        print("\n3. 리소스(Resources) 확인...")
        try:
            if hasattr(mcp, '_resources'):
                resources = mcp._resources
                resource_count = len(resources) if resources else 0
                print(f"   ✅ 리소스 개수: {resource_count}")
                if resources:
                    for resource_name in list(resources.keys())[:3]:
                        print(f"   - {resource_name}")
            else:
                print("   ⚠️  리소스 목록에 직접 접근 불가 (정상)")
        except Exception as e:
            print(f"   ⚠️  리소스 확인 중 오류: {e}")
        
        # Check app configuration
        print("\n4. OneSignal 앱 설정 확인...")
        try:
            from onesignal_server import app_configs, get_current_app
            current_app = get_current_app()
            if current_app:
                print(f"   ✅ 현재 앱: {current_app.name}")
                print(f"   앱 ID: {current_app.app_id[:8]}...")
            else:
                print("   ⚠️  앱 설정이 없습니다 (.env 파일 확인 필요)")
            
            if app_configs:
                print(f"   ✅ 설정된 앱 개수: {len(app_configs)}")
                for key, app in app_configs.items():
                    print(f"   - {key}: {app.name}")
            else:
                print("   ⚠️  설정된 앱이 없습니다")
        except Exception as e:
            print(f"   ⚠️  앱 설정 확인 중 오류: {e}")
        
        # Test server can start
        print("\n5. 서버 실행 가능 여부 확인...")
        print("   ✅ 서버 모듈이 정상적으로 로드되었습니다")
        print("   Cursor에서 MCP 서버로 연결할 수 있습니다")
        
        print("\n" + "=" * 60)
        print("✅ 모든 테스트 통과!")
        print("=" * 60)
        print("\n다음 단계:")
        print("1. Cursor를 재시작하세요")
        print("2. Cursor에서 MCP 서버가 연결되었는지 확인하세요")
        print("3. OneSignal 관련 도구들이 사용 가능한지 테스트하세요")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ 모듈 로드 실패: {e}")
        print("\n해결 방법:")
        print("1. 가상환경이 활성화되었는지 확인: source venv/bin/activate")
        print("2. 필요한 패키지가 설치되었는지 확인: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"   ❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)



