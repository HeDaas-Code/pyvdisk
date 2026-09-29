# Normify 产物归档

本分支是 [HeDaas-Code/pyvdisk](https://github.com/HeDaas-Code/pyvdisk) 的**生成产物归档分支**，只存放 Normify 编译出的架构图谱（`normify-pyvdisk/`），不含任何代码。

为什么单独成支：产物约 3.4 MB（272 个模块页、渲染图、依赖树与指纹清单），放回代码树会让每次文档同步都变成大 diff，也让仓库目录不再"读起来是代码"。归档到孤儿分支后，代码树保持干净，图谱仍可一键直达。

## 在线查看

- **[打开可交互架构图谱](https://htmlpreview.github.io/?https://github.com/HeDaas-Code/pyvdisk/blob/normify/normify-pyvdisk/normify.html)** — 单文件 `normify.html`，点击模块逐层下钻，`?lang=en` 切换英文，`#module=<id>` 深链直达。
- 逐层通读：[`normify-pyvdisk/outline.md`](normify-pyvdisk/outline.md)
- 机器可读：[`api-index.json`](normify-pyvdisk/api-index.json)、[`tree.json`](normify-pyvdisk/tree.json)、[`receipt.json`](normify-pyvdisk/receipt.json)（SHA-256 指纹与编译元数据）

## 溯源

图谱由 Normify 从仓库源码生成，每个叶子模块带仓库内真实文件路径 + 行号区间的 `source` 证据与 SHA-256 指纹，冻结于主仓库 commit `6d203c0`；`normify_validate` 结果 0 error。产物内容以 `receipt.json` 为准。

## 维护约定

- 仅在重新编译图谱时更新本分支（主仓库的日常提交不触碰这里）。
- 主仓库 README 的「架构图谱」一节索引本分支；改动索引请去主仓库。
