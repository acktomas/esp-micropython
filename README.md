# Git

## **必须掌握的6个命令（按使用顺序）**

| 命令                           | 作用                             | 使用场景                                             |
| ------------------------------ | -------------------------------- | ---------------------------------------------------- |
| `git init`、`git init -b main` | 在本地新建一个 Git 仓库          | 开始管理一个新项目或笔记文件夹                       |
| `git clone <网址>`             | 把 GitHub 上别人的项目下载到本地 | 获取优质开源资源（如学习模板、代码示例）             |
| `git add .`                    | 把修改的文件“暂存”起来准备提交   | 写完代码或笔记后，准备保存                           |
| `git commit -m "说明文字"`     | 正式保存一次更改                 | 每完成一个小功能或修改就提交一次                     |
| `git push`                     | 把本地提交上传到 GitHub          | 备份到云端，防止丢失`git push -u origin main`        |
| `git pull`                     | 从 GitHub 拉取最新内容           | 别人更新了项目（或你自己在另一台电脑改了），同步回来 |

### 命令：`git branch -M main`

这个命令其实是两个操作的缩写：

| 部分         | 含义                                                         |
| ------------ | ------------------------------------------------------------ |
| `git branch` | 管理分支的命令                                               |
| `-M`         | 是 `-m`（move/rename） + 强制（force）的组合，意思是“**重命名当前分支为……，即使名字冲突也强制改**” |
| `main`       | 新的分支名                                                   |

所以整句话的意思是：

> **“把当前所在的分支，强制改名为 `main`。”**

`git branch --set-upstream-to=origin/main main`
## git config 推荐设置



```
git config --global user.name "YourRealName"
git config --global user.email "your_email@example.com"  # GitHub 建议用 noreply 邮箱
```



```
git config --global credential.helper wincred
git config --global credential.helper store
git config --global init.defaultBranch main
git config --global alias.lg "log --oneline --graph --all"
git config --global --list
```

```
# 副本 A：用 HTTPS
git clone https://github.com/acktomas/repo.git repo-https

# 副本 B：用 SSH
git clone git@github.com:acktomas/repo.git repo-ssh
```
## 📌 ： SSH 行动清单
✅ 生成密钥：`ssh-keygen -t ed25519 -C "邮箱"`
✅ 复制公钥：

| 环境                   | 复制命令                                                     |
| ---------------------- | ------------------------------------------------------------ |
| **Git Bash (Windows)** | `cat ~/.ssh/id_ed25519.pub | clip`                           |
| **PowerShell**         | `Get-Content ~/.ssh/id_ed25519.pub | Set-Clipboard`          |
| **Linux/macOS 终端**   | `xclip -sel c < ~/.ssh/id_ed25519.pub`（需安装 xclip）或手动复制 |



✅ 粘贴到` GitHub → Settings → SSH keys`
✅ 测试：`ssh -T git@github.com`
✅ 克隆时用 `git@github.com:...`
## Git pull

## 📌 最佳实践组合

| 场景                         | 推荐方案                                                     |
| ---------------------------- | ------------------------------------------------------------ |
| **拉取自己的项目**           | ✅ 从 **Gitee** `git pull gitee main`（最快最稳）             |
| **偶尔需要 GitHub 最新提交** | ✅ 网络好时手动 `git pull origin main`                        |
| **长期跟踪活跃开源项目**     | ✅ 在 Gitee 上 Fork 该项目 → 设置自动同步（Gitee 支持定时从 GitHub 拉取） |

> 💡 Gitee 自动同步设置路径：
>  仓库 →「管理」→「镜像仓库管理」→ 添加 GitHub 地址 → 设置每天同步

## Git remote

```
# 查看当前 remote（应该只有 origin → GitHub）
git remote -v

# 添加 Gitee 作为新 remote，命名为 "gitee"
git remote add gitee git@github.com:acktomas/esp-micropython.git

# 删除之前的 gitee（可选）
git remote remove gitee

# 创建新 remote "all"，包含两个推送地址
git remote add all git@github.com:acktomas/esp-micropython.git

$ git remote set-url --add --push all git@github.com:acktomas/esp-micropython.git
$ git remote set-url --add --push all git@gitee.com:acktomas/esp-micropython.git


# 现在只需：
git push all main
```

## 创建 `.gitignore`

在项目根目录新建 `.gitignore`，内容如下：


```gitignore
# VS Code
.vscode/

# Python cache
__pycache__/
*.pyc

# Serial logs
*.log

# OS files
Thumbs.db
.DS_Store
```

###  create a new repository on the command line



```
echo "# wechat_app" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main

git remote add all git@github.com:acktomas/wechat_app.git

git remote set-url --add --push all git@github.com:acktomas/wechat_app.git
git remote set-url --add --push all git@gitee.com:acktomas/wechat_app.git

git push -u all main

# 更新 all 这个默认远程仓库的地址
$ git remote set-url all git@gitee.com:acktomas/wechat_app.git

```

### …or push an existing repository from the command line



```
git remote add origin https://github.com/acktomas/wechat_app.git
git branch -M main
git push -u origin main
```
