# 项目：TODO REST API

## 目标
构建一个功能完整的 TODO REST API，支持 CRUD 操作、输入验证和完整的测试覆盖。

## 完成标准
- [ ] 所有 CRUD 端点可正常工作
- [ ] 输入验证覆盖所有边界情况
- [ ] 测试覆盖率 > 80%
- [ ] API 文档完整（OpenAPI）

---

## Phase 1: 项目初始化 ⏳
> 预计任务数: 4

- [ ] 创建 Python 项目结构（src/, tests/, etc.）
- [ ] 配置 FastAPI + SQLAlchemy + Pydantic
- [ ] 设置 pytest 测试框架
- [ ] 创建 SQLite 数据库和 Todo 模型

## Phase 2: CRUD 实现 ⏳
> 预计任务数: 5

- [ ] GET /todos - 获取所有 TODO（支持分页）
- [ ] GET /todos/{id} - 获取单个 TODO
- [ ] POST /todos - 创建 TODO
- [ ] PUT /todos/{id} - 更新 TODO
- [ ] DELETE /todos/{id} - 删除 TODO

## Phase 3: 验证与错误处理 ⏳
> 预计任务数: 4

- [ ] Pydantic 输入验证（标题长度、状态枚举等）
- [ ] 统一错误响应格式
- [ ] 404/400/500 错误处理
- [ ] 请求日志中间件

## Phase 4: 测试 ⏳
> 预计任务数: 4

- [ ] 单元测试：模型和验证
- [ ] 集成测试：API 端点
- [ ] 边界情况测试
- [ ] 测试覆盖率报告

## Phase 5: 文档与交付 ⏳
> 预计任务数: 3

- [ ] OpenAPI 文档（自动生成）
- [ ] README 使用说明
- [ ] 最终代码审查

---

## 关键决策
| 决策 | 理由 | 迭代 |
|------|------|------|
| 使用 SQLite | 开发简单，无需额外服务 | 1 |
| FastAPI + Pydantic | 自动验证，自动文档 | 1 |

## 遇到的问题
| 问题 | 解决方案 | 迭代 |
|------|----------|------|

---

## 人工备注区
<!--
技术要求：
- Python 3.10+
- 使用 async/await
- 遵循 PEP 8
-->

