# LifeGraph

把人生经历结构化为「时间 + 地点 + 人物 + 事件」节点，再把节点连成网络的 Django 系统。

> 一个节点 = 一次真实经历。
> 节点结构 = 三维坐标（时间 / 地点 / 参与者）+ 内容。
> 本质：把人生变成可记录、可检索、可连接的数据。

完整产品定义见 [`first.md`](first.md)。

---

## 当前阶段

阶段 1（单人节点系统）：

- 极简输入：一句话写入一个节点
- 时间线主视图（前台）
- 后台节点 / 参与者管理（Django Admin + Unfold）
- 多语言（zh-hans / en）
- 后续规划：AI 自动结构化 → 多人节点 → 关系网络可视化

---

## 技术栈

| 层 | 选型 |
| --- | --- |
| Web | Django 5.x + Gunicorn |
| DB | PostgreSQL 17 |
| Cache / Session | Redis 7 |
| Admin | django-unfold |
| 定时任务 | django-apscheduler |
| 反向代理 | Caddy 2.8（生产） |
| 编排 | Docker Compose（base + override + prod 三文件） |

---

## 目录结构

```
.
├── docker-compose.yml              # 基础服务定义
├── docker-compose.override.yml     # 本地开发覆盖（自动加载）
├── docker-compose.prod.yml         # 生产覆盖
├── Makefile                        # 一键操作命令
├── docker/django/                  # Dockerfile / entrypoint / gunicorn
├── deploy/vps/                     # Caddyfile + 生产环境变量示例
├── requirements/                   # base / dev / prod 三套依赖
├── scripts/                        # 本地初始化与自检脚本
└── src/
    ├── config/                     # Django settings / urls / wsgi / asgi
    ├── core/                       # 中间件、Telegram、Turnstile、上传校验
    ├── apps/lifegraph/             # 业务模型与视图
    ├── templates/                  # 前台 + admin 模板
    ├── static/                     # 手写静态资源
    └── locale/                     # i18n 翻译
```

---

## 快速开始（本地开发）

需要：Docker Desktop。

```bash
# 1. 生成本地 .env（仅占位值，可直接跑）
bash scripts/init_local_env.sh

# 2. 起服务（db + redis + web）
make up

# 3. 数据库迁移
make migrate

# 4. 创建超级用户
make createsuperuser
```

访问：

- 前台时间线：<http://localhost:28000/>
- 后台：<http://localhost:28000/admin/>（路径由 `DJANGO_ADMIN_URL` 控制）

常用命令：

```bash
make logs          # 看全部日志
make logs-web      # 只看 Django
make shell         # 进 web 容器
make shell-db      # 进 Postgres 容器
make down          # 停服务
make reset         # 清数据卷重建
make check         # Django check --deploy
```

---

## 生产部署

生产编排走 `docker-compose.yml + docker-compose.prod.yml`，由 Caddy 反代 Django。

### 1. 准备 VPS 环境变量

```bash
cp deploy/vps/env/.env.lifegraph.example deploy/vps/env/.env.lifegraph
# 编辑填入真实的 SECRET_KEY / 数据库密码 / 域名 / ADMIN_URL 等
```

需要填的关键字段：

| 变量 | 说明 |
| --- | --- |
| `DJANGO_SECRET_KEY` | 长随机串，必填 |
| `DJANGO_DEBUG` | 生产固定 `false` |
| `DJANGO_ALLOWED_HOSTS` | 你的域名，逗号分隔 |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://example.com` 形式 |
| `POSTGRES_PASSWORD` | 强密码 |
| `APP_DOMAIN` | Caddy 提供服务的域名 |
| `DJANGO_ADMIN_URL` | 自定义后台路径，避免默认 `/admin/` |

### 2. 准备 TLS 证书

Caddyfile 默认从 `/etc/lifegraph/certs/` 读取 Cloudflare Origin 证书：

```
/etc/lifegraph/certs/cf-origin.pem
/etc/lifegraph/certs/cf-origin.key
```

如不用 Cloudflare，可改 `deploy/vps/caddy/Caddyfile` 让 Caddy 自动签 Let's Encrypt。

### 3. 一键部署

```bash
make prod-build
```

该命令会：down 旧栈 → 重建镜像 → 起 db / redis / web / proxy。

部署成功后若配置了 `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`，`entrypoint.sh` 会推送一条部署通知。

---

## 安全特性

`src/core/middleware.py` 内置若干中间件，生产默认启用：

- `TurnstileAdminLoginMiddleware` — 后台登录 Cloudflare Turnstile 验证
- `SessionTimeoutMiddleware` — 会话超时
- `RateLimitMiddleware` — 接口限流
- `AdminNoCacheMiddleware` — 后台禁缓存
- `SecurityHeadersMiddleware` — 安全响应头

生产配置（`settings.py` 的 `if not DEBUG` 分支）会强制启用 HSTS / Secure Cookie / X-Frame-Options 等。

---

## 数据备份与恢复

```bash
make backup-db                    # 导出到当前目录的 backup.sql
make restore-db                   # 从 backup.sql 恢复
```

生产环境的 `lifegraph_backup_data` 卷映射到容器内 `/app/backups/`，配合 `django-apscheduler` 可做定时备份。

---

## 项目状态

本仓库目前**封存中**。后续何时复工不定，欢迎 fork 自用。

---

## License

未指定。如需复用请先与作者联系。
