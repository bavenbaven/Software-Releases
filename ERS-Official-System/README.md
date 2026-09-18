# ERS Official System

授权管理系统配置文件

## 文件说明

| 文件名 | 用途 |
|--------|------|
| `ers-license.json` | Base64 编码的加密授权许可证（供 Worker 代码引用） |

> ⚠️ **安全提示**: 授权信息仅以加密形式存储，不包含明文密码

## 使用方法

在 Cloudflare Worker 代码中引用授权：

```javascript
var LICENSE_DATA = atob("BASE64_STRING_HERE");
var USERS = JSON.parse(LICENSE_DATA).users;
```

## 版本历史

- v1.0 - 初始版本 (2024)
