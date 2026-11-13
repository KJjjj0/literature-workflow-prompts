# AI Literature Workflow

一个面向 Codex、Claude Code、OpenCode 和兼容 Agent Skills 宿主的分阶段文献研究工作流。

## 核心思想

- AI 负责机械正确性、证据追溯、门禁校验和文件一致性。
- 人类负责研究范围、纳入排除标准、主张范围、最终解释和目标 venue。
- 没有冻结语料和证据卡，不进入写作。
- 没有人工主张范围批准，不进入综合与投稿。
- 没有通过引用审计和最终审计，不生成提交包。

## 支持的宿主

| 宿主 | 技能目录 | 安装方式 |
|---|---|---|
| Codex | `.codex/skills` | `.codex-plugin/plugin.json` |
| Claude Code | `.claude/skills` | `.claude-plugin/plugin.json` |
| OpenCode | `.opencode/skills` | `.opencode/opencode.json` |
| 通用 Agent Skills | `skills` | 直接复制到宿主技能目录 |

工作流在语料冻结后自动检查来源多样性、年份覆盖、标识符完整性和筛选风险；
引用完成后依次运行一致性审计、完整性审计和最终质量审计。

## 安装

Codex：

```powershell
codex plugin marketplace add KJjjj0/literature-workflow-prompts@main
codex plugin add ai-literature-workflow@literature-workflow
```

Claude Code：

```text
/plugin marketplace add KJjjj0/literature-workflow-prompts
/plugin install ai-literature-workflow@literature-workflow
```

OpenCode 全局安装：

```powershell
pwsh ./install.ps1 -Target opencode -Mode plugin
```

通用 Agent Skills 项目安装：

```powershell
pwsh ./install.ps1 -Target generic -Mode project -ProjectDir <项目目录>
```

## 调用

Codex：

```text
$ai-literature-workflow:literature-workflow-orchestrator
```

Claude Code：

```text
/ai-literature-workflow:literature-workflow-orchestrator
```

OpenCode：

```text
@literature-workflow-orchestrator
```

首次调用时提供研究主题、目标成果、时间范围、预计论文数量和主要来源。

普通门禁回复“批准”“同意”“认可”或“OK”即可，不需要重复填写理由。
只有拒绝、在多个方案中选择，或修改已经批准的范围时，才需要补充一句说明。

完整提示词见 [docs/prompt-version-1.md](docs/prompt-version-1.md)。

## 维护

根目录的 `skills/`、`references/`、`scripts/` 和 `AGENTS.md` 是规范源。

```powershell
python tools/sync_hosts.py --sync
python tools/sync_hosts.py --check
python tools/validate_distribution.py
```

各宿主树必须完整独立，不允许依赖符号链接或跨宿主路径。

## 许可证

MIT。
