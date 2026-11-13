# AI Literature Workflow 提示词版本一

适用插件：`ai-literature-workflow@local-literature`

安装完成后请新开一个 Codex 对话，让插件 Skills 重新加载。

推荐显式指定总控 Skill：

```text
$ai-literature-workflow:literature-workflow-orchestrator
```

如果界面无法识别 `$ai-literature-workflow:literature-workflow-orchestrator`，可以写：

```text
使用 ai-literature-workflow 插件中的 literature-workflow-orchestrator Skill。
```

## 一、首次启动提示词

```text
使用 $ai-literature-workflow:literature-workflow-orchestrator，
为下面的课题初始化一个严格执行 G0 到 G8 的文献研究项目。

项目目录：E:\研究\我的文献项目
项目名称：大模型推理效率优化研究
研究 profile：review
研究主题：大语言模型推理效率，包括量化、知识蒸馏、
稀疏注意力、推测解码和相关方法
目标成果：中文硕士论文的 Related Work 章节
时间范围：2022—2026
预计语料规模：20—40 篇核心论文
主要来源：arXiv、OpenAlex、Crossref、Semantic Scholar、
OpenReview 和正式会议论文集
Google Scholar 仅作为后备来源
中文文献：如有需要，由我手动从 CNKI 或万方导入
写作语言：中文
引用格式：先使用 BibTeX，最终格式等确定目标期刊、
会议或学校要求后再设置

必须遵守：
1. 严格按照 G0—G8 顺序执行，不能跳步。
2. 每次只推进一个门禁，完成当前阶段后停下。
3. 研究问题、纳入排除标准、主张范围和最终提交必须由我确认。
4. 不要代替我编写人工决策理由。
5. 没有进入冻结语料的论文，不得出现在正文引用中。
6. 不要编造 DOI、论文、实验结果或研究空白。
7. 当前先只执行 G0，完成 question_card.md，
   然后列出需要我确认的内容并等待。

请先检查项目和目标目录，初始化工作区，
报告当前门禁、计划和唯一下一步。
```

## 二、状态检查提示词

每次新对话或隔一段时间继续工作时，先检查状态：

```text
使用 $ai-literature-workflow:literature-workflow-orchestrator
检查 E:\研究\我的文献项目。

读取 planning/manifest.json、决策账本和当前产物，
告诉我：
1. 已通过哪些门禁；
2. 当前门禁和阻塞项；
3. 缺少哪些文件；
4. 唯一正确的下一步 Skill。

只诊断，不执行后续阶段。
```

确认状态后，再发送：

```text
执行当前门禁对应的唯一下一步。
严格遵守该阶段 Skill 的边界，完成后停止并报告产物。
```

## 三、G0：研究范围批准

检查 `planning/question_card.md` 后，如果研究问题和范围符合预期，发送：

```text
我确认当前 research question、范围、时间范围和成果形式。

批准理由：<填写你的真实理由，例如：
该问题与我的硕士论文方向一致，范围和时间跨度可支撑一篇 Related Work>

请将我的这次决定忠实记录为 scope_approval，
证据引用 planning/question_card.md。
然后验证 G0，并且只进入 G1 的检索协议设计。
```

## 四、G1：检索协议批准

检查 `search/search_protocol.md` 后，如果来源、查询词和筛选标准符合预期，发送：

```text
我确认当前检索来源、查询词、时间范围和纳入排除标准。

批准理由：<填写你的真实理由>

请记录为 search_protocol_approval，
验证 G1。随后只执行 G2 的检索、去重和初筛，
不要精读论文，不要写 Related Work。
```

## 五、G2：语料冻结

检查 `search/raw_results.csv`、`search/screening.csv` 和 `corpus/index.csv` 后发送：

```text
这是本次纳入论文的最终集合。
我确认 corpus/index.csv 中的纳入和排除决定。

批准理由：<填写你的真实理由>

请记录为 corpus_freeze，验证 G2。
随后只进入 G3，逐篇生成证据卡和 evidence_matrix.csv。
```

## 六、G3：论文精读与证据提取

```text
继续执行 G3。

只处理 corpus/index.csv 中已经冻结的论文。
每篇论文生成 corpus/notes/<paper_id>.json，
并同步 analysis/evidence_matrix.csv。

优先提取：
1. 研究问题；
2. 核心方法；
3. 数据集；
4. 基线；
5. 评价指标；
6. 主要结果；
7. 局限；
8. 论文对当前研究问题的支持范围。

只有摘要时标记 full_text_status 为 abstract-only。
不要把摘要信息当成完整实验细节。
G3 没有人工审批门禁，完成后验证并报告结果。
```

