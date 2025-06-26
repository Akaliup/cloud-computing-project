from flask import Flask, jsonify, request
import mysql.connector
import psutil
import subprocess
import json
import os
from datetime import datetime

app = Flask(__name__)

# 数据库配置
DB_CONFIG = {
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'password'),
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': os.environ.get('DB_NAME', 'cloud_monitor_db'),
    'raise_on_warnings': True
}

# 健康检查接口
@app.route('/health')
def health_check():
    return jsonify({"status": "ok", "timestamp": str(datetime.now())})

# 准备状态检查
@app.route('/ready')
def readiness_check():
    try:
        # 检查数据库连接
        conn = mysql.connector.connect(**DB_CONFIG)
        conn.close()
        return jsonify({"status": "ready", "timestamp": str(datetime.now())})
    except Exception as e:
        return jsonify({"status": "not_ready", "error": str(e)}), 500

# 获取系统资源使用情况
@app.route('/system/stats')
def get_system_stats():
    # 获取CPU使用率
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # 获取内存使用率
    memory = psutil.virtual_memory()
    mem_percent = memory.percent
    
    # 获取磁盘使用率
    disk = psutil.disk_usage('/')
    disk_percent = disk.percent
    
    return jsonify({
        "cpu_usage_percent": cpu_percent,
        "memory_usage_percent": mem_percent,
        "disk_usage_percent": disk_percent,
        "timestamp": str(datetime.now())
    })

# 获取容器列表
@app.route('/containers')
def get_containers():
    try:
        # 执行docker ps命令获取容器列表
        result = subprocess.run(['docker', 'ps', '-a', '--format', '{"id":"{{.ID}}","name":"{{.Names}}","image":"{{.Image}}","status":"{{.Status}}"}'], 
                               capture_output=True, text=True)
        
        if result.returncode != 0:
            return jsonify({"error": "Failed to get containers", "details": result.stderr}), 500
        
        # 处理输出结果
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    container = json.loads(line)
                    containers.append(container)
                except json.JSONDecodeError:
                    # 忽略解析错误的行
                    pass
        
        return jsonify({"containers": containers, "count": len(containers)})
    
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

# 获取容器详情
@app.route('/containers/<container_id>')
def get_container_details(container_id):
    try:
        # 执行docker inspect命令获取容器详情
        result = subprocess.run(['docker', 'inspect', container_id], 
                               capture_output=True, text=True)
        
        if result.returncode != 0:
            return jsonify({"error": "Failed to get container details", "details": result.stderr}), 404
        
        try:
            details = json.loads(result.stdout)[0]
            return jsonify(details)
        except json.JSONDecodeError:
            return jsonify({"error": "Failed to parse container details"}), 500
    
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

# 获取容器资源使用统计
@app.route('/containers/<container_id>/stats')
def get_container_stats(container_id):
    try:
        # 执行docker stats命令获取容器资源使用情况
        result = subprocess.run(['docker', 'stats', '--no-stream', container_id], 
                               capture_output=True, text=True)
        
        if result.returncode != 0:
            return jsonify({"error": "Failed to get container stats", "details": result.stderr}), 404
        
        # 解析输出
        lines = result.stdout.strip().split('\n')
        if len(lines) < 2:
            return jsonify({"error": "Invalid stats output"}), 500
        
        headers = lines[0].split()
        values = lines[1].split()
        
        # 构建统计数据
        stats = {}
        for i in range(min(len(headers), len(values))):
            stats[headers[i]] = values[i]
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

# 获取服务状态
@app.route('/services/status')
def get_services_status():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 查询服务状态
        query = "SELECT * FROM service_status"
        cursor.execute(query)
        services = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({"services": services})
    
    except Exception as e:
        return jsonify({"error": "Failed to get service status", "details": str(e)}), 500

# 更新服务状态
@app.route('/services/<service_name>/status', methods=['POST'])
def update_service_status(service_name):
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({"error": "Missing 'status' in request data"}), 400
        
        status = data['status']
        if status not in ['running', 'down', 'warning']:
            return jsonify({"error": "Invalid status value. Must be 'running', 'down', or 'warning'"}), 400
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 更新服务状态
        query = "UPDATE service_status SET status = %s, last_updated = NOW() WHERE service_name = %s"
        cursor.execute(query, (status, service_name))
        conn.commit()
        
        rows_affected = cursor.rowcount
        cursor.close()
        conn.close()
        
        if rows_affected == 0:
            return jsonify({"error": f"Service '{service_name}' not found"}), 404
        
        return jsonify({"message": f"Service '{service_name}' status updated to '{status}'"})
    
    except Exception as e:
        return jsonify({"error": "Failed to update service status", "details": str(e)}), 500

# 获取容器指标历史
@app.route('/metrics/history/<container_id>')
def get_container_metrics_history(container_id):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 查询容器指标历史
        query = """
            SELECT cpu_usage, memory_usage, timestamp 
            FROM container_metrics 
            WHERE container_id = %s 
            ORDER BY timestamp DESC 
            LIMIT 100
        """
        cursor.execute(query, (container_id,))
        metrics = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({"metrics": metrics})
    
    except Exception as e:
        return jsonify({"error": "Failed to get metrics history", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)    