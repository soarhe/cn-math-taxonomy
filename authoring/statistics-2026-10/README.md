# 已接受统计修订的生成源

`patch.json`是本次数据修改的规范源，保存每个修改对象的before/after和修改前hash。

```sh
python3 scripts/build_statistics.py
python3 scripts/build_statistics.py --check
python3 scripts/build_statistics_review.py
python3 tests/test_statistics_build.py
```

可对原基线或已经应用的版本运行；记录出现其他上游修改时拒绝覆盖，须先合并审阅。补丁包含新增节点、题目和按目标节点分组的出边；不删除无关科目或学段。

这不是全库历史生成链的重写。旧build_primary等脚本有固定规模断言和阶段性输出，不应直接用于当前全库；如在独立目录重建上游基线，最后应用本补丁，并执行全库校验。批次A生成器已冻结，防止新数据覆盖旧审核证据。

用户已接受S01–S07；新增和修订内容仍未经学科教师审核。正式ID保持稳定，316/317为新增，215的范围变化与题目修订详见CHANGELOG。
