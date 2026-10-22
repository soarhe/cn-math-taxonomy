# 批次B验证记录

日期：2026-10-22；数据版本 statistics-2026-10.1。

- `python3 scripts/build_statistics.py --check`：通过。
- `python3 scripts/validate.py`：通过；原有2个非统计节点无课标引用警告保留。
- `python3 scripts/verify_questions.py --file data/questions.json --report data/verification_report.json`：6185题；5628题表达式核验通过、0不一致；557题不适用或缺少自动表达式，不标成全部自动核验。
- `node tests/test_engine.js`：85通过；只更新随新增数据改变的节点/边计数断言，未放松引擎行为断言。
- `python3 tests/test_statistics_build.py`：4通过；覆盖补丁重复运行、修改前基线应用、无关记录保留、上游漂移时拒绝写入、版本文件指纹和用户决定。
- 浏览器：本地诊断 `?target=cnm_305&seed=3` 显示SVG箱线图；打开参考答案后中位数/IQR/极差判据正确显示。图中文字和端点已目视检查。
- 存档：代码采用独立数学会话键，旧键不删，首页提供导出；英语键保留。未模拟所有历史浏览器存档版本，通用迁移留待批次C。

数值自动核验和程序测试不构成教师审核或实证诊断效度验证。原盲解记录为旧题面历史材料，本次修改题目不继承其通过标记。
