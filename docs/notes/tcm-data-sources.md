# 中医药数据源调研报告

> 使用场景：中医辨证论治 Agent（医师辅助工具）
> 需求：教材、药典、经典条文、医案、评测集、知识图谱

---

## 一、现成开源数据集（可立即拿来用）

### 1. PanckooAI/TCM_Datasets（优先级 1）

- 链接：https://github.com/PanckooAI/TCM_Datasets
- 内容：**45 本中医国家规划教材**（十四五版本），包括中医内科学、中药学、中医方剂学、中医儿科学、中医婴产科学、针灸推拿、内科学、外科学、金匮要略等。每本 0.5–2 MB markdown，总计约 30 MB 。
- 格式：**Markdown + LaTeX 公式**，UTF-8 编码。
- 许可：MIT（但限研究与教育用途，禁止商业二次开发与传播）。
- **推荐理由**：这是你项目的高优先级资源——“十四五”版本是中医高等院校教材，容量、权威性、格式都适合你的 chunk 化 + 嵌入检索。先拿这些走通检索流水线。

### 2. TR2335/ZY-TCM-Knowledge-Graph（优先级 1）

- 链接：https://github.com/TR2335/ZY-TCM-Knowledge-Graph
- 内容：data/curated/ 提供**已结构化的安全规则 CSV**：
  - `shiba_fan.csv`（十八反，5 KB）
  - `shijiu_wei.csv`（十九畏，1.4 KB）
  - `pregnancy_contra.csv`（妊娠禁忌，5 KB）
  - `toxic_exclusion.csv`（毒性药材排除，5.5 KB）
- 许可：MIT
- **推荐理由**：你的 `safety/rules.yaml` 已有这几类规则的 v0，可以用这个项目的 CSV 作为参考去扩展。同时项目的整体架构与你的手册趋同，能看到实际项目是怎么落地的。

### 3. lin-haust/TCM-prescription-datasets（优先级 2）

- 链接：https://github.com/lin-haust/TCM-prescription-datasets
- 内容：**23 种治法 + 400+ 治法亚类 + 4174 中药材 + 900+ 经典方剂 + 21 种上下文信息特征**。是现成最全的中药处方结构化数据集。
- 格式：Python（提供处方推荐代码）。
- 许可：未明确，需检查 LICENSE。

### 4. orangeshushu/TCM-Ladder（优先级 2）

- 链接：https://github.com/orangeshushu/TCM-Ladder（NeurIPS 2025 已收录）
- 数据集：https://huggingface.co/datasets/timzzyus/TCM-Ladder
- 内容：**首个专门为 TCM LLM 设计的多模态 QA 评测集**，涵盖基础理论、诊断、方剂、内科、外科、药学、儿科。含单选、多选、填空、诊断对话、视觉理解。
- **推荐理由**：你需要评测集时，这是现成最权威的 TCM 评测套餐（含 leaderboard，在 tcmladder.com）。可以用你 Agent 在这个套餐上评测，得出可比较的指标。

### 5. KerroKapple/TCM_KnowledgeGraph（优先级 3）

- 链接：https://github.com/KerroKapple/TCM_KnowledgeGraph
- 内容：包含一个完整的 **Neo4j 图谱 schema + 实际实现**（app/src/tcm_kgraph/graph_schema.py）。可以拿来对标你的 graph/schema.cypher。
- 许可：MIT

### 6. Jane-o-O-o-O/zhongyi-graph（优先级 3）

- 链接：https://github.com/Jane-o-O-o-O/zhongyi-graph
- 内容：包含 Neo4j + Qdrant 混合检索 + RAGFlow 接入。架构参考价值高，但仓库本身没提供 TCM 原始数据集。

---

## 二、中文 NLP / 医学文本资源（需 API 或爬虦获取）

### 7. OpenKG（中文知识图谱开源社区）

- 链接：http://www.openkg.cn/
- 内容：含 TCM 专题知识图谱，数据集以 RDF/OWL 为主。是中国知识图谱领域最大的开源社区。
- 访问：部分免费，部分需提交申请。
- **推荐理由**：对你 Neo4j 图谱阶段能提供高质量决爵。推荐查“中医”、“本草”、“方剂”关键词。

