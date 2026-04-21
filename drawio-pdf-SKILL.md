---
name: drawio-pdf
description: 生成高质量drawio架构图XML，用户导出SVG后自动转换为贴边裁剪的矢量PDF并插入论文
---

# 目的

为论文生成学术级架构图：生成drawio XML → 用户在draw.io桌面端导出SVG → 自动转换为贴边裁剪的矢量PDF → 插入LaTeX编译验证。

# 调用方式

```
/drawio-pdf <图表描述或章节信息>
```

# 交互流程

```
Step 1: 生成 drawio XML → 写入 figures/chN/ 目录
Step 2: 提示用户 "请在 draw.io 中打开并导出 SVG（勾选 Crop），导出后告诉我"
Step 3: [等待用户确认] → 自动执行 HTML wrapper + chromium 渲染 + pikepdf 去空白页
Step 4: 编译论文验证 → 报告结果
```

# drawio XML 生成规范

## 画布与字号（推荐范围，按图复杂度微调）

| 属性 | 简单图 | 中等图 | 复杂图 |
|------|--------|--------|--------|
| pageWidth | 900-1000 | 1000-1120 | 1120-1300 |
| pageHeight | 400-500 | 500-620 | 620-800 |
| 主模块标签 | 16-18pt | 15-16pt | 14-16pt |
| 子模块/内部块 | 14-16pt | 13-15pt | 12-14pt |
| 边标签(特征名) | 18-20pt | 16-18pt | 15-17pt |
| Stage标题 | 15-17pt | 14-16pt | 13-15pt |
| 参数标注 | 14-16pt | 13-15pt | 12-14pt |

**核心原则**: 论文中 `\includegraphics[width=\textwidth]` 时，最小文字不低于 8pt。
计算公式: 实际pt ≈ drawio字号 × (论文版心宽度cm / 画布宽度px × 28.35)

## 中西文混排字体方案

drawio 单个 cell 只能设置一个 `fontFamily`，无法像 LaTeX 那样自动按字符切换中西文字体。
解决方案：**`html=1` + `<font face="SimSun">` 包裹中文**。

### 原则

| 字符类型 | 字体 | 实现方式 |
|----------|------|----------|
| 西文/数字/符号 | Times New Roman | cell style 的 `fontFamily=Times New Roman`（默认） |
| 中文 | SimSun (宋体) | value 中用 `<font face="SimSun">中文</font>` 包裹 |

### 前置条件

- cell 的 style 必须包含 `html=1`，否则 `<font>` 标签会被当作纯文本显示为乱码
- style 中设置 `fontFamily=Times New Roman` 作为默认字体

### 写法示例

**中西混合标题** (如 "VLLiNet (第二章)")：
```xml
value="&lt;b&gt;&lt;font color=&quot;#C03C38&quot;&gt;VLLiNet&lt;/font&gt;  (&lt;font face=&quot;SimSun&quot;&gt;第二章&lt;/font&gt;)&lt;/b&gt;"
style="text;html=1;fontSize=16;fontFamily=Times New Roman;..."
```
→ "VLLiNet" 用 Times New Roman，"第二章" 用宋体

**纯中文内容** (如 "轻量化多模态道路分割方法")：
```xml
value="&lt;font face=&quot;SimSun&quot;&gt;轻量化多模态道路分割方法&lt;/font&gt;"
style="text;html=1;fontFamily=Times New Roman;..."
```

**中英夹杂列表** (如模块说明)：
```xml
value="• MobileNetV3 &lt;font face=&quot;SimSun&quot;&gt;双流编码器&lt;/font&gt;&lt;br&gt;• &lt;font face=&quot;SimSun&quot;&gt;大核瓶颈增强&lt;/font&gt; (LargeKernelBridge)"
style="text;html=1;fontFamily=Times New Roman;..."
```

**边 (edge) 标签** (如 "感知输入"、"解决")：
```xml
value="&lt;font face=&quot;SimSun&quot;&gt;&lt;b&gt;感知输入&lt;/b&gt;&lt;/font&gt;"
style="edgeStyle=orthogonalEdgeStyle;html=1;fontFamily=Times New Roman;..."
```
⚠️ 边也必须加 `html=1`，否则 HTML 标签会显示为原始文本

### 常见错误

| 错误 | 症状 | 修复 |
|------|------|------|
| 缺少 `html=1` | 显示 `<font face="SimSun">文字</font>` 原始标签 | 在 style 中加 `html=1` |
| 用 `html=0` + `<font>` | 同上 | 改为 `html=1` |
| 在 draw.io GUI 中改字体 | 整个 cell 变成同一字体 | 不要用 GUI 改字体，直接编辑 XML |

## 统一样式规范

- **字体**: 默认 `fontFamily=Times New Roman`，中文用 `<font face="SimSun">` 包裹（见上方混排方案）
- **配色方案**（与ch3保持一致）:
  - 蓝色系 `#DAE8FC/#6C8EBF` — RGB/视觉流
  - 绿色系 `#D5E8D4/#82B366` — 深度/LiDAR流
  - 紫色系 `#E1D5E7/#9673A6` — 融合模块
  - 橙色系 `#FFF2CC/#D6B656` — 桥接/增强模块
  - 红色系 `#F8CECC/#B85450` — 解码器/输出
  - 灰色系 `#F5F5F5/#666666` — 输入
  - 黑色 `#000000` — 最终输出
