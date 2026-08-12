# Backend Harness Template

一个可直接复制的 FastAPI 后端 Harness 模板。它把项目上下文、API/数据库边界、机械验证、CI、迁移、集成测试、Loop 状态、预算和人工门禁放进同一个仓库。

模板附带最小 FastAPI + PostgreSQL + Redis 示例，但重点是外围 Harness，不是 `example_items` 业务。

## 快速开始

```bash
cd /path/to/backend-harness-template
uv run python scripts/create_project.py \
  --target ../my-backend \
  --name my-backend \
  --provider github \
  --description "一句话说明产品、用户和核心结果"

cd ../my-backend
uv sync --all-groups
cp .env.test.example .env.test
docker compose up -d
APP_ENV_FILE=.env.test make verify
```

`--provider` 支持 `github`、`gitlab` 和 `both`，省略时默认为 `both`。生成单平台项目时会删除另一平台的专属文件。

创建脚本会排除虚拟环境、缓存、覆盖率、构建产物和 Git 元数据，再更新项目名称、描述、SCM provider 和 lockfile 中的根项目名称。它不会初始化 Git、创建分支、提交、推送、创建数据库或部署。

已经复制好的项目可以重新初始化元数据：

```bash
uv run python scripts/init_harness.py \
  --name my-backend \
  --provider github \
  --description "新的项目摘要"
```

单平台项目若要恢复已经删除的平台文件，应从模板重新创建。

## 首次采用必须人工完成

1. 更新 `docs/project-context.md` 和 `docs/architecture.md`。
2. 删除或替换 `example_items` 示例模型、迁移、CRUD、API 和测试。
3. 明确身份、权限、时间、幂等、删除、保留、重试和状态转换语义。
4. 把真实高风险路径补进 `harness.config.json`、`harness/loop-policy.json` 和 `gate.yaml`。
5. 用业务关键测试替换示例测试，并根据基线调整覆盖率门槛。
6. 在 GitHub 或 GitLab 启用默认分支保护，要求 CI 通过且至少一人审批。
7. 保持 Loop 为 report-only，直到 `docs/loop-operations.md` 的升级条件全部满足。

## Provider 模式

| Provider | CI 与评审配置 | 依赖更新配置 |
| --- | --- | --- |
| `github` | GitHub Actions、PR 模板 | Dependabot |
| `gitlab` | GitLab Pipeline、MR 模板 | Renovate |
| `both` | 同时保留两套配置 | Dependabot + Renovate；只启用团队真实使用的平台 |

两种 CI 使用相同的 Make 目标，避免本地和流水线的验收口径分叉。

## 默认质量门禁

| 命令 | 作用 |
| --- | --- |
| `make format-check` | 检查 Python 格式漂移 |
| `make lint` | Ruff 静态检查 |
| `make typecheck` | 严格 MyPy 检查 |
| `make test-coverage` | 单元测试和覆盖率阈值 |
| `make check-harness` | 校验 Harness 文件、预算、SCM 和保护路径 |
| `make check-api-policy` | 机械阻止 PUT/PATCH/DELETE 等方法 |
| `make check-db-boundaries` | 阻止 Route 直接执行 SQLAlchemy |
| `make migration-check` | 检查 Alembic 单根、单头、完整无环链 |
| `make openapi-check` | 检查提交的 OpenAPI 与实际路由是否漂移 |
| `make security-audit` | 审计当前锁定依赖的安全公告 |
| `make preflight` | 聚合无需外部服务的确定性门禁 |
| `make db-upgrade test-integration` | 在隔离 PostgreSQL/Redis 上迁移并跑集成测试 |
| `make verify` | 完整验证 |

## 本地运行

```bash
uv sync --all-groups
cp .env.example .env
docker compose up -d
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8080
```

示例端点：

- `GET /api/health/live`
- `GET /api/health/ready`
- `POST /api/examples/create`
- `POST /api/examples/get`
- `POST /api/examples/search`

OpenAPI：`http://localhost:8080/docs`。

## 目录

```text
.
├── .github/                 # GitHub CI、PR 模板、Dependabot
├── .gitlab/                 # GitLab MR 模板
├── app/
│   ├── api/routes/          # 薄 HTTP 层
│   ├── core/                # 配置和公共错误
│   ├── db/crud/             # 业务持久化和事务
│   ├── db/models/           # SQLAlchemy 模型
│   ├── schemas/             # 公开请求/响应契约
│   └── services/            # 跨基础设施编排
├── docs/                    # 架构、API、迁移、测试、Git、Loop 运维
├── harness/                 # 机器可读策略、预算、项目元数据、运行记录
├── migrations/              # Alembic 迁移
├── scripts/                 # 初始化和确定性 Harness 检查器
├── tests/unit/              # 无外部服务的确定性测试
├── tests/integration/       # 隔离 PostgreSQL/Redis 集成测试
├── AGENTS.md                # 编码 Agent 的项目规则
├── LOOP.md                  # 默认后端巡检循环
├── STATE.md                 # 跨会话状态
├── gate.yaml                # Git 写操作和高风险路径门禁
└── loop-constraints.md      # 人类可读的 Loop 安全约束
```

## 设计原则

- 确定性验证优先于概率性提示。
- 默认只报告，逐级增加自治。
- Builder 和 Checker 分离。
- API 契约、数据库行为和异步状态机需要更强的人类门禁。
- 本地、GitHub 和 GitLab 使用相同验收命令。
- 每次执行有状态、预算、最大尝试次数和停止条件。
- 失败必须产生可审计证据，不能通过削弱测试隐藏。

详细采用路线见 [Harness 采用指南](docs/harness-adoption.md)。
