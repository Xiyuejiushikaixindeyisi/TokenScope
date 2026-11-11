## 25年MAAS服务业务覆盖情况概览
### PPT 风格与内容分析
1、设计风格 (Design Style)：
商务科技风 (Corporate Tech)： 整体采用蓝、白、灰为主色调，辅以少量的橙色（用于强调重点数据）和黄色（用于高亮关键指标）。
- 扁平化 (Flat Design)： 没有复杂的立体阴影，使用简单的边框和色块区分层级。
- 模块化 (Modular)： 页面被清晰地划分为 “顶部指标区”、“中部业务矩阵区” 和 “底部基础支撑区”。
- 数据可视化： 大量使用加粗的大号数字来展示成果（如 100%, 3000+, 99.9%）。
2、内容逻辑 (Content Logic)：
- 顶部 (KPIs)： 展示核心宏观指标，如 HIS+AI 覆盖率、算力节约量、模型调用成功率。
- 中部 (Business Matrix)： 详细罗列了各个业务部门（研发、营销、采供、财经、HR、行政、法务等）的 AI 应用场景。每个场景都标注了具体的 “调用量” 和 “Token 消耗量”，体现业务落地的深度。
- 底部 (Infrastructure)： 展示了底层的 IT 热线、员工助手和数字产线等基础 AI 服务。
3、组件 (Components)：
- 卡片 (Cards)： 用于承载具体的业务场景。
- 标签 (Tags)： 如 "TOP1" 标签，用于标记该部门下最核心的项目。
- 数据标注 (Data Labels)： 红色字体标注的调用量数据。

