# ERS Official System

授权管理系统配置文件

## 文件说明

| 文件名 | 用途 |
|--------|------|
| `ers-license.json` | **AES-256 + Base64 双重加密**的授权许可证 |

## ⚠️ 安全警告

此文件使用 **AES-256-CBC** 加密，**不包含明文密码**！

## 加密信息

- **算法**: AES-256-CBC
- **密钥长度**: 256 位
- **编码**: Base64

## Worker 代码使用示例

```javascript
// 1. 从 GitHub 获取 Base64 内容
var encryptedBase64 = "SFNYSWtJb1pL..."; // 从 ers-license.json 读取

// 2. AES-256 解密（需要 Crypto API）
var encrypted = atob(encryptedBase64);
var decrypted = decryptAES(encrypted);
var USERS = JSON.parse(decrypted).users;

// 3. 验证登录
if (USERS[username] === password) {
    // 登录成功
}
```

## 加密脚本

参见项目根目录的 `generate-encrypted-license.js` 了解如何生成新的授权文件。

## 版本历史

- v1.0 - 初始版本，使用 AES-256 + Base64 双重加密 (2024)
