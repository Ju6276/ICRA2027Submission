图2输入素材

将真实小图保存为以下 PNG 文件，运行 `python3 figures/draw_fig02_architecture.py` 后会自动嵌入 SVG、PDF 和预览图。缺少素材时显示多视角占位框、示意力曲线或状态图标。

- `fig02_multiview.png`：参考查询时刻的机器人多视角图像，可先拼成一张图。
- `fig02_force_history.png`：当前修正时刻的力历史曲线；教师监督和学生输入区域共用此图。
- `fig02_state.png`：当前机器人状态的可视化；两个面板共用此图。

素材按原始宽高比完整放入区域，不裁剪。指令保留文本输入，任务上下文保留 token 表示。