```html
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI辅助变革项目汇报</title>
<style>
:root {
--primary-blue: #e6f7ff;
--border-blue: #1890ff;
--text-dark: #333;
--text-red: #d9363e;
--bg-gray: #f0f2f5;
--header-bg: #f9f9f9;
}body {
font-family: "Microsoft YaHei", sans-serif;
background-color: #fff;
margin: 0;
padding: 20px;
color: var(--text-dark);
}

.container {
max-width: 1200px;
margin: 0 auto;
border: 1px solid #ddd;
padding: 20px;
background: #fff;
}

/* 顶部 KPI 区域 */
.kpi-header {
display: flex;
justify-content: space-between;
margin-bottom: 20px;
gap: 15px;
}

.kpi-card {
flex: 1;
background: var(--primary-blue);
padding: 15px;
text-align: center;
border-radius: 4px;
border: 1px solid #bae7ff;
}

.kpi-card.highlight {
background: #fffbe6;
border-color: #ffe58f;
}

.kpi-title {
font-size: 14px;
color: #666;
margin-bottom: 5px;
}

.kpi-value {
font-size: 24px;
font-weight: bold;
color: var(--border-blue);
}

.kpi-card.highlight .kpi-value {
color: #d48806;
}

/* 中部业务矩阵 */
.section-title {
font-size: 18px;
font-weight: bold;
margin-bottom: 15px;
border-left: 4px solid var (--border-blue);
padding-left: 10px;
display: flex;
justify-content: space-between;
align-items: center;
}

.legend {
font-size: 12px;
color: #999;
}

.business-grid {
display: grid;
grid-template-columns: repeat(4, 1fr);
gap: 15px;
margin-bottom: 20px;
}

.business-card {
border: 1px solid #d9d9d9;
border-radius: 4px;
padding: 10px;
background: #fff;
position: relative;
}

.business-card.top-level {
border-color: var(--border-blue);
background: var(--primary-blue);
}

.card-header {
font-weight: bold;
margin-bottom: 10px;
display: flex;
align-items: center;
gap: 5px;
}

.tag-top1 {
background: #ff4d4f;
color: white;
font-size: 10px;
padding: 2px 4px;
border-radius: 2px;
}

.item-list {
list-style: none;
padding: 0;
margin: 0;
}

.item-list li {
padding: 5px 0;
border-bottom: 1px dashed #eee;
font-size: 13px;
}

.item-list li:last-child {
border-bottom: none;
}

.data-stat {
color: var(--text-red);
font-size: 12px;
margin-bottom: 8px;
font-weight: bold;
}

/* 特殊布局调整 */
.grid-3-col {
grid-template-columns: repeat (3, 1fr);
}

.grid-2-col {
grid-template-columns: repeat(2, 1fr);
}

/* 底部支撑区域 */
.bottom-section {
background: var (--primary-blue);
padding: 15px;
border-radius: 4px;
border: 1px solid #bae7ff;
}

.bottom-grid {
display: flex;
justify-content: space-between;
}

.bottom-item {
text-align: center;
flex: 1;
padding: 0 10px;
border-right: 1px solid #bae7ff;
}

.bottom-item:last-child {
border-right: none;
}

.bottom-title {
font-weight: bold;
margin-bottom: 5px;
}

.bottom-data {
color: var(--text-red);
font-size: 12px;
}

/* 模拟右侧独立模块 */
.right-side-modules {
display: flex;
gap: 15px;
margin-bottom: 20px;
}

.module-box {
flex: 1;
border: 1px solid #d9d9d9;
padding: 10px;
text-align: center;
}

    </style></head>
<body><div class="container">
<!-- 顶部 KPI -->
<div class="kpi-header">
<div class="kpi-card">
<div class="kpi-title">HIS+AI 覆盖</div>
<div class="kpi-value">100%</div>
</div>
<div class="kpi-card">
<div class="kpi-title">变革项目TOP1 场景覆盖</div>
<div class="kpi-value">60%</div>
</div>
<div class="kpi-card">
<div class="kpi-title">变革项目TOP场景 覆盖</div>
<div class="kpi-value">43%</div>
</div>
<div class="kpi-card">
<div class="kpi-title">共享模型数</div>
<div class="kpi-value">13个</div>
</div>
<div class="kpi-card highlight">
<div class="kpi-title">通过模型共享，共节约算力3000+卡<br>模型服务调用成功率: 99.9%</div>
</div>
</div>    
    <div class="section-title">
<span>AI辅助变革项目</span>
<span class="legend">已覆盖 | 未覆盖</span>
</div>
    
    <div class="business-grid">
<!-- 华为云 -->
<div class="business-card top-level">
<div class="card-header"><span class="tag-top1">TOP1</span> 华为云</div>
<div class="data-stat">调用量: 268w+, token: 799亿+</div>
<ul class="item-list">
<li>智能客服</li>
<li>AI辅助客户</li>
<li>AI辅助数据中心</li>
</ul>
</div>
        
        <div class="business-card">
<div class="card-header">算力先遣队</div>
<div class="data-stat">调用量: 25w+, token: 4亿+</div>
<ul class="item-list">
<li>写本子</li>
</ul>
</div>
        
        <div class="business-card">
<div class="card-header">终端</div>
<div class="data-stat">调用量: 1229w+, token: 448.76亿+</div>
<ul class="item-list">
<li>CBG-培训智能陪练</li>
<li>终端VOC观点运营</li>
<li>终端服务知识库搜索</li>
</ul>
</div>
        
        <div class="business-card">
<div class="card-header">鸿蒙</div>
<ul class="item-list">
<li>资源与连接-鸿蒙项目</li>
</ul>
</div>
</div>
    
    <div class="right-side-modules">
<div class="module-box">
<div class="card-header">XXXX</div>
<div class="item-list">
<li>ADN</li>
</div>
</div>
<div class="module-box">
<div class="card-header">内网LLM服务-jiyuanyi</div>
<div class="data-stat">调用量: 562.76w+, 总token: 125.89亿+</div>
</div>
<div class="module-box">
<div class="card-header">小鲁班-renwei</div>
<div class="data-stat">调用量: 596.97w+, token: 55.08亿+</div>
</div>
<div class="module-box">
<div class="card-header">个人桌面-xiaomin</div>
<div class="data-stat">调用量: 15865, token: 6570.38w+</div>
</div>
</div>
    
    <div class="business-grid">
<!-- 研发 -->
<div class="business-card top-level">
<div class="card-header"><span class="tag-top1">TOP1</span> 研发</div>
<div class="data-stat">调用量: 447+, token: 135亿+</div>
<ul class="item-list">
<li>AI辅助代码生成</li>
<li>AI辅助研发知识问答</li>
</ul>
</div>
        
        <div class="business-card top-level">
<div class="card-header"><span class="tag-top1">TOP1</span> 营销&服务</div>
<div class="data-stat">调用量: 132w+, token: 84亿+</div>
<ul class="item-list">
<li>AI辅助配置</li>
<li>AI辅助SOC答复</li>
<li>AI辅助交易履约</li>
<li><span class="tag-top1">TOP1</span> 服务知识助手</li>
<li>GTS-AI辅助低码编排</li>
<li>交付智能助手</li>
<li>GTS-mobile问题管理</li>
</ul>
</div>
        
        <div class="business-card top-level">
<div class="card-header"><span class="tag-top1">TOP1</span> 采供制</div>
<ul class="item-list">
<li>AI辅助海关政策遵从</li>
<li>AI辅助采购策略及合同智能生成</li>
<li>计划感知决策大模型</li>
<li>AI辅助质量风险拦截</li>
<li>AI辅助DFM极简设计</li>
<li>制造-iSee维修诊断</li>
</ul>
</div>
        
        <div class="business-card top-level">
<div class="card-header"><span class="tag-top1">TOP1</span> 财经</div>
<div class="data-stat">调用量: 4058, token: 1864w+</div>
<ul class="item-list">
<li>财经智能辅助规则解读(税务)</li>
<li>收付款作业文档解析及匹配</li>
</ul>
</div>
        
        <div class="business-card top-level">
<div class="card-header"><span class="tag-top1">TOP1</span> HR</div>
<div class="data-stat">调用量: 259w+, token: 100亿+</div>
<ul class="item-list">
<li>AI辅助面试</li>
<li>岗位推荐</li>
<li>AT会议纪要</li>
</ul>
</div>
        
        <div class="business-card top-level">
<div class="card-header"><span class="tag-top1">TOP1</span> 行政&办公</div>
<ul class="item-list">
<li>AI辅助差旅助手</li>
<li><span class="tag-top1">TOP1</span> Welink会议</li>
</ul>
</div>
        
        <div class="business-card top-level">
<div class="card-header"><span class="tag-top1">TOP1</span> 法务</div>
<div class="data-stat">调用量: 15w+, token: 5亿+</div>
<ul class="item-list">
<li>审计测试Agent</li>
<li>代表处稽查-风险等级评估</li>
<li>法律评审助手</li>
</ul>
</div>
</div>
    
    <div class="bottom-section">
<div class="bottom-grid">
<div class="bottom-item">
<div class="bottom-title">IT热线 (智能客服、智能质检)</div>
<div class="bottom-data">总调用量: 300w+<br>总token: 67亿+</div>
</div>
<div class="bottom-item">
<div class="bottom-title">HIS + AI 员工助手</div>
<div class="bottom-data">总调用量: 1.9亿+<br>总token: 3063亿+</div>
</div>
<div class="bottom-item">
<div class="bottom-title">数字产线</div>
<div class="bottom-data">总调用量: 545w+<br>总token: 186亿+</div>
</div>
</div>
</div></div></body>
</html>
```