## 七、G4：质量判断与主张范围批准

检查 `analysis/quality_report.json` 后发送：

```text
我确认当前质量结论和可支持的主张范围。

批准理由：<填写你的真实理由>

请记录为 quality_scope_approval，验证 G4。
不要从单篇论文扩大成普遍性结论。
随后只进入 G5 的研究综合和空白分析。
```

重点检查：

- 数据集是否匹配目标问题；
- 基线是否充分；
- 是否存在数据泄漏；
- 指标是否合理；
- 是否报告方差和统计不确定性；
- 计算资源差异是否影响结论；
- 预印本结论是否被错误表述成同行评审共识。

## 八、G5：综述提纲和研究空白批准

检查 `analysis/gap_map.md` 和 `synthesis/review_outline.md` 后发送：

```text
我确认当前主题分类、方法演进、争议和研究空白。

批准理由：<填写你的真实理由>

请记录为 synthesis_approval，验证 G5。
随后只进入 G6，依据已批准提纲和证据矩阵起草 Related Work。
不得检索或新增论文。
```

## 九、G6：Related Work 写作

```text
执行 G6。

使用 related-work-writer Skill。
只能读取：
1. synthesis/review_outline.md；
2. analysis/evidence_matrix.csv；
3. 已批准的证据卡；
4. 人工主张范围决定。

按方法家族、问题和 trade-off 组织内容，
不要逐篇罗列论文。
每项实质事实必须使用 [@bib_key] 形式引用。
不得新增或搜索论文。
完成后验证 G6，并列出仍需人工检查的论点。
```

## 十、G7：引用和投稿格式

```text
目标 venue 为：<会议、期刊或学校格式>

使用 citation-and-venue-auditor。
生成并核对 references.bib，执行引用审计和格式检查。

要求：
1. 每个正文引用都必须同时存在于冻结语料和 BibTeX；
2. 不得编造 DOI、作者、页码或会议信息；
3. 预印本和正式发表版本必须区分；
4. 在 G7 全部通过前不要进入最终审计。
```

## 十一、G8：最终提交批准

检查 `audit/citations.json`、`audit/consistency.json`、
`audit/final_audit.json` 和最终稿后发送：

```text
我确认最终主张范围和提交内容。

批准理由：<填写你的真实理由，例如：
当前证据只支持特定任务和基准范围内的结论>

请记录为 submission_approval，验证 G8。
执行最终一致性、引用和反虚构审计。
审计通过后再生成 research-package.zip。
```

## 十二、最省事的日常提示词

```text
使用 $ai-literature-workflow:literature-workflow-orchestrator
检查当前文献项目状态。

严格按 G0—G8 门禁执行唯一下一步。
遇到人工决策门时停下等待我确认。
不要代替我生成决策理由，
不要跳过检索、证据提取、引用审计或最终审计。
```

## 十三、人工决策理由示例

`scope_approval`：

```text
该问题与我的硕士论文方向一致，范围和时间跨度能够支撑论文中的 Related Work。
```

`search_protocol_approval`：

```text
当前来源覆盖 AI 顶会、预印本和正式论文元数据，纳入排除标准能够控制语料规模。
```

`corpus_freeze`：

```text
纳入论文与我的研究问题直接相关，排除论文主要是训练优化或缺少可比推理实验。
```

`quality_scope_approval`：

```text
现有证据主要支持特定模型和基准上的效率结论，不接受扩展到所有模型和所有部署环境。
```

`synthesis_approval`：

```text
当前方法分类能够解释主要技术路线，研究空白来自已纳入证据，而不是主观猜测。
```

`submission_approval`：

```text
我确认正文、引用、图表和结论没有超出已批准的证据范围。
```

## 十四、重要提醒

- 不要在首次提示词中要求“一次完成整篇论文”。
- 不要跳过 G2 语料冻结。
- 不要把 `paper-lookup` 返回的搜索摘要直接当成精读证据。
- 不要用论文数量代替证据质量。
- 不要把预印本称为正式发表论文。
- 不要在正文中加入语料库之外的引用。
- 当前对话不会即时加载新安装的插件，安装后应新开会话。
