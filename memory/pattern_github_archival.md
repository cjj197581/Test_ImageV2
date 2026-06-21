---
name: pattern-github-project-archival
description: "Complete workflow to archive a Python project to GitHub: git init, .gitignore security audit, README, commit, remote, branch rename, push"
metadata: 
  node_type: memory
  type: pattern
  originSessionId: f16ddc1d-3f44-42bf-8daa-6373bda1f48a
---

## GitHub 项目封存完整流程

### Step 1: Git 初始化
```bash
cd E:\项目目录
git init
git config user.name "你的GitHub用户名"
git config user.email "你的邮箱"
```

### Step 2: .gitignore 安全审计 (关键!)

逐类检查，确保敏感信息不泄露：

| 类别 | 排除规则 | 原因 |
|------|---------|------|
| API Key | `.env` | 绝对不能提交 |
| 缓存 | `__pycache__/`, `*.py[cod]` | 系统生成 |
| 截图 | `*截图*/`, `*API易*/*`, `*apiyi*/*` | 含账户余额/用户名 |
| 个人照片 | `参考图/` | 含用户隐私 |
| 二进制大文件 | `output/` (可选) | 看用户是否要求展示 |

**审查命令:** `git add --dry-run .` 预览所有将被提交的文件，逐一确认无敏感信息。

### Step 3: README 编写
- 项目简介 (一句话)
- 快速开始 (3-4 行命令)
- 项目结构 (树形图)
- 关键特性/模型对比
- 使用说明
- 许可证

### Step 4: 分阶段提交
```
第一批: 源码 + 文档 + 配置 (不含 output/)
git add src/ examples/ *.md .env.example .gitignore requirements.txt
git commit -m "Initial commit: ..."

第二批: 生成物 (如果用户要求)
git add output/ prompts_*/
git commit -m "Add generated images and videos as examples"

第三批: README 更新
git commit -m "docs: update README ..."
```

### Step 5: 推送
```bash
# 用户在 GitHub 网页上创建空仓库 (不要勾选 README/.gitignore/LICENSE)
git remote add origin git@github.com:用户名/仓库名.git
git branch -M main        # 本地 master → main (GitHub 默认分支名)
git push -u origin main
```

### 常见陷阱
- **忘记 git branch -M main** → 推送后 GitHub 上出现 master 分支, 需要手动改默认分支
- **先创建 GitHub 仓库并勾选 README** → 推送时会冲突, 需要 git pull --rebase
- **.bat 文件中文乱码** → 确保用 GBK 编码保存
- **SSH 权限问题** → 确认 `gh auth status` 或 SSH key 已配置

Related: [[feedback-windows-bat-encoding]]