## 典型的技术架构与成果汇报页（结构化对比风）
### PPT 风格与内容分析
1. 视觉风格与组件分析 (Visual Analysis)

    (1) 配色方案 (Color Palette)：
    - 主色调：华为红（#C00000 或类似深红），用于标题和强调重点。
    - 背景色：纯白（#FFFFFF），保持页面干净。
    - 辅助色：浅灰（#F2F2F2）用于背景框，深灰（#333333）用于正文。
    - 强调色：浅绿色（#E8F5E9）用于功能模块框，起到区分层级作用。

    (2) 排版布局 (Layout)：
    - 顶部导航：右上角有典型的 “总结 / 诉求 / 规划” 表格，这是华为汇报的标准格式。
    - 模块化：内容被严格限制在矩形框（Box）内，层级分明。
    - 对齐：严格的左对齐和居中对齐，利用箭头（→）展示流程。

    (3) 字体与图标：
    - 字体通常为微软雅黑（Microsoft YaHei）或黑体，加粗标题。
    - 使用简单的几何图形（矩形、圆角矩形）和箭头来代替复杂的装饰。

2. 内容结构拆解 (Content Structure)
- 标题区：25 年 MAAS 服务建设：沉淀 MAAS 服务业务流程，MAAS 服务基本能力初步构建。
- 右上角表格：25 年总结、26 年诉求、26 年规划。
- 核心流程图：模型服务生命周期管理（引入 -> 体验 -> 共享 -> 高效 & 加速 -> 运营运维）。
- 业务场景：AI 辅助配置、AI 辅助面试等。
- 技术架构图 (MAAS 服务)：
    - 在线推理：自然语言、多模态等。
    - 管理 / 路由 / 加速 / 运维：四个核心功能模块。
