# 这个文档记录后续的研发计划

- [x] **1. 对话管理与上下文记忆**: 为应用增加对话管理功能，可以查看和切换历史对话。在每次交互中，将当前对话的消息历史作为上下文传递给大模型，实现连续对话能力。
- [x] **2. 对话历史持久化存储**: 实现对话记录的本地持久化存储。采用简单、轻量的 JSON 文件方案，确保应用重启后历史对话不会丢失。
- [x] **3. 生成调研报告**: 支持对当前对话的所有内容（包括搜索记录）一键生成一份结构化的调研报告。报告的格式和结构将通过优化的提示词进行定义。具体的实现建议是:
    1. 我希望按钮触发调研报告生成，生成调研报告时时基于前面所有轮次gemini 搜索所返回的信息和引用网址;
    2. 严格基于当前对话的历史消息中的历史搜索结果，生成最终的调研报告和参考文献列表；
    3. 参考文献要良好的呈现，并在文中做引用。要准确实现参考文献的引用，每次的搜索记录应该被恰当的保存。请注意**参考文献的可溯源性**非常重要！
- [x] **4.对话和消息列表优化**:
    1. 优化历史对话列表，展开显示，然后历史对话列表中的每一项支持删除；
    2. 一个对话窗口中的历史消息，不管是用户的还是机器人回答的，都支持删除，删除的消息将不会再保留，后续生成调研报告时，这个消息也不会再被利用；（这是为了允许用户删除一些它觉得质量不高的回答，避免污染后续的调研报告）。
- [x] **5.优化设置入口**：支持有一个设置入口设置1.api endpoint(写一个默认的)，2.gemini api key；3.搜索模式和报告生成的提示词（设置框中显示默认的提示词）；4.模型选择，支持设置搜索用的模型和报告生成用的模型，搜索推荐时2.5 flash,报告生成推荐时2.5 pro


# 遗留bug
- [x] **调研报告的参考文献再文中的序号和末尾的参考文献对应不上**（严重）