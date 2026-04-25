# 项目规则

> 本文件是项目的核心规则文件，每次新会话开始前必须先读取。

## 指令：提交并同步

当我说"提交并同步"时，Claude 需要：

**1. 本地 git 提交**
- 自动 stage 所有变更、写好 commit message、提交并 push

**2. 输出以下 VPS 操作命令供我执行**

```bash
cd /var/www/lifegraph
git pull
make prod-build
```
