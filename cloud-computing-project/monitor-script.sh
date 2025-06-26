#!/bin/bash

# 云计算监控脚本 - 检查容器资源使用情况

# 配置参数
LOG_FILE="/var/log/cloud_monitor.log"
THRESHOLD_CPU=80
THRESHOLD_MEM=80
DB_USER="monitor_user"
DB_PASS="monitor_pass"
DB_HOST="mysql-service"
DB_NAME="cloud_monitor_db"

# 日志函数
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# 检查容器资源使用情况
check_container_resources() {
    log_message "开始检查容器资源使用情况..."
    
    # 获取所有运行中的容器
    containers=$(docker ps -q)
    
    for container in $containers; do
        # 获取容器名称
        container_name=$(docker inspect --format '{{.Name}}' $container | sed 's/^\///')
        
        # 获取CPU和内存使用率
        stats=$(docker stats --no-stream $container)
        cpu_usage=$(echo "$stats" | awk 'NR==2 {print $3}' | sed 's/%//')
        mem_usage=$(echo "$stats" | awk 'NR==2 {print $5}' | sed 's/%//')
        
        # 记录到日志
        log_message "容器: $container_name, CPU: $cpu_usage%, 内存: $mem_usage%"
        
        # 检查是否超过阈值
        if (( $(echo "$cpu_usage > $THRESHOLD_CPU" | bc -l) )); then
            log_message "警告: 容器 $container_name CPU使用率 ($cpu_usage%) 超过阈值 ($THRESHOLD_CPU%)"
            send_alert "CPU警告" "容器 $container_name CPU使用率过高: $cpu_usage%"
        fi
        
        if (( $(echo "$mem_usage > $THRESHOLD_MEM" | bc -l) )); then
            log_message "警告: 容器 $container_name 内存使用率 ($mem_usage%) 超过阈值 ($THRESHOLD_MEM%)"
            send_alert "内存警告" "容器 $container_name 内存使用率过高: $mem_usage%"
        fi
        
        # 保存到数据库
        save_metrics_to_db $container $container_name $cpu_usage $mem_usage
    done
    
    log_message "容器资源检查完成"
}

# 发送警报
send_alert() {
    subject="$1"
    message="$2"
    
    # 使用mail命令发送邮件
    echo "$message" | mail -s "$subject" admin@cloud-example.com
    
    # 记录警报日志
    log_message "发送警报: $subject - $message"
}

# 保存指标到数据库
save_metrics_to_db() {
    container_id="$1"
    container_name="$2"
    cpu_usage="$3"
    memory_usage="$4"
    
    # 插入数据到数据库
    mysql -h $DB_HOST -u $DB_USER -p$DB_PASS $DB_NAME <<EOF
INSERT INTO container_metrics (container_id, container_name, cpu_usage, memory_usage)
VALUES ('$container_id', '$container_name', $cpu_usage, $memory_usage);
EOF
}

# 主函数
main() {
    log_message "===== 开始执行监控脚本 ====="
    
    # 检查依赖
    command -v docker >/dev/null 2>&1 || { log_message "错误: 需要安装docker"; exit 1; }
    command -v mysql >/dev/null 2>&1 || { log_message "错误: 需要安装mysql客户端"; exit 1; }
    command -v mail >/dev/null 2>&1 || { log_message "警告: 未安装mail命令，警报邮件功能将不可用"; }
    
    # 执行检查
    check_container_resources
    
    log_message "===== 监控脚本执行完成 ====="
}

# 执行主函数
main    