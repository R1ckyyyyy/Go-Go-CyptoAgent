# 部署指南 (Deployment Guide)

本系统支持使用 Docker Compose 进行一键部署，包含后端 API、前端界面和 Redis 缓存服务。

## 前置要求
- Docker Engine >= 19.03
- Docker Compose >= 1.28

## 快速开始

1. **构建并启动服务**
   ```bash
   docker-compose up -d --build
   ```

2. **验证部署**
   - 前端界面: [http://localhost](http://localhost)
   - 后端 API 文档: [http://localhost:8000/docs](http://localhost:8000/docs)

3. **停止服务**
   ```bash
   docker-compose down
   ```

## 目录结构映射

- `backend/data`: 挂载到容器 `/app/data`，持久化数据库和日志。
- `backend/config`: 挂载到容器 `/app/config`，支持热更新配置。

## 环境变量
在 `.env` 文件中配置（已移动到 `backend/.env`，Docker 会自动加载）：
- `Nothing special yet`

## 常见问题
- **端口冲突**: 如果 80 端口被占用，请修改 `docker-compose.yml` 中的 frontend ports 映射（例如 `"8080:80"`）。
- **数据库路径**: 默认使用 SQLite，数据保存在 `backend/data/database.db`。