- 底部模型列表：内源模型（盘古）、开源模型（通义千问、DeepSeek 等）。
- 右侧文字总结：
    - 业务：5 个阶段的详细描述。
    - 产品：从 0 到 1 构建的具体成果（在线推理、模型服务管理等）。
```html
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>华为风 PPT - MAAS服务建设</title>
<style>
:root {
--huawei-red: #C00000;
--bg-gray: #F2F2F2;
--box-border: #333;
--light-green-bg: #E8F5E9;
--light-green-border: #4CAF50;
--text-main: #333;
--text-sub: #666;
}body {
font-family: "Microsoft YaHei", sans-serif;
background-color: #fff;
margin: 0;
padding: 20px;
color: var(--text-main);
display: flex;
justify-content: center;
}

/* 模拟 PPT 页面容器 */
.ppt-slide {
width: 1280px;
height: 720px;
background: white;
position: relative;
box-shadow: 0 0 10px rgba (0,0,0,0.1);
padding: 20px;
box-sizing: border-box;
display: flex;
flex-direction: column;
}

/* 标题区域 */
.header {
display: flex;
justify-content: space-between;
align-items: center;
margin-bottom: 15px;
border-bottom: 2px solid var (--huawei-red);
padding-bottom: 10px;
}

.title {
font-size: 24px;
font-weight: bold;
color: var(--huawei-red);
}

/* 右上角表格 */
.summary-table {
border-collapse: collapse;
font-size: 12px;
}
.summary-table td, .summary-table th {
border: 1px solid #999;
padding: 4px 8px;
text-align: center;
}
.summary-table th {
background-color: var (--bg-gray);
}
.highlight-cell {
background-color: var (--huawei-red);
color: white;
}

/* 主内容区域布局 */
.main-content {
display: flex;
flex: 1;
gap: 20px;
}

.left-panel {
flex: 2;
display: flex;
flex-direction: column;
gap: 15px;
}

.right-panel {
flex: 1;
font-size: 14px;
line-height: 1.6;
}

/* 通用框体样式 */
.box {
border: 1px solid var (--box-border);
padding: 10px;
position: relative;
}

.box-title {
font-weight: bold;
text-align: center;
margin-bottom: 10px;
font-size: 16px;
}

/* 流程图样式 */
.flow-container {
display: flex;
justify-content: space-between;
align-items: center;
text-align: center;
}
.flow-step {
background: var (--bg-gray);
padding: 8px 15px;
border: 1px solid #999;
flex: 1;
margin: 0 5px;
}
.arrow {
font-size: 20px;
color: #999;
}

/* 业务场景标签 */
.tags {
display: flex;
gap: 10px;
flex-wrap: wrap;
}
.tag {
border: 1px solid #999;
padding: 4px 10px;
font-size: 12px;
background: #fff;
}

/* 技术架构图 */
.tech-arch {
border: 2px solid #007bff; /* 蓝色边框区分 */
padding: 15px;
background: #fff;
}
.arch-grid {
display: grid;
grid-template-columns: 1fr 1fr 1fr;
gap: 10px;
margin-top: 10px;
}
.arch-col {
border: 1px solid #ccc;
padding: 10px;
display: flex;
flex-direction: column;
gap: 10px;
}
.arch-item {
background: var (--light-green-bg);
border: 1px solid var (--light-green-border);
padding: 8px;
text-align: center;
font-size: 13px;
}
.arch-header {
text-align: center;
font-weight: bold;
margin-bottom: 5px;
border-bottom: 1px solid #eee;
padding-bottom: 5px;
}

/* 底部模型列表 */
.model-list {
display: flex;
justify-content: space-around;
border: 1px solid #ccc;
padding: 10px;
background: var (--bg-gray);
}
.model-item {
text-align: center;
font-size: 12px;
}
.model-logo {
width: 40px;
height: 40px;
background: #ddd;
margin: 0 auto 5px;
display: flex;
align-items: center;
justify-content: center;
font-size: 10px;
color: #666;
}

/* 右侧文字样式 */
.section-title {
color: var (--huawei-red);
font-weight: bold;
font-size: 16px;
margin-top: 15px;
margin-bottom: 5px;
}
.section-title::before {
content: "➤";
margin-right: 5px;
}
.content-list {
margin: 0;
padding-left: 20px;
}
.content-list li {
margin-bottom: 5px;
}
.bold-text {
font-weight: bold;
}

    </style></head>
<body>    <div class="ppt-slide">
<!-- 头部 -->
<div class="header">
<div class="title">25年MAAS服务建设：沉淀MAAS服务业务流程，MAAS服务基本能力初步构建</div>
<table class="summary-table">
<tr>
<th class="highlight-cell">25年总结</th>
<th>26年诉求</th>
<th>26年规划</th>
</tr>
<tr>
<td>业务覆盖<br>情况</td>
<td>标杆案例<br>员工助手</td>
<td>服务建设<br>总结</td>
</tr>
<tr>
<td></td>
<td></td>
<td>典型问题</td>
</tr>
</table>
</div>
        <div class="main-content">
<!-- 左侧：图表区域 -->
<div class="left-panel">
                
                <div class="box">
<div class="box-title">MAAS服务的业务流程</div>
<div style="font-size: 14px; margin-bottom: 10px; text-align: center;">模型服务生命周期管理</div>
<div class="flow-container">
<div class="flow-step">引入</div>
<div class="arrow">➜</div>
<div class="flow-step">体验</div>
<div class="arrow">➜</div>
<div class="flow-step">共享</div>
<div class="arrow">➜</div>
<div class="flow-step">高效&加速</div>
<div class="arrow">➜</div>
<div class="flow-step">运营运维</div>
</div>
</div>
                
                <div class="tags">
<div class="tag">AI辅助配置</div>
<div class="tag">AI辅助面试</div>
<div class="tag">AI辅助规则解读</div>
<div class="tag">IT热线</div>
<div class="tag">员工助手</div>
<div class="tag">华为云客服</div>
<div class="tag">......</div>
</div>
                
                <div class="tech-arch">
<div class="box-title" style="font-size: 18px;">MAAS服务</div>
                    
                    <div style="border: 1px solid #ccc; padding: 5px; margin-bottom: 10px;">
<div style="text-align: center; font-weight: bold; margin-bottom: 5px;">在线推理</div>
<div style="display: flex; justify-content: space-around;">
<div class="arch-item" style="flex:1">自然语言类</div>
<div class="arch-item" style="flex:1">多模态类</div>
<div class="arch-item" style="flex:1">代码类</div>
<div class="arch-item" style="flex:1">向量化类</div>
</div>
</div>
                    
                    <div class="arch-grid">
<!-- 模型服务管理 -->
<div class="arch-col">
<div class="arch-header">模型服务管理</div>
<div class="arch-item">服务并发配置</div>
<div class="arch-item">服务上下架</div>
</div>
                        
                        <div class="arch-col">
<div class="arch-header">模型服务路由</div>
<div class="arch-item">变长请求</div>
<div class="arch-header" style="margin-top:10px;">模型加速</div>
<div class="arch-item">长文本</div>
<div class="arch-item">高并发</div>
<div class="arch-item">低时延</div>
</div>
                        
                        <div class="arch-col">
<div class="arch-header">运营运维</div>
<div class="arch-item">用量统计</div>
<div class="arch-item">租户配额管理</div>
</div>
</div>
</div>
                
                <div class="model-list">
<div class="model-item">
<div class="model-logo">盘古</div>
<div>内源模型</div>
</div>
<div class="model-item">
<div class="model-logo">通义千问</div>
<div>开源模型</div>
</div>
<div class="model-item">
<div class="model-logo">DeepSeek</div>
<div></div>
</div>
<div class="model-item">
<div class="model-logo">GLM 1-4</div>
<div></div>
</div>
</div>
            </div>
            
            <div class="right-panel">
<div class="section-title">业务：沉淀MAAS服务的业务流程</div>
<ul class="content-list">
<li><span class="bold-text">引入：</span>完成昇腾算力的快速适配；</li>
<li><span class="bold-text">体验：</span>面向种子用户的新模型试验场；</li>
<li><span class="bold-text">共享：</span>面向公司内部全面正式推广；</li>
<li><span class="bold-text">高效&加速：</span>基于技术驱动，让模型服务更高效；</li>
<li><span class="bold-text">运营运维：</span>保障服务的稳定可靠，数据可视；</li>
</ul>
                <div class="section-title">产品：从0到1构建了MAAS服务</div>
<ul class="content-list">
<li><span class="bold-text">在线推理：</span>推出了自然语言类、多模态类、代码类、向量化类 4类共13个基础模型；</li>
<li><span class="bold-text">模型服务管理：</span>支撑模型服务的上下架和并发配置；</li>
<li><span class="bold-text">模型服务路由：</span>变长请求通过感知请求长度，分流至最优实例处理，提升了模型服务利用率；</li>
<li><span class="bold-text">运营运维：</span>初步搭建用了统计、租户配额管理等运营能力</li>
<li><span class="bold-text">模型加速：</span>采用PD分类、融合算子等技术实现了长文本、高并发、低时延的加速效果</li>
</ul>
</div>
</div>
</div></body>
</html>
```

