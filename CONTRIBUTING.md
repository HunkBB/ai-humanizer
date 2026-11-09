# Contributing

欢迎提出具体问题或提交改进。请说明使用场景、预期行为和实际结果，并提供不含个人信息的最小示例。

1. 修改 `academic-writing-humanizer/SKILL.md` 或对应资源；保留相对路径和文件引用。
2. 更新 Wikipedia 映射时记录固定版本、检索日期和适用情境，保留来源署名及 CC BY-SA 4.0 说明。不要把观察性特征改成作者身份判定。
3. 改动脚本时添加针对真实行为或缺陷的测试，并运行：
   ```bash
   python3 -m unittest discover -s tests -p 'test_*.py' -v
   ```
4. 对重大写作流程改动，使用公开或合成的输入做前后比较，分别检查含义保真和阅读体验。说明是自评、AI-agent 评审还是真实读者反馈。
5. 提交说明应列出改变的行为、验证结果和仍未验证的限制。

不要提交简历、申请材料、私人通信、账号凭据、真实检测报告或其他人的文稿。需要示例时使用合成材料或获得授权并移除个人信息。

Do not report invented detector percentages or imply that passing code tests proves undetectability. Keep actual author contributions and validation limits accurate.
