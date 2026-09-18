# ERS Official System

授权管理系统配置文件

## 文件说明

| 文件名 | 用途 |
|--------|------|
| `ers-license.json` | Base64 + AES-256 双重加密的授权许可证 |

## 授权账号

- **用户名**: bavenbaven
- **密码**: YQXyqx19840212#（已加密存储）

## 使用方法

### Worker 代码引用

```javascript
// 第一步：Base64 解码
var LICENSE_DATA = atob("BASE64_ENCODED_CONTENT");

// 第二步：AES-256 解密（需要实现解密函数）
var license = decryptAES(LICENSE_DATA);
var USERS = JSON.parse(license).users;

// 第三步：验证登录
if (USERS[username] && USERS[username] === password) {
    // 登录成功
}
```

### 密钥信息（仅保存在安全位置）

- **算法**: AES-256-CBC
- **Key**: 固定密钥（建议生产环境动态生成）
- **IV**: 固定初始化向量

## 版本历史

- v1.0 - 初始版本，使用 Base64 + AES-256 双重加密 (2024)
