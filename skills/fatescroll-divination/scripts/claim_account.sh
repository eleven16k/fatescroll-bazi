#!/usr/bin/env bash
# 绑定 Fatescroll 账号：打印配对码与一键链接（无本机 token 则先匿名注册）
# 用户在浏览器打开链接（5 分钟有效、一次性）即登录技能侧账号——排盘历史与额度随之同步到网页版。
set -euo pipefail
umask 077  # token 文件是登录凭证，不给同机其他用户读；先于 mkdir 使新建目录/文件一并受保护
API="${FATESCROLL_API:-https://api.fatescroll.ai}"
WEB="${FATESCROLL_WEB:-https://fatescroll.ai}"
TOKEN_FILE="${HOME}/.fatescroll/token"
mkdir -p "$(dirname "$TOKEN_FILE")"
if [ ! -s "$TOKEN_FILE" ]; then
  DID="skill-$(uuidgen | tr 'A-Z' 'a-z')"
  TOKEN=$(curl -fsS -X POST "$API/api/auth/device" -H 'Content-Type: application/json' -d "{\"deviceId\":\"$DID\"}" | sed -n 's/.*"token":"\([^"]*\)".*/\1/p')
  [ -n "$TOKEN" ] || { echo "註冊失敗：無法從 API 回應解析 token" >&2; exit 1; }
  printf '%s' "$TOKEN" > "$TOKEN_FILE"
fi
# 簽發：附帶狀態碼取回應（-w 末行為 HTTP code），精確區分三類失敗——
# 僅 401/403（鑑權確鑿失效）刪檔自愈；網路錯/5xx 憑證仍可能有效，保留僅提示重試
if ! RESP=$(curl -sS -w '\n%{http_code}' -X POST "$API/api/claim" -H "Authorization: Bearer $(cat "$TOKEN_FILE")"); then
  echo "網路異常：無法連線 ${API}，請稍後重試（本機憑證已保留）" >&2
  exit 1
fi
HTTP=$(printf '%s' "$RESP" | tail -n 1)
if [ "$HTTP" = "401" ] || [ "$HTTP" = "403" ]; then
  rm -f "$TOKEN_FILE"
  echo "本機 token 已失效，請重新執行本命令" >&2
  exit 1
fi
if [ "$HTTP" != "200" ]; then
  echo "簽發失敗：服務端返回 HTTP ${HTTP}，請稍後重試（本機憑證已保留）" >&2
  exit 1
fi
CODE=$(printf '%s' "$RESP" | sed -n 's/.*"code":"\([^"]*\)".*/\1/p')
TTOK=$(printf '%s' "$RESP" | sed -n 's/.*"token":"\([^"]*\)".*/\1/p')
# 防 200 但非本接口 JSON（代理劫持/captive portal）：空解析直接拒出，不出死链
[ -n "$CODE" ] && [ -n "$TTOK" ] || { echo "簽發失敗：無法從 API 回應解析 code/token" >&2; exit 1; }
echo "配对码：${CODE}（备查；网页版无配对码输入页，绑定请用下方链接）"
echo "一键链接（5 分钟有效，仅限一次）：${WEB}/claim?t=${TTOK}"
