# 贡献指南

感谢您参与本仓库的贡献！

## 提交 Issue

- 请先搜索已有 Issue，避免重复。
- 描述问题时请附上：复现步骤、期望行为、实际行为、相关日志与环境信息（Terraform 版本、区域等）。

## 提交 Pull Request

1. Fork 本仓库并创建特性分支。
2. 修改代码后请自测：
   - 函数：`python -m py_compile src/functions/*/index.py`
   - 基础设施：`cd infra && terraform validate`
   - 前端：`cd src/frontend && npm run build`
3. 保持文档同步更新（README、docs/）。
4. 提交 PR 时说明变更动机与影响范围。

## 代码规范

- Python：PEP 8，函数入口保持 `handler(event, context)` 签名。
- Terraform：变量须注明是否敏感（`sensitive = true`），禁止硬编码凭据。
- 前端：保持现有组件风格，新增依赖需在 PR 中说明理由。

## 合规要求

- 仓库中不得出现任何明文 AK/SK、口令或 JWT 密钥。
- 涉及人脸等生物特征信息的功能，必须在产品层面提供用户授权与告知（参见前端授权弹窗）。
