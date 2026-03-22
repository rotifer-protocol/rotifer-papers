# 从 autoresearch 到集体进化：Karpathy 项目揭示了 AI Agent 的下一步

**作者：** Rotifer Foundation

**日期：** 2026 年 3 月

**前置知识：** 本文假设读者熟悉 AI Agent 框架（MCP、LangChain 等）和基本进化概念。Rotifer Protocol 规范详见 [Rotifer Protocol Specification](https://github.com/rotifer-protocol/rotifer-spec)。入门介绍详见 [From Skill to Gene](https://github.com/rotifer-protocol/rotifer-papers/blob/main/rotifer-gene-vs-skill.md)。

---

## 引言

Andrej Karpathy 的 [autoresearch](https://github.com/karpathy/autoresearch) 是近年来最优雅的进化计算演示之一。前提极其简单：给 AI Agent 一个真实的 LLM 训练环境，让它修改代码，训练 5 分钟，评估结果是否改善，保留或丢弃，然后重复。用户去睡觉；Agent 做实验；用户醒来看到一份实验日志和一个更好的模型。

该仓库在 2026 年 3 月发布后几天内突破 39,000 stars。开发者社区的反应是即时且强烈的——不是因为 autoresearch 自动化了超参数调优（很多工具都能做到），而是因为它展示了更根本的东西：**自然选择作用于代码，可以在无人干预的情况下产生真正的改进。**

本文探讨 autoresearch 与 [Rotifer Protocol](https://rotifer.dev)（一个面向自主软件 Agent 的开源进化框架）之间的结构性平行关系。我们认为，autoresearch 代表了一个出色的*垂直*进化计算演示，而 Rotifer Protocol 提供了将这一模式泛化到所有 Agent 能力的*水平*基础设施——关键是，使发现能够在 Agent 之间传播，而非孤立地留在个体实验中。

---

## 1. autoresearch 的极简之美

autoresearch 的力量来自化约。整个系统由三个组件构成：

| 组件 | 角色 | 编辑者 |
|------|------|--------|
| `train.py` | 可变异单元——包含完整的 GPT 模型、优化器（Muon + AdamW）和训练循环 | Agent |
| `val_bpb` | 适应度函数——验证集 bits per byte，越低越好，与词表大小无关 | 自动计算 |
| `program.md` | 宪法文档——给 Agent 的基线指令 | 人类 |

Karpathy 的关键设计决策强化了这种简洁性：

- **单文件修改。** Agent 只修改 `train.py`。架构、超参数、优化器、batch size——一切都可以改，但一切都在一个文件中。范围受限；diff 可审查。

- **固定时间预算。** 训练始终运行恰好 5 分钟的壁钟时间，无论 Agent 做了什么改动。这使实验直接可比：新架构、不同的 batch size、新颖的优化器——都在相同的时间约束下评估。

- **自包含。** 无分布式训练，无复杂配置。一个 GPU，一个文件，一个指标。

这三个设计选择揭示了进化系统的*最小可行结构*：

1. **可变异单元** — 可以改变的东西
2. **适应度函数** — 衡量改变好坏的量化标准
3. **不可变约束层** — 进化过程本身不能修改的规则

这种三元结构并非 autoresearch 独有。我们认为，它是一种普遍模式。

---

## 2. 孤立问题

autoresearch 的优雅伴随着一个结构性局限：**每个实验都是孤立的。**

每个用户 fork 仓库，在自己的 GPU 上运行实验，在自己的 `train.py` 中发现改进。如果旧金山的 Alice 在 H100 上发现某个训练技巧显著降低了 `val_bpb`，全球其他 5,000 个 fork 不会从中受益——除非 Alice 提交 PR，维护者审查并合并，其他用户再拉取更新。

这不是对 autoresearch 设计的批评。对于单用户 ML 优化工具来说，孤立是合理的简化。但它映射了 HGT 出现之前生物学中的一种模式，这种模式限制了数十亿年的进化速度：**有用的变异被锁定在个体谱系内部。**

在水平基因转移出现之前的生物进化中，每个有机体都必须独立发现每一种适应。抗生素耐药性、代谢通路、应激反应——每个谱系都在重新发明轮子。进化创新的速率受限于个体有机体的突变率。

---

## 3. 轮虫在 4000 万年前就想明白了

蛭形轮虫（*Rotifera: Bdelloidea*）是微小的淡水无脊椎动物，已有约 4000 万年完全通过无性方式繁殖。按照传统进化理论，这应该是灾难性的——无性繁殖导致 Muller 棘轮效应（有害突变不可逆积累）和对共同进化寄生虫的脆弱性（红皇后假说）。

然而，蛭形轮虫是地球上最具韧性的动物之一。它们的秘密：**水平基因转移**（HGT）。在干燥诱导的 DNA 损伤和修复过程中，轮虫将其他物种——真菌、细菌甚至植物——的遗传物质直接整合到自己的基因组中。它们表达的基因中，高达 8-10% 来自非后生动物来源，是动物界中记录到的最广泛的 HGT 案例。

轮虫 HGT 的关键特性：

- **无中央协调者** — 转移通过环境暴露发生，而非定向通信
- **适应度比例采纳** — 改善生存的基因被保留；中性或有害的获取被选择淘汰
- **跨物种转移** — 有用基因的来源无关紧要；重要的是它是否有效

结果：4000 万年的韧性、多样性和适应——没有有性繁殖，没有中央规划，没有看门人。

---

## 4. 结构性收敛

autoresearch 与 Rotifer Protocol 之间的平行关系不是设计出来的——它是*收敛的*。两个系统独立地到达了相同的进化原语，因为这些原语是任何利用选择压力进行改进的系统的最低要求：

| autoresearch | Rotifer Protocol | 共享原理 |
|-------------|-----------------|---------|
| `train.py` | Gene | 可变异单元——原子化、自包含的逻辑 |
| `val_bpb` | F(g) = (S_r × log(1+C_util) × (1+R_rob)) / (L × R_cost) | 量化适应度——选择压力 |
| `program.md` | L0 Kernel | 不可变约束——宪法层 |
| 5 分钟时间预算 | Arena | 标准化评估环境 |
| Fork | Agent | 独立进化实体 |
| 实验日志 | Gene 谱系 + 版本历史 | 进化记录 |

这种收敛验证了一个论断：**三元结构（可变异单元 + 适应度函数 + 约束层）是计算进化的普遍最小架构。**

---

## 5. 集体进化带来什么

Rotifer Protocol 用只有在进化发生在 Agent *网络*中时才会涌现的能力，扩展了单 Agent 进化循环：

### 5.1 水平逻辑迁移（HLT）

在 autoresearch 中，成功的变异留在一个 fork。在 Rotifer Protocol 中，高适应度 Gene 按其适应度分数和作者声誉比例在网络中传播。这是轮虫 HGT 的计算类比：

- Agent A 发现了完成任务的更好方法
- 该方法被封装为具有量化适应度分数的 Gene
- 其他 Agent 可以发现并采用它：`rotifer install gene-name`
- 随着更多 Agent 评估，Gene 的适应度分数不断更新

没有 PR 审核瓶颈。没有合并队列。网络以计算速度而非人类代码审查速度，将好想法路由到需要它的地方。

### 5.2 跨绑定可移植性

autoresearch 为单个 NVIDIA GPU 设计。Rotifer Protocol 将 Gene 编译为 Rotifer IR（WASM + Gene 感知约束层），通过形式化的能力协商协议，实现跨异构环境执行——云端（Supabase）、边缘、本地、Web3。在一个环境中工作的 Gene 可以在执行前自动验证与另一个环境的兼容性。

### 5.3 多维适应度

autoresearch 使用单一标量指标（`val_bpb`）。Rotifer Protocol 的适应度函数 F(g) 是一个乘法模型，包含成功率、利用率、鲁棒性、延迟和资源成本。乘法结构确保安全性或可靠性为零的 Gene 会被立即淘汰，无论其他分数如何——当 Gene 在服务真实用户的 Agent 网络中传播时，这一特性变得至关重要。

### 5.4 集体安全

当进化在隔离中发生（一个用户，一个 GPU），安全是个人关注的问题。当它在网络中发生时，就变成了系统性问题。Rotifer Protocol 通过以下方式解决：

- **V(g) 安全评分** — 独立于适应度，评估沙箱合规性、资源消耗模式和行为异常
- **WASM 沙箱隔离** — 每个 Gene 在自己的沙箱环境中执行
- **L0 不可变约束** — 即使通过自我修改也无法绕过的宪法层
- **L4 集体免疫**（未来）— 当一个 Agent 检测到恶意 Gene 时，整个网络通过广播威胁指纹获得抵抗力

---

## 6. 垂直 Demo，水平 Protocol

精确描述二者关系：autoresearch 和 Rotifer Protocol 不是竞争对手。它们在不同的抽象层面运作。

**autoresearch** 是一个*垂直演示* — 证明进化计算在特定高价值领域（ML 训练优化）有效。它的力量来自极致简洁和对单一用例的激光聚焦。它回答的问题是："AI Agent 能否自主改进 ML 训练代码？"

**Rotifer Protocol** 是一个*水平基础设施层* — 一个定义任何软件能力如何参与进化动力学的协议规范。它回答的问题是："我们能否构建基础设施，使任何 Agent 能力都能进化、竞争、传播，并被其他 Agent 安全采用？"

autoresearch 证明进化对 `train.py` 有效。Rotifer Protocol 追问：如果它对 AI Agent 能执行的每个功能都有效呢？而如果一个 Agent 的发现可以自动惠及所有其他 Agent 呢？

---

## 7. 结论：从个体实验到集体智慧

Karpathy 的 autoresearch 给开发者社区一种对计算进化的直觉感受：设定好，去睡觉，醒来后一切变得更好。这种直觉——软件可以通过选择压力自我改进——是使一切成为可能的基础洞察。

下一步是让这个过程变成集体的。不只是一个 Agent 在一夜之间改进一个训练脚本，而是一个 Agent 网络持续改进一个能力网络，最好的想法自动传播，最差的被选择淘汰。

从 autoresearch 到集体进化的路径，映射了从孤立有机体到水平基因转移的生物学路径。大自然花了数亿年。在软件中，我们可以有意识地构建这个基础设施。

这就是 Rotifer Protocol 的目标。

---

## 参考文献

1. Karpathy, A. (2026). *autoresearch*. GitHub. https://github.com/karpathy/autoresearch
2. Gladyshev, E. A., Meselson, M., & Arkhipova, I. R. (2008). Massive horizontal gene transfer in bdelloid rotifers. *Science*, 320(5880), 1210-1213.
3. Boschetti, C., et al. (2012). Biochemical diversification through foreign gene expression in bdelloid rotifers. *PLoS Genetics*, 8(11), e1003035.
4. Rotifer Foundation. (2026). *Rotifer Protocol Specification*. https://rotifer.dev/docs
5. Rotifer Foundation. (2026). *From Skill to Gene: Why AI Agents Need to Evolve*. https://rotifer.dev/blog/from-skill-to-gene

---

*Rotifer Protocol 基于 Apache 2.0 + Safety Clause 开源。网站：[rotifer.dev](https://rotifer.dev)。CLI：`npm i -g @rotifer/playground`。*
