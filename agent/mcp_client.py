import subprocess
import json
import os
import threading


class MCPClient:
    def __init__(self, server_script: str):
        self.server_script = server_script
        self.proc = None
        self.lock = threading.Lock()
        self._start()

    def _start(self):
        env = os.environ.copy()
        self.proc = subprocess.Popen(
            ["python3", self.server_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=env
        )
        self._initialize()

    def _send_and_receive(self, message: dict) -> dict:
        line = json.dumps(message) + "\n"
        self.proc.stdin.write(line.encode())
        self.proc.stdin.flush()
        response = self.proc.stdout.readline()
        return json.loads(response)

    def _send_notification(self, message: dict):
        line = json.dumps(message) + "\n"
        self.proc.stdin.write(line.encode())
        self.proc.stdin.flush()

    def _initialize(self):
        self._send_and_receive({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "promptci", "version": "1.0"}
            }
        })
        self._send_notification({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        })

    def call_tool(self, name: str, arguments: dict) -> str:
        with self.lock:
            response = self._send_and_receive({
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": name,
                    "arguments": arguments
                }
            })
        result = response.get("result", {})
        content = result.get("content", [])
        if content:
            return content[0].get("text", "")
        return ""

    def close(self):
        if self.proc:
            self.proc.terminate()


mcp = MCPClient(
    server_script=os.path.join(
        os.path.dirname(__file__),
        "..", "mcp_server", "github_tools.py"
    )
)