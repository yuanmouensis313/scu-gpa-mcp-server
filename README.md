# 四川大学绩点计算MCP服务器
基于Model Context Protocol(MCP)实现的四川大学本科生绩点核算服务，严格遵循川大2017秋起十二级绩点官方标准。

## 功能特性
- ✅ 百分制成绩转绩点（严格遵循川大官方对照表）
- ✅ 十二级字母等级制成绩转绩点
- ✅ 五级中文等级制成绩兼容
- ✅ 单门课程绩点与加权绩点计算
- ✅ 批量课程总学分/总加权绩点/平均绩点计算
- ✅ 完整的输入校验与异常处理

## 支持的等级列表
- 字母等级：A/A-/B+/B/B-/C+/C/C-/D+/D/F
- 中文等级：优秀/良好/中等/及格/不及格

## 使用方式
### 1. 在HelloAgents框架中使用
```python
from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import MCPTool

agent = SimpleAgent(name="川大绩点助手", llm=HelloAgentsLLM())
# 添加MCP工具
gpa_tool = MCPTool(
    server_command=["python", "server.py"]
)
agent.add_tool(gpa_tool)

# 调用计算
response = agent.run("帮我计算高等数学，学分4，成绩88分的绩点")
print(response)