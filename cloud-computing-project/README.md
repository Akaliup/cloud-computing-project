# 云计算监控与管理系统

这是一个基于容器化技术的云计算监控与管理系统，用于监控和管理云环境中的容器、服务和资源。系统采用微服务架构设计，使用Docker和Kubernetes进行容器化部署和编排，提供了完善的监控、告警和管理功能。

## 项目架构

系统主要由以下组件构成：

- **监控服务**：负责收集和分析容器、服务和系统资源的使用情况
- **API网关**：提供统一的API接口，处理请求路由和权限控制
- **数据存储**：使用MySQL数据库存储监控数据和系统配置
- **告警系统**：基于预设阈值，自动检测并发送告警通知
- **前端界面**：提供直观的可视化监控界面和管理功能

所有组件均采用容器化部署，并通过Kubernetes进行编排管理。

## 技术栈

- **容器化技术**：Docker, Kubernetes (k8s)
- **后端开发**：Python, Flask框架
- **数据库**：MySQL
- **自动化工具**：GitHub Actions, Shell脚本
- **监控工具**：Prometheus, Grafana (可集成)

## 项目功能

1. **容器监控**：实时监控容器的CPU、内存和磁盘使用情况
2. **服务状态管理**：跟踪和管理云服务的运行状态
3. **告警系统**：当资源使用超过阈值时自动触发告警
4. **API接口**：提供RESTful API用于系统集成和扩展
5. **自动化部署**：基于GitHub Actions的CI/CD流程，实现自动化构建和部署

## 部署指南

### 前提条件

- 已安装Docker和Docker Compose
- 已配置Kubernetes集群 (可使用Minikube或云提供商的K8s服务)
- 具备基本的云计算和容器化知识

### 部署步骤

1. **克隆项目代码**
git clone https://github.com/yourusername/cloud-computing-project.git
cd cloud-computing-project
2. **构建Docker镜像**
docker build -t cloud-monitor:v1.0.0 .
3. **创建Kubernetes资源**
kubectl apply -f k8s-deployment.yaml
4. **配置数据库**
# 创建数据库和表
kubectl exec -it <mysql-pod-name> -- mysql -u root -p
# 输入密码后执行init-db.sql中的SQL语句
5. **验证部署**
kubectl get pods,svc
# 确认所有Pod和Service都正常运行
6. **访问应用**

通过LoadBalancer服务的外部IP地址访问应用界面：
kubectl get svc cloud-monitor-service
# 在浏览器中访问<EXTERNAL-IP>
## 使用说明

系统提供以下主要功能：

- **系统概览**：显示整体系统状态和关键指标
- **容器管理**：查看和管理所有容器，包括详细的资源使用情况
- **服务状态**：监控和管理云服务的运行状态
- **告警历史**：查看历史告警记录和处理状态
- **API文档**：提供系统API的详细文档和测试工具

## 贡献指南

1.  Fork项目到自己的GitHub账户
2.  创建新的feature分支：`git checkout -b new-feature`
3.  提交代码变更：`git commit -am 'Add some feature'`
4.  将分支推送到GitHub：`git push origin new-feature`
5.  提交Pull Request

## 许可证

本项目采用MIT许可证。有关详细信息，请参阅LICENSE文件。    