# ERS Official System

鎺堟潈绠＄悊绯荤粺閰嶇疆鏂囦欢

## 鏂囦欢璇存槑

| 鏂囦欢鍚?| 鐢ㄩ€?|
|--------|------|
| `ers-license.json` | Base64 缂栫爜鐨勬巿鏉冭鍙瘉锛堜緵 Worker 浠ｇ爜寮曠敤锛?|
| `ers-auth.json` | 鏄庢枃鎺堟潈鏁版嵁锛堜粎渚涘弬鑰冿紝涓嶈鍏紑锛?|
| `README.md` | 鏈鏄庢枃浠?|

## 鎺堟潈璐﹀彿

- **鐢ㄦ埛鍚?*: bavenbaven
- **瀵嗙爜**: YQXyqx19840212#

## 浣跨敤鏂规硶

灏嗕互涓?Base64 瀛楃涓插祵鍏?Cloudflare Worker 浠ｇ爜锛?
```javascript
var LICENSE_DATA = atob("BASE64_HERE");
var USERS = JSON.parse(LICENSE_DATA).users;
```

## 鐗堟湰鍘嗗彶

- v1.0 - 鍒濆鐗堟湰 (2024)
