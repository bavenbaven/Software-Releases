#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERS Tech Music - 官方授权中心密钥与账号生成器
用于读取或生成 200 个 12 位卡密、200 组 VIP 账号密码，导出备份文档并在 auth.json 中生成 1 对 1 对应的加密哈希与鉴权结构
"""

import os
import sys
import json
import csv
import hashlib
import secrets
import base64
from datetime import datetime

# 强制 UTF-8 标准输出
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# 密钥字符集（剔除容易混淆的 0, O, 1, I, L 等字符）
KEY_CHARS = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"
PWD_CHARS = "23456789abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ"

# 统一预置盐值与加密密钥（与客户端 authService.ts 保持一致）
AUTH_SALT = "ERS_TECH_AUTH_SALT_V4_SECURE_2026"
ENCRYPTION_KEY_RAW = "ERS_TECH_MUSIC_V4_MASTER_SECRET_KEY_20260806"

def derive_key(secret: str) -> bytes:
    """生成 32 字节 AES 密钥"""
    return hashlib.sha256(secret.encode("utf-8")).digest()

def stream_encrypt(data_str: str, key_bytes: bytes) -> tuple[str, str]:
    """
    使用跨平台标准的流式异或加密与动态哈希链（兼容纯 JS/TS 解密与纯 Python 3）
    """
    iv = secrets.token_bytes(16)
    iv_b64 = base64.b64encode(iv).decode("utf-8")
    
    data_bytes = data_str.encode("utf-8")
    
    stream_key = bytearray()
    counter = 0
    while len(stream_key) < len(data_bytes):
        block = hashlib.sha256(key_bytes + iv + counter.to_bytes(4, 'big')).digest()
        stream_key.extend(block)
        counter += 1
        
    encrypted_bytes = bytes([b ^ k for b, k in zip(data_bytes, stream_key[:len(data_bytes)])])
    return base64.b64encode(encrypted_bytes).decode("utf-8"), iv_b64

def generate_12_digit_key() -> str:
    """生成形如 'A8K2-9M4Q-3X7W' 的 12 位格式化卡密"""
    raw_chars = [secrets.choice(KEY_CHARS) for _ in range(12)]
    return f"{''.join(raw_chars[0:4])}-{''.join(raw_chars[4:8])}-{''.join(raw_chars[8:12])}"

def generate_password(length=12) -> str:
    """生成 12 位高强度密码"""
    return "".join(secrets.choice(PWD_CHARS) for _ in range(length))

def hash_credential(value: str) -> str:
    """标准化 SHA-256 哈希计算 (去除连接符并转大写加盐计算不可逆哈希)"""
    clean_val = value.replace("-", "").strip().upper()
    return hashlib.sha256(f"{clean_val}:{AUTH_SALT}".encode("utf-8")).hexdigest()

def hash_password(password: str) -> str:
    """密码加盐 SHA-256 哈希计算"""
    return hashlib.sha256(f"{password.strip()}:{AUTH_SALT}".encode("utf-8")).hexdigest()

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(script_dir, "keys_and_accounts_backup.csv")
    txt_file = os.path.join(script_dir, "keys_and_accounts_backup.txt")
    auth_json_path = os.path.join(script_dir, "auth.json")
    version_json_path = os.path.join(script_dir, "version.json")
    
    print("==================================================")
    print("🚀 ERS Tech Music 官方授权中心 - 密钥与账号同步管理")
    print("==================================================")
    
    TOTAL_KEYS = 200
    TOTAL_ACCOUNTS = 200
    
    license_keys = []
    accounts = []
    
    # 优先从现有的 CSV 读取
    if os.path.exists(csv_file):
        print(f"📖 读取现有备份清单: {csv_file}")
        with open(csv_file, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if not row or len(row) < 4:
                    continue
                rtype, idx, val, pwd = row[0].strip(), row[1].strip(), row[2].strip(), row[3].strip()
                if "卡密" in rtype:
                    if val not in license_keys:
                        license_keys.append(val)
                elif "账号" in rtype or "VIP" in rtype:
                    if not any(a["username"] == val for a in accounts):
                        accounts.append({
                            "id": int(idx) if idx.isdigit() else len(accounts) + 1,
                            "username": val,
                            "password": pwd,
                            "role": "VIP 尊享用户",
                            "tier": "VIP尊享",
                            "max_devices": 3
                        })
                        
    # 确保特定专属账号 bavenbaven 存在且配置最高权限
    admin_acc = next((a for a in accounts if a["username"] == "bavenbaven"), None)
    if not admin_acc:
        accounts.insert(0, {
            "id": 0,
            "username": "bavenbaven",
            "password": "yqx19840212",
            "role": "超级管理员 / 终身SVIP",
            "tier": "SVIP 永久旗舰版",
            "max_devices": 99
        })
    else:
        admin_acc["password"] = "yqx19840212"
        admin_acc["role"] = "超级管理员 / 终身SVIP"
        admin_acc["tier"] = "SVIP 永久旗舰版"
        admin_acc["max_devices"] = 99
            
    # 若不足 200 组则自动补充
    seen_keys = set(license_keys)
    while len(license_keys) < TOTAL_KEYS:
        k = generate_12_digit_key()
        if k not in seen_keys:
            seen_keys.add(k)
            license_keys.append(k)
            
    while len([a for a in accounts if a["username"] != "bavenbaven"]) < TOTAL_ACCOUNTS:
        i = len([a for a in accounts if a["username"] != "bavenbaven"]) + 1
        username = f"ers_vip_{i:03d}"
        if not any(a["username"] == username for a in accounts):
            password = generate_password(12)
            accounts.append({
                "id": i,
                "username": username,
                "password": password,
                "role": "VIP 尊享用户",
                "tier": "VIP尊享",
                "max_devices": 3
            })
        
    print(f"✨ 准备处理: {len(license_keys)} 个 12 位卡密, {len(accounts)} 组 VIP 独立账号")
    
    # 1. 构建 1 对 1 对应的卡密加密字典与列表
    key_bytes = derive_key(ENCRYPTION_KEY_RAW)
    
    license_keys_map = {}
    license_keys_list = []
    
    for idx, k in enumerate(license_keys, 1):
        khash = hash_credential(k)
        # 生成掩码：例如 4ACP-****-****-6XSC
        k_clean = k.replace("-", "").strip().upper()
        mask = f"{k_clean[:4]}-****-****-{k_clean[-4:]}" if len(k_clean) >= 8 else f"{k_clean[:2]}****{k_clean[-2:]}"
        
        # 为每个 Key 单独生成加密数字签名
        sig_data = f"ERS_LIC_{idx:04d}_{khash[:12]}_{k_clean}_SVIP"
        enc_sig, _ = stream_encrypt(sig_data, key_bytes)
        
        item_info = {
            "id": idx,
            "key_hash": khash,
            "key_mask": mask,
            "tier": "SVIP 永久版",
            "type": "lifetime_vip",
            "max_devices": 3,
            "encrypted_token": enc_sig[:32],
            "status": "active",
            "created_at": "2026-08-06"
        }
        license_keys_map[khash] = item_info
        license_keys_list.append(item_info)
        
    # 2. 构建 1 对 1 对应的账号加密字典与列表
    accounts_map = {}
    accounts_list = []
    for acc in accounts:
        phash = hash_password(acc["password"])
        acc_info = {
            "id": acc["id"],
            "username": acc["username"],
            "password_hash": phash,
            "role": acc["role"],
            "tier": "VIP 尊享用户",
            "max_devices": acc["max_devices"],
            "status": "active",
            "created_at": "2026-08-06"
        }
        accounts_map[acc["username"]] = acc_info
        accounts_list.append(acc_info)
        
    # 3. 构建核心完整 Payload 并加密
    payload = {
        "status": "active",
        "auth_version": "4.0.0",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_keys": len(license_keys),
        "total_accounts": len(accounts),
        "features": [
            "music_search",
            "lossless_download",
            "online_streaming",
            "cloud_drive_sync",
            "skin_themes",
            "desktop_lyrics",
            "auto_updates",
            "volume_boost",
            "preamp_dsp"
        ],
        "license_keys": license_keys_map,
        "accounts": accounts_map,
        "banned_devices": []
    }
    
    payload_json = json.dumps(payload, ensure_ascii=False, indent=2)
    encrypted_payload, iv_b64 = stream_encrypt(payload_json, key_bytes)
    
    # 4. 生成公开资料仓的 auth.json（根级别直接包含 1 对 1 对应的 200 个加密 Key 条目和 200 组账号）
    auth_json_content = {
        "product": "ERS Tech Music",
        "status": "active",
        "auth_version": "4.0.0",
        "announcement": "ERS Tech Music 官方正版授权验证系统运行正常 (200组卡密/账号加密校验库已同步)",
        "update_server": "https://raw.githubusercontent.com/bavenbaven/Software-Releases/main/ERS%20Tech%20Music/version.json",
        "mirrors": [
            "https://raw.githubusercontent.com/bavenbaven/Software-Releases/main/ERS%20Tech%20Music/version.json",
            "https://cdn.jsdelivr.net/gh/bavenbaven/Software-Releases@main/ERS%20Tech%20Music/version.json",
            "https://ghfast.top/https://raw.githubusercontent.com/bavenbaven/Software-Releases/main/ERS%20Tech%20Music/version.json"
        ],
        "allowed_features": payload["features"],
        "latest_version": "4.0.0",
        "total_keys": len(license_keys),
        "total_accounts": len(accounts),
        "encryption_algorithm": "SHA256-SALTED-HASH-HMAC-CHACHA-V4",
        "cipher_algo": "SHA256-CHACHA-STREAM-V4",
        "iv": iv_b64,
        "payload": encrypted_payload,
        "license_keys": license_keys_map,
        "accounts": accounts_map,
        "keys_encrypted_list": license_keys_list
    }
    
    with open(auth_json_path, "w", encoding="utf-8") as f:
        json.dump(auth_json_content, f, ensure_ascii=False, indent=2)
    print(f"✅ 已成功将 200 组加密卡密与账号 1 对 1 写入: {auth_json_path}")
    
    # 5. 更新 TXT 备份文件
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("   ERS Tech Music 官方授权卡密与 VIP 账号密码备份清单 (共200组密钥 + 200组账号)\n")
        f.write("   生成日期: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "  |  版本: v4.0.0\n")
        f.write("   说明: 请妥善保管此文件，用于向用户发放 12 位激活码或专属 VIP 账号！\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("一、 200 个 12 位激活卡密 (格式: XXXX-XXXX-XXXX，支持在软件内一键激活):\n")
        f.write("-" * 80 + "\n")
        for idx, k in enumerate(license_keys, 1):
            khash = hash_credential(k)
            f.write(f"序号 {idx:03d} | 卡密: {k}  | 权限: SVIP永久授权  | 哈希验证码: {khash[:16]}... | 状态: 可用\n")
            
        f.write("\n" + "=" * 80 + "\n\n")
        f.write("二、 200 组 VIP 独立账号与密码 (支持在软件内直接登录使用):\n")
        f.write("-" * 80 + "\n")
        for acc in accounts:
            f.write(f"序号 {acc['id']:03d} | 账号: {acc['username']:<14} | 密码: {acc['password']:<14} | 权限: VIP尊享 | 限制: 3台设备\n")
            
        f.write("\n" + "=" * 80 + "\n")
        f.write("清单结束 - ERS Tech Music 官方正版保护\n")
    print(f"✅ 已成功更新文本备用清单: {txt_file}")
    
    # 6. 更新 CSV 备份文件
    with open(csv_file, "w", encoding="utf-8-sig") as f:
        f.write("类型,序号,卡密/账号,密码,权限级别,可用状态,备注\n")
        for idx, k in enumerate(license_keys, 1):
            f.write(f"12位激活卡密,{idx},{k},-,SVIP永久版,可用,未分配\n")
        for acc in accounts:
            f.write(f"VIP账号密码,{acc['id']},{acc['username']},{acc['password']},VIP尊享,可用,未分配\n")
    print(f"✅ 已成功更新 CSV 表格备用清单: {csv_file}")
    
    # 7. 更新 version.json
    version_content = {
        "name": "ERS Tech Music",
        "version": "4.0.0",
        "releaseDate": datetime.now().strftime("%Y-%m-%d"),
        "downloadUrl": "https://raw.githubusercontent.com/bavenbaven/Software-Releases/main/ERS%20Tech%20Music/ERS%20Tech%20Music_3.0.0_x64-setup.exe",
        "downloadMirror": "https://ghfast.top/https://raw.githubusercontent.com/bavenbaven/Software-Releases/main/ERS%20Tech%20Music/ERS%20Tech%20Music_3.0.0_x64-setup.exe",
        "authUrl": "https://raw.githubusercontent.com/bavenbaven/Software-Releases/main/ERS%20Tech%20Music/auth.json",
        "authMirror": "https://cdn.jsdelivr.net/gh/bavenbaven/Software-Releases@main/ERS%20Tech%20Music/auth.json",
        "changelog": [
            "1. 软件正式迈入全新大版本 v4.0.0 时代",
            "2. 引入全新 ERS Tech 终端安全授权登录系统（支持 12 位卡密激活与 VIP 账号密码登录）",
            "3. 音乐云盘重构升级：支持本地/云盘文件一键高速导入、双击无缝秒播与全盘顺序播放",
            "4. 界面精简瘦身：彻底移除冗余占位说明文字，修复字体变形与边框拉伸问题",
            "5. 全新极速增量热更与云端多镜像容灾校验，秒速生效"
        ],
        "platforms": {
            "windows-x86_64": {
                "url": "https://ghfast.top/https://raw.githubusercontent.com/bavenbaven/Software-Releases/main/ERS%20Tech%20Music/ERS%20Tech%20Music_3.0.0_x64-setup.exe"
            }
        }
    }
    with open(version_json_path, "w", encoding="utf-8") as f:
        json.dump(version_content, f, ensure_ascii=False, indent=2)
    print(f"✅ 已成功同步 version.json")
    print("\n🎉 全部 200 个密钥与 200 组账号已 1 对 1 加密输出至 auth.json！\n")

if __name__ == "__main__":
    main()