## 宏观战略与业务全景图页（模块化堆叠风）
### PPT 风格与内容分析
1. 视觉风格 (Visual Style)
- 配色方案：经典的 “华为红”（#D7141E）搭配深灰 / 黑（#333333）与白。红色用于强调重点、标题和核心数据，灰色用于辅助信息，白色用于背景。
排版布局：
- 模块化：页面被严格划分为几个矩形区域（挑战 1、挑战 2、价值、问题）。
    - 对齐：严格的左对齐或居中对齐，网格感强。
    - 扁平化：没有阴影、渐变或复杂的 3D 效果，所有图形都是扁平的色块。
- 字体：无衬线字体（如微软雅黑、Arial），字号层级分明（标题大、正文小、数据特大）。

2. 内容逻辑 (Content Logic)
- 标题先行：标题直接给出结论 ——“算力比预估节约 800 + 卡”。
- 对比法 (Before vs. Now)：这是核心叙事逻辑。通过 “优化前” 和 “优化后” 的数据对比（如并发 4->128，时延 109ms->81ms），直观展示成果。
- 数据量化：大量使用具体的数字（32 倍、499 卡、40%、8K->128K），拒绝模糊形容词。
- 技术术语堆叠：TP8+DP4、PD 分离、混合并行等，体现专业度。

