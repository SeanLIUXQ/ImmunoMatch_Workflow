# ImmunoMatch 轻量级论文 Workflow 复现

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)
![Workflow](https://img.shields.io/badge/Workflow-Lightweight%20Reproduction-green)
![Model](https://img.shields.io/badge/Model-ImmunoMatch-orange)

**基于官方 ImmunoMatch 公开模型与示例数据的轻量级、可运行、可复现 workflow**

[English](README.en.md) | [原论文信息](docs/original-paper.md) | [快速开始](#快速开始)

</div>

---

## 项目简介

本项目是对 ImmunoMatch 论文公开 workflow 的轻量级复现。目标不是重训原始模型，也不是复现全量原始数据分析，而是在普通本地环境中打通论文核心逻辑：

- 使用单细胞观测到的 VH/VL 配对作为正样本。
- 按论文思想通过打乱 light-chain partner 构造 pseudo-negative。
- 使用作者公开的 ImmunoMatch kappa/lambda checkpoints 进行推理。
- 计算 AUC-ROC、accuracy、confusion matrix 和 score distribution。
- 输出可编辑 SVG 图、PNG 预览图和结果表。

当前 workflow 已在本地验证通过，适合作为教学、方法复现、项目模板或后续扩展的起点。

## 原论文

**论文地址：** https://doi.org/10.1038/s41592-025-02913-x

**论文引用：**

Guo, D., Dunn-Walters, D.K., Fraternali, F. et al. ImmunoMatch learns and predicts cognate pairing of heavy and light immunoglobulin chains. *Nature Methods* 23, 106-117 (2026). https://doi.org/10.1038/s41592-025-02913-x

**原始论文文件说明：**

- 本仓库不重新分发出版商 PDF。
- 原论文信息整理在 `docs/original-paper.md`。
- 如需 PDF，请通过 Nature Methods 官方页面、机构订阅或 DOI 页面获取。

## 与原论文的关系

| 模块 | 原论文 workflow | 本项目轻量复现 |
|---|---|---|
| 数据来源 | 大规模单细胞 BCR paired VH/VL 数据 | 官方 GitHub 示例数据 `King_Tonsil_GC_paired.csv` |
| 正样本 | 同一单细胞中观测到的 VH/VL 配对 | 保留示例数据中的 observed pairs |
| 负样本 | 随机打乱 light-chain partner 构造 pseudo-negative | 同样采用 VL shuffle 构造 balanced pseudo-negative |
| 模型 | AntiBERTa2 fine-tuned ImmunoMatch | 使用作者公开的 kappa/lambda ImmunoMatch checkpoints |
| 训练 | 论文作者完成的模型训练 | 不重训，直接使用公开预训练模型 |
| 推理 | 对 VH/VL pair 输出 pairing score | 本地加载 checkpoint 输出 `pairing_scores` |
| 评估 | AUC-ROC、accuracy、confusion matrix、外部验证等 | AUC-ROC、accuracy@0.5、confusion matrix、score distribution |
| 图表 | 论文完整图组 | 轻量 ROC 曲线和 score distribution 图 |

## 当前验证结果

默认轻量运行使用 24 个 observed positive 和 24 个 pseudo-negative。

| 指标 | 当前结果 |
|---|---:|
| Positive 数量 | 24 |
| Pseudo-negative 数量 | 24 |
| AUC-ROC | 0.7101 |
| Accuracy @ 0.5 | 0.6667 |
| Mean observed score | 0.7365 |
| Mean pseudo-negative score | 0.4678 |

Confusion matrix at threshold 0.5:

```text
[[12, 12],
 [ 4, 20]]
```

## 仓库结构

```text
.
├── README.md                              # 语言选择入口
├── README.zh-CN.md                        # 中文说明
├── README.en.md                           # English README
├── docs/
│   └── original-paper.md                  # 原论文引用与资源说明
├── download_immunomatch_assets.py         # 下载并缓存 ImmunoMatch checkpoint
├── run_immunomatch_toy.py                 # 最小 toy 推理脚本
├── run_lightweight_paper_workflow.py      # 论文级轻量 workflow 主脚本
├── run_lightweight_paper_workflow_windows.ps1
├── run_reproduction_windows.ps1
├── toy_immunomatch_input.csv
├── example_input/
│   └── King_Tonsil_GC_paired.csv          # 官方小示例数据
├── lightweight_paper_workflow/            # 已验证输出示例
│   ├── lightweight_pairs.csv
│   ├── lightweight_pairs_scored.csv
│   ├── metrics.json
│   ├── score_distribution.svg
│   ├── score_distribution.png
│   ├── roc_curve.svg
│   └── roc_curve.png
└── requirements_reproduced.txt
```

## 快速开始

### 1. 克隆仓库

```bash
git clone <your-repo-url>
cd ImmunoMatch_Workflow
```

### 2. 创建 Python 环境

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip wheel
.\.venv\Scripts\python.exe -m pip install ImmunoMatch==0.1.10 protobuf matplotlib scikit-learn
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel
python -m pip install ImmunoMatch==0.1.10 protobuf matplotlib scikit-learn
```

### 3. 下载模型权重

默认使用 Hugging Face 镜像，避免直连超时。模型权重约 1.6 GB，不建议提交到 GitHub。

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe download_immunomatch_assets.py --endpoint https://hf-mirror.com --model-root models --cache-dir .hf_cache
```

Linux/macOS:

```bash
python download_immunomatch_assets.py --endpoint https://hf-mirror.com --model-root models --cache-dir .hf_cache
```

如网络可直连 Hugging Face，也可以使用：

```bash
python download_immunomatch_assets.py --endpoint https://huggingface.co --model-root models --cache-dir .hf_cache
```

### 4. 运行轻量论文 workflow

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe run_lightweight_paper_workflow.py --model-root models --output-dir lightweight_paper_workflow --n-pairs 24
```

Linux/macOS:

```bash
python run_lightweight_paper_workflow.py --model-root models --output-dir lightweight_paper_workflow --n-pairs 24
```

默认输入数据为本仓库内置的 `example_input/King_Tonsil_GC_paired.csv`。如果要换自己的 paired VH/VL CSV，可额外传入 `--input your_file.csv`。

### 5. Windows 一键运行

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File run_lightweight_paper_workflow_windows.ps1
```

## 输出文件

运行后会生成：

- `lightweight_paper_workflow/lightweight_pairs.csv`
- `lightweight_paper_workflow/lightweight_pairs_scored.csv`
- `lightweight_paper_workflow/metrics.json`
- `lightweight_paper_workflow/score_distribution.svg`
- `lightweight_paper_workflow/score_distribution.png`
- `lightweight_paper_workflow/roc_curve.svg`
- `lightweight_paper_workflow/roc_curve.png`

## 常见问题

### 是否需要训练？

不需要。本项目使用作者公开的预训练 ImmunoMatch checkpoints。公开仓库中没有完整训练 pipeline，因此本项目不伪造训练过程。

### 为什么不上传 `models/`？

两个 checkpoint 权重合计约 1.6 GB，而且模型许可证来自原作者。建议运行 `download_immunomatch_assets.py` 自行下载。

### GitHub clone 或 Hugging Face 下载失败怎么办？

本项目已支持：

- GitHub 源码 zip archive 获取方式。
- `hf-mirror.com` endpoint。
- 大权重断点续传。

### 能否扩大样本量？

可以调整 `--n-pairs`，例如：

```bash
python run_lightweight_paper_workflow.py --model-root models --output-dir lightweight_paper_workflow_n100 --n-pairs 100
```

CPU 环境下会变慢；GPU 可由 PyTorch/Transformers 自动使用。

## 许可证与致谢

本项目代码用于方法复现和教学演示。ImmunoMatch 原始模型、名称、论文和相关资源归原作者所有。请遵守 ImmunoMatch 模型页面和原论文相关许可证要求。官方 README 中说明模型使用 CC-BY-NC-4.0 许可证。

如果使用本项目或 ImmunoMatch 模型，请引用原论文：

```bibtex
@article{guo2026immunomatch,
  title = {ImmunoMatch learns and predicts cognate pairing of heavy and light immunoglobulin chains},
  author = {Guo, D. and Dunn-Walters, D. K. and Fraternali, F. and others},
  journal = {Nature Methods},
  volume = {23},
  pages = {106--117},
  year = {2026},
  doi = {10.1038/s41592-025-02913-x}
}
```
