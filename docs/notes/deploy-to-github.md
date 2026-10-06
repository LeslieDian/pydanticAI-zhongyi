# 部署到 GitHub

本地已完成所有提交（2 个 commit）。由于环境网络问题无法直接推送。

## 三种推送方式

### 方弎 1：直接 push（最简单）

网络恢复后：

```bash
git push -u origin main
```

### 方弎 2：用 bundle 推送（本项目已生成）

```bash
git clone experiments/runs/pydanticAI-zhongyi.bundle pydanticAI-zhongyi-pushed
cd pydanticAI-zhongyi-pushed
git remote set-url origin https://github.com/LeslieDian/pydanticAI-zhongyi.git
git push -u origin main
```

### 方弎 3：手动上传到 GitHub

在 https://github.com/LeslieDian/pydanticAI-zhongyi 页面点 **Upload files**。

**不要上传 .env**（含真实 API key，已被 .gitignore 排除）。

## 推送前请确认

```bash
git log --oneline
git status
```

## 推送后请验证

```bash
# 克隆到本机另一目录验证
git clone https://github.com/LeslieDian/pydanticAI-zhongyi.git verify-clone
cd verify-clone
pip install -e ".[dev]"
pytest tests/
```
