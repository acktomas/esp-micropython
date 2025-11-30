当然可以！下面是一个专为 **Windows 11 + Git 初学者** 设计的 **PowerShell 脚本**，它能：

✅ 自动检查是否已有 SSH 密钥
 ✅ 若没有，交互式生成新的 Ed25519 密钥（带邮箱输入）
 ✅ 自动复制公钥到剪贴板
 ✅ 提示你下一步操作（如粘贴到 GitHub）
 ✅ 安全、无破坏性、适合新手运行

------

### 📜 脚本名称：`setup-git-ssh.ps1`



```powershell
# setup-git-ssh.ps1
# 一键检查/生成/配置 Git SSH 密钥（适用于 Windows 11 + GitHub）
# 作者：你的 Git 设计师
# 使用方法：在 PowerShell 中运行 .\setup-git-ssh.ps1

Write-Host "🔍 检查 SSH 配置..." -ForegroundColor Cyan

$sshDir = "$env:USERPROFILE\.ssh"
$keyPath = "$sshDir\id_ed25519"
$pubKeyPath = "$sshDir\id_ed25519.pub"

# 创建 .ssh 目录（如果不存在）
if (!(Test-Path $sshDir)) {
    Write-Host "📁 创建 ~/.ssh 目录..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $sshDir | Out-Null
}

# 检查是否已有密钥
if (Test-Path $keyPath) {
    Write-Host "✅ 已检测到现有 SSH 私钥：$keyPath" -ForegroundColor Green
    Write-Host "📄 公钥路径：$pubKeyPath" -ForegroundColor Gray

    # 自动复制公钥到剪贴板
    if (Test-Path $pubKeyPath) {
        $pubKey = Get-Content $pubKeyPath
        $pubKey | Set-Clipboard
        Write-Host "📋 公钥已自动复制到剪贴板！" -ForegroundColor Magenta
    } else {
        Write-Host "⚠️  公钥文件不存在，请检查密钥对是否完整。" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "🔑 未找到 SSH 密钥，开始生成新密钥..." -ForegroundColor Yellow

    # 获取用户邮箱（用于注释）
    $email = Read-Host "请输入你的 GitHub 邮箱（仅作标识，不会上传）"
    if ([string]::IsNullOrWhiteSpace($email)) {
        $email = "user@example.com"
        Write-Host "⚠️  未输入邮箱，使用默认值：$email" -ForegroundColor DarkYellow
    }

    # 生成密钥（不设 passphrase，适合初学者）
    Write-Host "⏳ 正在生成 Ed25519 密钥（算法更安全）..." -ForegroundColor Yellow
    ssh-keygen -t ed25519 -C "$email" -f "$keyPath" -N "" -q

    if (Test-Path $keyPath) {
        Write-Host "✅ SSH 密钥生成成功！" -ForegroundColor Green
        Write-Host "🔒 私钥保存于：$keyPath" -ForegroundColor Gray
        Write-Host "🌐 公钥保存于：$pubKeyPath" -ForegroundColor Gray

        # 复制公钥到剪贴板
        $pubKey = Get-Content $pubKeyPath
        $pubKey | Set-Clipboard
        Write-Host "📋 公钥已复制到剪贴板！" -ForegroundColor Magenta
    } else {
        Write-Host "❌ 密钥生成失败，请手动运行：ssh-keygen -t ed25519 -C 'your_email@example.com'" -ForegroundColor Red
        exit 1
    }
}

# 最终提示
Write-Host ""
Write-Host "🚀 下一步操作：" -ForegroundColor Cyan
Write-Host "1. 打开 GitHub → Settings → SSH and GPG keys" -ForegroundColor White
Write-Host "2. 点击 'New SSH key'" -ForegroundColor White
Write-Host "3. Title 填写设备名（如 'Windows 11 Laptop'）" -ForegroundColor White
Write-Host "4. Key 类型选 'Authentication Key'" -ForegroundColor White
Write-Host "5. 粘贴（Ctrl+V）——公钥已复制好！" -ForegroundColor White
Write-Host ""
Write-Host "🧪 测试连接命令（稍后可运行）：" -ForegroundColor Cyan
Write-Host "   ssh -T git@github.com" -ForegroundColor Green
```

------

### ▶️ 如何使用这个脚本？

#### 第 1 步：保存脚本

1. 打开 **记事本**
2. 复制上面全部内容
3. 另存为：`C:\git-practice\setup-git-ssh.ps1`（注意后缀是 `.ps1`）

#### 第 2 步：允许运行脚本（首次需设置）

PowerShell 默认禁止运行脚本，需临时放宽策略：

```powershell
# 以管理员身份打开 PowerShell（或普通用户也可）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

> 输入 `Y` 确认即可（安全，只影响当前用户）

#### 第 3 步：运行脚本

```powershell
cd C:\git-practice
.\setup-git-ssh.ps1
```

#### 第 4 步：按提示操作

- 如果是第一次，会提示你输入邮箱
- 脚本完成后，**公钥已自动复制到剪贴板**
- 打开 GitHub SSH 设置页，粘贴即可！

------

### 🔒 安全说明

- 脚本**不会上传任何数据**
- 私钥始终保存在你的 `C:\Users\<你>\.ssh\` 目录
- 未设置密码（passphrase），方便初学者使用（进阶时可手动加）

------

### 💡 进阶建议（以后可做）

- 给私钥加密码：运行 `ssh-keygen -p -f ~/.ssh/id_ed25519`
- 使用 `ssh-agent` 缓存密码（避免每次输 passphrase）

------

需要我再为你生成一个 **“SSH 故障排查清单”** 或 **“多账号配置模板（config 文件）”** 吗？这样你可以同时管理个人和工作项目！