3. 组件拆解 (Components)
- 红色标题栏：醒目的红色背景白字。
- 对比卡片：左右或上下排列的灰色 / 白色方框，中间用箭头连接。
- 流程图 / 架构图：简单的矩形框加箭头，展示数据流向或模型结构。
- 底部总结栏：通常用不同颜色的背景（如浅黄或浅红）总结 “价值” 或 “问题”。

```html
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>华为风格 PPT 模板 Skill</title>
<style>
/* 全局重置与基础设置 */
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
background-color: #f0f0f0;
font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
display: flex;
justify-content: center;
align-items: center;
min-height: 100vh;
}/* PPT 容器：模拟 16:9 比例 */
.ppt-slide {
width: 1280px;
height: 720px;
background-color: #ffffff;
box-shadow: 0 0 20px rgba (0,0,0,0.1);
padding: 40px;
display: flex;
flex-direction: column;
position: relative;
}

/* 顶部标题栏 */
.header {
margin-bottom: 30px;
}
.header h1 {
color: #D7141E; /* 华为红 */
font-size: 32px;
font-weight: bold;
margin-bottom: 10px;
}
.header .sub-info {
display: flex;
justify-content: flex-end;
font-size: 14px;
color: #666;
}
.header .sub-info span {
margin-left: 20px;
padding: 5px 10px;
border: 1px solid #ccc;
border-radius: 4px;
}
.header .sub-info span.active {
background-color: #D7141E;
color: white;
border-color: #D7141E;
}

/* 主体内容区：两列布局 */
.main-content {
display: flex;
gap: 30px;
flex: 1;
}

/* 通用卡片样式 */
.card {
flex: 1;
display: flex;
flex-direction: column;
border: 1px solid #e0e0e0;
background: #fff;
}

/* 挑战标题 */
.challenge-title {
background-color: #f9f9f9;
padding: 10px 15px;
font-size: 18px;
font-weight: bold;
color: #333;
border-bottom: 1px solid #e0e0e0;
}

/* 红色强调条 */
.highlight-bar {
background-color: #D7141E;
color: white;
padding: 8px 15px;
font-size: 16px;
font-weight: bold;
text-align: center;
}

/* 内容区域 */
.card-body {
padding: 15px;
flex: 1;
display: flex;
flex-direction: column;
gap: 15px;
}

/* 对比模块 (Before vs Now) */
.comparison-row {
display: flex;
align-items: center;
justify-content: space-between;
background: #f8f8f8;
padding: 10px;
border-radius: 4px;
}
.box {
border: 1px solid #999;
padding: 10px;
text-align: center;
width: 40%;
background: #fff;
}
.box.before { border-color: #666; }
.box.now { border-color: #D7141E; background: #fff0f0; }
.arrow { font-size: 24px; color: #D7141E; font-weight: bold; }

.tech-tags {
font-size: 12px;
color: #666;
margin-bottom: 5px;
text-align: center;
}

/* 流程图模拟 */
.flow-chart {
display: flex;
flex-direction: column;
align-items: center;
gap: 10px;
margin-top: 10px;
}
.flow-node {
border: 1px solid #333;
padding: 5px 15px;
font-size: 14px;
background: #fff;
}
.flow-arrow {font-size: 12px; color: #666;}
.flow-branch {
display: flex;
justify-content: space-around;
width: 100%;
}

/* 底部总结栏 */
.summary-bar {
margin-top: 15px;
padding: 10px;
font-size: 14px;
border: 1px dashed #D7141E;
background-color: #fff8f8;
color: #333;
}
.summary-bar strong {color: #D7141E;}

/* 问题栏 */
.issue-bar {
margin-top: auto;
background-color: #ffebee;
color: #c62828;
padding: 10px;
font-size: 14px;
display: flex;
justify-content: space-between;
border-top: 2px solid #D7141E;
}

/* 数据高亮 */
.data-highlight {
color: #D7141E;
font-weight: bold;
font-size: 1.1em;
}
</style>

</head>
<body>    <div class="ppt-slide">
<!-- 头部 -->
<div class="header">
<h1>员工助手：通过模型共享、加速、变长请求等方案，算力比预估节约800+卡</h1>
<div class="sub-info">
<span>25年总结</span>
<span class="active">26年诉求</span>
<span>26年规划</span>
</div>
</div>
        
        <div class="main-content">
            
            <div class="card">
<div class="challenge-title">挑战1：Deepseek模型需求强，但并发低、时延大、上下文不足</div>
<div class="highlight-bar">通过混合并行、PD分离等技术，并发提升32倍</div>
                <div class="card-body">
<!-- 并发对比 -->
<div class="tech-tags">混合并行 (TP8+DP4+MOE_TP8+MOE_EP4) | PD分离 (1P1D) | 融合算子</div>
<div class="comparison-row">
<div class="box before">
<div>Before</div>
<div>知识问答</div>
<div>128集群并发: 4</div>
<div>增量时延: 109ms</div>
</div>
<div class="arrow">➔</div>
<div class="box now">
<div>Now</div>
<div>知识问答</div>
<div>128集群并发: <span class="data-highlight">128</span></div>
<div>增量时延: <span class="data-highlight">81ms</span></div>
</div>
</div>
                    
                    <div class="tech-tags" style="margin-top:10px;">混合并行 (TP8+DP2+MOE_TP4+MOE_EP4) | PD分离 (2P1D) | Sequence Parallel</div>
<div class="comparison-row">
<div class="box before">
<div>Before</div>
<div>知识问答</div>
<div>上下文长度: 8K</div>
</div>
<div class="arrow">➔</div>
<div class="box now">
<div>Now</div>
<div>知识问答</div>
<div>上下文长度: <span class="data-highlight">128K</span></div>
</div>
</div>
</div>
                <div class="summary-bar">
<strong>价值：</strong>共享模型服务+加速（并发提升）是两个最基础的成本节约手段，既提升了资源利用效率，同时提升了用户体验。
</div>
                <div class="issue-bar">
<span><strong>问题：</strong>非实时场景调用在线推理服务，抢占实时并发，占比约25%</span>
<span>峰值时段0.3%请求限流</span>
</div>
</div>
            
            <div class="card">
<div class="challenge-title">挑战2：算力消耗大，单Qwen3-32B一款模型业务评估需要499卡</div>
<div class="highlight-bar">变长精确分流，节省40%算力</div>
                <div class="card-body">
<!-- 流程图 -->
<div class="flow-chart">
<div class="flow-node">员工助手</div>
<div class="flow-arrow">判断上下文</div>
<div class="flow-branch">
<div class="flow-node">Qwen3-32B-32K<br><span style="color:red">60%</span></div>
<div class="flow-node">Qwen3-32B-16K<br><span style="color:red">10%</span></div>
<div class="flow-node">Qwen3-32B-8K<br><span style="color:red">30%</span></div>
</div>
<div style="font-size:12px; color:#666;">业务调用比例 8K: 16K: 32K = 3: 1: 6，耗费499卡</div>
</div>
                    <div style="border-top: 1px dashed #ccc; margin: 10px 0;"></div>
                    <div class="flow-chart">
<div class="flow-node" style="background:#fff0f0; border-color:#D7141E;">Now</div>
<div class="flow-node" style="background:#D7141E; color:white;">Qwen3-32B</div>
<div class="flow-branch">
<div class="flow-node">8K</div>
<div class="flow-node">16K</div>
<div class="flow-node">32K</div>
<div class="flow-node">64K</div>
</div>
<div style="font-size:12px; color:#666;">自动分流比例 8K: 16K: 32K: 64K = 5: 2.4: 2.4: 0.2，<br>实际耗费<span style="color:red; font-weight:bold;">300卡</span></div>
</div>
</div>
                <div class="summary-bar">
<strong>价值：</strong>作为通用能力，简化了业务接入复杂度，全场景通用。
</div>
                <div class="issue-bar">
<span>关键大参数模型引入周期超过1个月，无法匹配助手快速创新的诉求</span>
<span>Qwen3 32B模型TPOT不满足诉求。期望≤25ms (当前35ms)</span>
</div>
</div>
        </div>
</div></body>
</html>
```