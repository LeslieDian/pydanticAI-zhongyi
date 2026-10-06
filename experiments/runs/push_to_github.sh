#!/usr/bin/env bash
# 推送到 GitHub。网络恢复后运行：
#   bash experiments/runs/push_to_github.sh
set -e
cd "$(dirname "$0")/../.."
git push -u origin main
echo "OK pushed. Verify at https://github.com/LeslieDian/pydanticAI-zhongyi"
