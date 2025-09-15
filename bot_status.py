"""
Bot Status Monitoring and Health Check Service
Provides real-time status monitoring for all platform bots
"""

from flask import Blueprint, jsonify, render_template_string
from flask_login import login_required, current_user
from bot_manager import bot_manager
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Create blueprint for bot status endpoints
bot_status_bp = Blueprint('bot_status', __name__)

@bot_status_bp.route('/bot-status')
@login_required
def bot_status_page():
    """Bot status monitoring page for admins"""
    if not current_user.is_admin:
        return "Access denied - Admin only", 403
    
    status_template = """
    <!DOCTYPE html>
    <html lang="uz">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🤖 Bot Status Monitor - BotFactory AI</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                background: white;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                text-align: center;
            }
            .status-card {
                background: white;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .status-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }
            .bot-card {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 15px;
            }
            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 8px;
            }
            .status-running { background: #28a745; }
            .status-error { background: #dc3545; }
            .status-starting { background: #ffc107; }
            .metric {
                display: flex;
                justify-content: space-between;
                margin: 8px 0;
                padding: 8px 0;
                border-bottom: 1px solid #eee;
            }
            .metric:last-child {
                border-bottom: none;
            }
            .refresh-button {
                background: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 16px;
            }
            .refresh-button:hover {
                background: #0056b3;
            }
            .auto-refresh {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #28a745;
                color: white;
                padding: 10px;
                border-radius: 20px;
                font-size: 14px;
            }
        </style>
        <script>
            // Auto-refresh every 10 seconds
            setTimeout(() => {
                window.location.reload();
            }, 10000);
            
            function refreshNow() {
                window.location.reload();
            }
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 BotFactory AI - Bot Status Monitor</h1>
                <p>Real-time monitoring of all platform bots</p>
                <button class="refresh-button" onclick="refreshNow()">🔄 Refresh Now</button>
            </div>
            
            <div class="status-card">
                <h2>📊 System Overview</h2>
                <div class="metric">
                    <span>Bot Manager Status:</span>
                    <span>
                        <span class="status-indicator {{ 'status-running' if status.startup_complete else 'status-starting' }}"></span>
                        {{ 'Running' if status.startup_complete else 'Starting' }}
                    </span>
                </div>
                <div class="metric">
                    <span>Total Active Bots:</span>
                    <span><strong>{{ status.total_active_bots }}</strong></span>
                </div>
                <div class="metric">
                    <span>System Uptime:</span>
                    <span>{{ system_uptime }}</span>
                </div>
                <div class="metric">
                    <span>Last Updated:</span>
                    <span>{{ current_time }}</span>
                </div>
            </div>
            
            {% if status.bots %}
            <div class="status-card">
                <h2>🤖 Active Bots</h2>
                <div class="status-grid">
                    {% for bot_key, bot_info in status.bots.items() %}
                    <div class="bot-card">
                        <h3>
                            <span class="status-indicator {{ 'status-running' if bot_info.status == 'running' else 'status-error' }}"></span>
                            {{ bot_info.name }}
                        </h3>
                        <div class="metric">
                            <span>Platform:</span>
                            <span>{{ bot_info.platform.title() }}</span>
                        </div>
                        <div class="metric">
                            <span>Status:</span>
                            <span>{{ bot_info.status.title() }}</span>
                        </div>
                        <div class="metric">
                            <span>Started:</span>
                            <span>{{ bot_info.started_at }}</span>
                        </div>
                        <div class="metric">
                            <span>Uptime:</span>
                            <span>{{ "%.1f"|format(bot_info.uptime_seconds / 60) }} minutes</span>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% else %}
            <div class="status-card">
                <h2>⚠️ No Active Bots</h2>
                <p>No bots are currently running. Check the database for active bots or verify bot tokens.</p>
            </div>
            {% endif %}
        </div>
        
        <div class="auto-refresh">
            🔄 Auto-refresh: 10s
        </div>
    </body>
    </html>
    """
    
    try:
        # Get bot manager status
        status = bot_manager.get_bot_status()
        
        # Calculate system uptime (approximate)
        system_uptime = "Active"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return render_template_string(
            status_template, 
            status=status, 
            system_uptime=system_uptime,
            current_time=current_time
        )
        
    except Exception as e:
        logger.error(f"Error rendering bot status page: {e}")
        return f"Error loading bot status: {str(e)}", 500

@bot_status_bp.route('/api/bot-status')
@login_required
def api_bot_status():
    """API endpoint for bot status (JSON)"""
    if not current_user.is_admin:
        return jsonify({"error": "Access denied"}), 403
    
    try:
        status = bot_manager.get_bot_status()
        
        # Add additional system info
        status['timestamp'] = datetime.now().isoformat()
        status['system'] = 'BotFactory AI'
        status['version'] = '1.0'
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting bot status via API: {e}")
        return jsonify({
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "status": "error"
        }), 500

@bot_status_bp.route('/api/bot-health')
def bot_health_check():
    """Public health check endpoint for monitoring systems"""
    try:
        from bot_manager import get_bot_manager_health
        health = get_bot_manager_health()
        
        # Determine HTTP status code based on health
        status_code = 200 if health['status'] in ['healthy', 'starting'] else 500
        
        return jsonify(health), status_code
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@bot_status_bp.route('/api/restart-bot/<int:bot_id>')
@login_required
def restart_bot_api(bot_id):
    """API endpoint to restart a specific bot"""
    if not current_user.is_admin:
        return jsonify({"error": "Access denied"}), 403
    
    try:
        from models import Bot
        
        bot = Bot.query.get(bot_id)
        if not bot:
            return jsonify({"error": "Bot not found"}), 404
        
        if not bot.is_active:
            return jsonify({"error": "Bot is not active"}), 400
        
        # Restart the bot
        platform = bot.platform.lower()
        bot_manager.restart_bot(bot_id, platform)
        
        logger.info(f"Admin {current_user.username} restarted bot {bot.name} (ID: {bot_id})")
        
        return jsonify({
            "success": True,
            "message": f"Bot {bot.name} restart initiated",
            "bot_id": bot_id,
            "platform": platform
        })
        
    except Exception as e:
        logger.error(f"Error restarting bot {bot_id}: {e}")
        return jsonify({
            "error": str(e),
            "bot_id": bot_id
        }), 500