### 8. SymMap（中药综合数据库）

- 链接：https://www.symmap.org/
- 内容：中药、化合物、病、目标、药理行为的综合关系数据库。
- 访问：需注册（免费）。
- 适用场景：未来要展示“中药 ↔ 现代药理”时用。MVP 不需要。

### 9. BATMAN-TCM（中药机制数据库）

- 链接：https://bionet.ncpsb.org.cn/batman-tcm/
- 内容：中药中的化学组分与其目标。同上，定位是现代生物学补充，MVP 不需要。

### 10. 中国药典 2020 版（公开发行版）

- 访问：**公开发行的 PDF 版本在多个第三方网站可获取**（习都区医药师都有电子版）。但**版权属于国家药品监督管理局**，使用需谨慎，不要直接发布原始文本。
- **推荐理由**：你需要的是药名、性味、归经、毒性、剂量区间——**事实型数据**（不受版权保护，但需要自己重新输入）。可以参考多个已有的 TCM-DB 项目的药典子集。

---

## 三、LLM 评测与训练资源

### 11. CMtMedQA（中医问答训练集）

- 链接：查找 "CMtMedQA" 或查 "ChatMed" GitHub repo
- 用途：如果你未来要 fine-tune 模型，这些是训练语料。MVP 阶段你只需评测，不需要训练，可以先不看。

### 12. TCMxPlore

- 链接：https://github.com/Insilico-org/TCMxPlore
- 用途：封装器，连接 TCMID/TCMSP/HERB 等数据库。你现阶段不需要。

---

## 四、推荐的项目实施路径

根据你的手册 Phase 0.6 要求 + 现有项目状态，推荐如下顺序：

### 阶段 1：先拿“十四五”教材走通检索管道（实验性）

从 **PanckooAI/TCM_Datasets** 下载：
- 中医内科学（最重要，覆盖最多证型）
- 中医方剂学（方剂组成与加减）
- 中药学（药性、毒性、剂量上下限）
- 金匮要略（经典条文）

处理流：
```bash
git clone https://github.com/PanckooAI/TCM_Datasets.git
# 选 4 本重点教材，复制到 data/raw/十四五教材/
# 写 markdown → chunk 脚本（按证候条目 / 方剂条目 / 药材条目 切分）
# 调 BGE-M3 生成向量入 pgvector
# 跑 run_pipeline，看诊断结果是否质量可接受
```

### 阶段 2：补齐安全规则 + 丰富药品区间

从 **TR2335/ZY-TCM-Knowledge-Graph** 复制 4 个 CSV：
- shiba_fan.csv / shijiu_wei.csv / pregnancy_contra.csv / toxic_exclusion.csv
- 覆盖到你的 safety/rules.yaml，扩展鲜覆盖中医药品
- 参考《中国药典》手动补齐未覆盖的品种

### 阶段 3：评测集

双轨走：
- 小量定制：联系中医师，从《中医内科学》教材选 30–50 个标准病例作为衡量 gold standard
- 大量评测：用 **TCM-Ladder** 作为补充评测（多选题可以量化）

### 阶段 4（不急）：知识图谱

接入 **OpenKG** 的 TCM 子集，或者参考 **KerroKapple/TCM_KnowledgeGraph** 的 graph_schema.py 作为起点，从 200 高频证候开始建图。

---

## 五、版权与合规提醒

1. **PanckooAI/TCM_Datasets** 的 MIT 许可明确限制不得商业使用，你需要在项目 README 中清楚注明。
2. **《中国药典》** 是国家药品监督管理局出版，**原始文本不要发布到公开仓库**（包括 HuggingFace/GitHub）。只提取你所需要的结构化数据字段。
3. 医案如果是真实门诊记录，需要脱敏（姓名、身份证、联系方式）后才能入库。推荐仅使用教材/社会公开的标准病例。
4. 最后，如果未来要上线成为临床辅助产品，需要医疗器械许可证（二类/三类）。

---

## 总结

你的项目 MVP 阶段不需要一下子寻找完整中医语料库。**先拿 PanckooAI/TCM_Datasets 的 4 本重点教材 + TR2335 的 4 个安全 CSV，就能走通检索流水线**。其余资源后期需要再逐步接入。