- **箭头**: `strokeWidth=2` 实线为主流，`strokeWidth=1.5;dashed=1` 虚线为跳连
- **边标签**: 粗体+上标格式 `<b>F<sup>name</sup></b>`，颜色与所属模块一致
- **模块形状**:
  - 编码器: trapezoid (direction=south，上窄下宽)
  - 解码器: trapezoid (direction=north，下窄上宽)
  - 融合/处理模块: rounded rectangle
  - 输入/输出: rectangle
- **参数标注**: 模块下方，粗体，颜色与模块一致

## XML 模板结构

```xml
<mxfile host="65bd71144e">
  <diagram id="DIAGRAM_ID" name="DIAGRAM_NAME">
    <mxGraphModel dx="214" dy="132" grid="1" gridSize="10" guides="1"
      tooltips="1" connect="1" arrows="1" fold="1" page="1"
      pageScale="1" pageWidth="1120" pageHeight="620" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        <!-- 节点和边 -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

# SVG → PDF 转换流程

## 技术方案（HTML wrapper + chromium + pikepdf）

**核心原理**: 不能直接用 chromium 渲染 SVG（会输出整页 A4 + 页眉），也不能用 inkscape（不支持 drawio 的 foreignObject 文字标签）。正确做法是用 HTML 包装器通过 `@page { size }` 指定精确页面尺寸，让 chromium 直接输出贴边 PDF。

```python
# 完整 Python 实现（推荐直接用此脚本）
import subprocess, re, pikepdf, os

svg_path = "INPUT.svg"  # SVG 绝对路径或相对于 $HOME 的路径
output_pdf = "OUTPUT.pdf"

# Step 1: 读取 SVG 尺寸
with open(svg_path) as f:
    content = f.read(2000)
W = int(re.search(r'width="(\d+)', content).group(1))
H = int(re.search(r'height="(\d+)', content).group(1))

# Step 2: 创建 HTML 包装器（@page size 精确匹配 SVG 像素尺寸）
html_path = os.path.expanduser("~/svg_to_pdf.html")
with open(html_path, "w") as f:
    f.write(f"""<!DOCTYPE html>
<html><head>
<style>
@page {{ margin: 0; size: {W}px {H}px; }}
body {{ margin: 0; padding: 0; }}
</style>
</head><body>
<img src="{svg_path}" width="{W}" height="{H}">
</body></html>""")

# Step 3: chromium headless 渲染（必须 cd $HOME + 相对路径输出）
raw_pdf = os.path.expanduser("~/raw_output.pdf")
subprocess.run([
    "snap", "run", "chromium", "--headless", "--no-sandbox", "--disable-gpu",
    "--print-to-pdf-no-header", f"--print-to-pdf={os.path.basename(raw_pdf)}",
    html_path
], cwd=os.path.expanduser("~"))

# Step 4: pikepdf 删除空白第2页（chromium 常生成多余空白页）
pdf = pikepdf.open(raw_pdf)
while len(pdf.pages) > 1:
    del pdf.pages[-1]
pdf.save(output_pdf)
pdf.close()

# Step 5: 清理临时文件
os.remove(html_path)
os.remove(raw_pdf)
```

## 关键注意事项

1. **绝不能直接 chromium 渲染 SVG**: 会输出 A4/Letter 整页 + 页眉日期，ghostscript 裁剪不可靠（只改元数据不改内容流）
2. **绝不能用 inkscape**: drawio SVG 使用 `<foreignObject>` 渲染文字，inkscape 不支持，文字会截断或丢失
3. **HTML `@page { size }` 是关键**: 让 chromium 按 SVG 精确像素尺寸生成页面，天然贴边
4. **snap chromium 沙箱**: 输出路径必须用相对路径，先 `cd $HOME` 再执行
5. **--print-to-pdf-no-header**: 必须加，否则有日期页眉
6. **pikepdf 删空白页**: chromium 经常在内容页后追加空白第2页，必须用 pikepdf 删除（不要用 ghostscript）
7. **清理**: 删除临时 HTML 和未处理的 raw PDF

# 文件命名规范

```
figures/chN/Fig.N-M_描述.drawio    # drawio 源文件
figures/chN/Fig.N-M_描述.svg       # 用户从 draw.io 导出
figures/chN/Fig.N-M_描述.pdf       # 最终裁剪后的 PDF（插入论文用）
```

# 完整示例

```
用户: /drawio-pdf 生成Ch4 AutoStripe的模型架构图
Claude:
  1. 读取 Ch4 素材，理解模型结构
  2. 生成 drawio XML → figures/ch4/Fig.4-1_AutoStripe_arch.drawio
  3. 输出: "请在 draw.io 中打开 Fig.4-1_AutoStripe_arch.drawio，
           检查布局后导出 SVG（勾选 Crop），导出后告诉我。"
用户: 导出了
Claude:
  4. 读取 SVG 尺寸 → 创建 HTML 包装器
  5. snap run chromium → ghostscript bbox → ghostscript crop
  6. 复制 PDF 到 figures/ch4/
  7. latexmk 编译验证
  8. 输出: "PDF 已生成（XXx YY pts, ZZ KB），编译通过。"
```
