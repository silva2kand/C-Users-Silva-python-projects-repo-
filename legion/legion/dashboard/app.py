"""
Legion Dashboard - Real-time monitoring interface for the AI Agent Swarm
"""
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, Response, jsonify
from flask_socketio import SocketIO, emit
import threading
import queue

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables for real-time updates
journal_queue = queue.Queue()
active_agents = {}
system_status = {
    "status": "initializing",
    "active_agents": 0,
    "total_tasks": 0,
    "last_activity": None
}


class DashboardMonitor:
    """Monitors Legion activity and broadcasts updates"""

    def __init__(self, legion_core):
        self.legion_core = legion_core
        self.monitoring = False

    def start_monitoring(self):
        """Start monitoring Legion activity"""
        self.monitoring = True
        thread = threading.Thread(target=self._monitor_loop)
        thread.daemon = True
        thread.start()

    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Check for new journal entries
                self._check_journal_updates()

                # Update system status
                self._update_system_status()

                time.sleep(1)  # Check every second

            except Exception as e:
                print(f"Dashboard monitoring error: {e}")
                time.sleep(5)

    def _check_journal_updates(self):
        """Check for new journal entries and broadcast them"""
        try:
            journal_file = Path(self.legion_core.journal.log_file)
            if journal_file.exists():
                with open(journal_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-10:]:  # Check last 10 entries
                        try:
                            entry = json.loads(line.strip())
                            # Broadcast to all connected clients
                            socketio.emit('journal_entry', entry)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"Error checking journal: {e}")

    def _update_system_status(self):
        """Update and broadcast system status"""
        global system_status, active_agents

        # Update status
        system_status.update({
            "active_agents": len(active_agents),
            "last_activity": datetime.now().isoformat(),
            "status": "active" if active_agents else "idle"
        })

        # Broadcast status update
        socketio.emit('system_status', system_status)


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """API endpoint for current system status"""
    return jsonify(system_status)


@app.route('/api/agents')
def get_agents():
    """API endpoint for active agents"""
    return jsonify({
        "active_agents": active_agents,
        "count": len(active_agents)
    })


@app.route('/api/journal/stream')
def journal_stream():
    """Server-sent events endpoint for journal streaming"""
    def generate():
        while True:
            try:
                # Wait for new journal entries
                if not journal_queue.empty():
                    entry = journal_queue.get()
                    yield f"data: {json.dumps(entry)}\n\n"
                time.sleep(0.1)
            except GeneratorExit:
                break
            except Exception as e:
                yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
                time.sleep(1)

    return Response(generate(), mimetype='text/event-stream')


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print("Client connected to dashboard")
    emit('system_status', system_status)


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print("Client disconnected from dashboard")


def create_dashboard_app(legion_core):
    """Create and configure the dashboard app"""
    global monitor

    # Create monitor instance
    monitor = DashboardMonitor(legion_core)

    return app, monitor


# Template for the dashboard HTML
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Legion Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .status-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        .metric h3 {
            margin: 0 0 10px 0;
            font-size: 2em;
        }
        .journal-feed {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            height: 400px;
            overflow-y: auto;
        }
        .journal-entry {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
            border-left: 4px solid #4CAF50;
        }
        .journal-entry.error {
            border-left-color: #f44336;
        }
        .journal-entry.warning {
            border-left-color: #ff9800;
        }
        .timestamp {
            color: #ccc;
            font-size: 0.8em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 Legion AI Agent Swarm</h1>
            <p>Real-time monitoring dashboard</p>
        </div>

        <div class="status-grid">
            <div class="metric">
                <h3 id="status">Initializing</h3>
                <p>System Status</p>
            </div>
            <div class="metric">
                <h3 id="active-agents">0</h3>
                <p>Active Agents</p>
            </div>
            <div class="metric">
                <h3 id="total-tasks">0</h3>
                <p>Total Tasks</p>
            </div>
            <div class="metric">
                <h3 id="last-activity">--</h3>
                <p>Last Activity</p>
            </div>
        </div>

        <div class="status-card">
            <h2>📋 Activity Feed</h2>
            <div id="journal-feed" class="journal-feed">
                <div class="journal-entry">
                    <div class="timestamp">System initialized</div>
                    <div>Dashboard connected and monitoring Legion activity...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        const journalFeed = document.getElementById('journal-feed');

        socket.on('system_status', function(data) {
            document.getElementById('status').textContent = data.status;
            document.getElementById('active-agents').textContent = data.active_agents;
            document.getElementById('total-tasks').textContent = data.total_tasks;
            document.getElementById('last-activity').textContent = new Date(data.last_activity).toLocaleTimeString();
        });

        socket.on('journal_entry', function(entry) {
            const entryDiv = document.createElement('div');
            entryDiv.className = `journal-entry ${entry.type}`;

            const timestamp = new Date(entry.timestamp).toLocaleString();
            entryDiv.innerHTML = `
                <div class="timestamp">${timestamp} - ${entry.agent}</div>
                <div><strong>${entry.type}:</strong> ${JSON.stringify(entry.data)}</div>
            `;

            journalFeed.insertBefore(entryDiv, journalFeed.firstChild);

            // Keep only last 50 entries
            while (journalFeed.children.length > 50) {
                journalFeed.removeChild(journalFeed.lastChild);
            }
        });

        // Auto-scroll to top for new entries
        socket.on('journal_entry', function() {
            journalFeed.scrollTop = 0;
        });
    </script>
</body>
</html>
"""


@app.route('/dashboard')
def dashboard():
    """Serve the dashboard HTML"""
    return DASHBOARD_HTML


if __name__ == '__main__':
    # For standalone testing
    socketio.run(app, host='localhost', port=8080, debug=True)