当然可以！以下是一份专为 **Windows 11 + Git 初学者** 设计的 **SSH 故障排查清单（Troubleshooting Checklist）**。当你遇到 `git push` 失败、`ssh -T git@github.com` 报错等问题时，按顺序逐项检查，90% 的 SSH 问题都能快速解决。

------

## 🛠️ SSH 故障排查清单（Git + GitHub 场景）

> 💡 建议：在 **PowerShell** 中逐条执行命令验证

------

### ✅ 第 1 步：确认你用的是 **SSH 地址**，不是 HTTPS

- ❌ 错误地址：`https://github.com/user/repo.git`
- ✅ 正确地址：`git@github.com:user/repo.git`

**检查命令**：

```powershell
git remote -v
```

如果显示 `https://...`，请改为 SSH：

```
git remote set-url origin git@github.com:你的用户名/仓库名.git
```

------

### ✅ 第 2 步：确认 `.ssh` 目录和密钥存在

```powershell
ls ~/.ssh
```

✅ 应看到至少两个文件：

- `id_ed25519`（私钥）
- `id_ed25519.pub`（公钥）

⚠️ 如果没有：

- 运行你之前的 `setup-git-ssh.ps1` 脚本
- 或手动执行：`ssh-keygen -t ed25519 -C "邮箱"`

------

### ✅ 第 3 步：确认公钥已正确添加到 GitHub

1. 复制当前公钥：

   ```powershell
   Get-Content ~/.ssh/id_ed25519.pub
   ```

2. 对比 GitHub → Settings → SSH keys 中的内容
   → 必须**完全一致**（包括 `ssh-ed25519` 开头和末尾的邮箱）

❌ 常见错误：

- 只复制了中间部分（漏了开头/结尾）
- 多复制了空格或换行
- 用了 `id_rsa.pub` 但 GitHub 存的是 `id_ed25519.pub`

------

### ✅ 第 4 步：测试 SSH 连接（关键！）

```powershell
ssh -T git@github.com
```

#### 🟢 成功响应：

text

```text
Hi your-username! You've successfully authenticated...
```

→ 说明 SSH 完全正常！

#### 🔴 常见错误及解决：

| 错误信息                                               | 原因                           | 解决方案                                                  |
| ------------------------------------------------------ | ------------------------------ | --------------------------------------------------------- |
| `Permission denied (publickey)`                        | 公钥未正确配置                 | 1. 检查第 3 步 2. 确保私钥在 `~/.ssh/` 3. 重启 PowerShell |
| `Could not resolve hostname github.com`                | 网络/DNS 问题                  | 检查网络，或尝试 `ping github.com`                        |
| `sign_and_send_pubkey: signing failed for ED25519 ...` | 私钥权限问题（罕见于 Windows） | 重新生成密钥，避免使用第三方工具加密                      |

------

### ✅ 第 5 步：检查 SSH 配置文件（如有）

如果你创建过 `~/.ssh/config`，检查语法是否正确：

```powershell
notepad ~/.ssh/config
```

✅ 正确示例：

config

```config
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
```

❌ 错误示例：

- 缩进用 Tab（应使用空格）
- 路径写错（如 `/Users/...` 是 macOS 写法，Windows 用 `~/.ssh/`）

> 💡 初学建议：**先不要用 config 文件**，用默认密钥即可。

------

### ✅ 第 6 步：确认 Git 使用的是系统 SSH（而非内置）

某些 Git 安装会自带 SSH 客户端，可能不读取你的密钥。

**检查 Git 使用的 SSH**：

```powershell
git config --global core.sshCommand
```

- 如果返回空值 ✅ 正常（使用系统 OpenSSH）

- 如果返回路径，可重置：

  ```powershell
  git config --global --unset core.sshCommand
  ```

> 📌 Windows 11 默认已内置 OpenSSH 客户端（无需额外安装）

------

### ✅ 第 7 步：重启终端 & 清除缓存

有时旧会话会缓存失败状态：

1. 关闭所有 PowerShell / CMD / VS Code
2. 重新打开终端
3. 再次运行 `ssh -T git@github.com`

------

### ✅ 第 8 步：防火墙 / 企业网络限制（特殊场景）

- 公司/学校网络可能屏蔽 SSH（端口 22）
- 尝试用手机热点测试
- 或改用 HTTPS + Personal Access Token（临时方案）

------

## 🧪 附：一键诊断脚本（可选）

你可以将以下命令保存为 `ssh-diag.ps1` 快速收集信息：



```powershell
Write-Host "=== SSH 诊断报告 ===" -ForegroundColor Cyan
Write-Host "1. Git remote 地址:"
git remote -v
Write-Host "`n2. .ssh 目录内容:"
ls ~/.ssh
Write-Host "`n3. 测试连接 (等待几秒):"
ssh -T git@github.com 2>&1
Write-Host "`n4. Git SSH 配置:"
git config --global core.sshCommand
```

------

## ✅ 最后建议

- **不要频繁生成新密钥** → 会导致 GitHub 上密钥堆积
- **私钥 = 身份凭证** → 切勿上传到 GitHub 或发给别人
- **成功后，把 `ssh -T git@github.com` 加入你的日常检查习惯**

------

需要我为你生成一份 **PDF 版本的排查清单**，或者一个 **VS Code 任务（tasks.json）自动运行诊断** 吗？这样你可以一键检测环境！