---
name: user-role-and-context
description: "User is learning gpt-image-2 text-to-image APIs through the API易 Chinese relay service, building a Python project for hands-on testing"
metadata: 
  node_type: memory
  type: user
  originSessionId: f16ddc1d-3f44-42bf-8daa-6373bda1f48a
---

# User Role & Context

用户是一名中国开发者，正在学习如何使用 OpenAI 最新发布的 **gpt-image-2** 模型（ChatGPT Images 2.0，2026年4月22日发布）进行文本转图片及其他图像/视频生成任务。

## 背景

- 因为 OpenAI 对 API Key 申请要求严苛（需海外手机号/信用卡验证），用户无法直接申请 OpenAI 官方 API Key
- 用户选择了国内中转服务 **API易 (apiyi.com)** 来解决 API 访问问题
- 用户已申请 API易 API Key 并完成配置，可成功调用 gpt-image-2 系列模型
- 用户在本项目中使用 Python 进行开发测试

## 当前状态

- 已完成核心模块封装（config.py, client.py, utils.py）
- 已编写 9 个示例脚本覆盖基础生图到高级功能
- 已成功生成 10+ 张测试图片验证各模型和参数
- 已编写 API易 完整使用指南（APIYI_完整使用指南.md）
- 未来可能扩展到视频生成功能的实际测试

## 技术偏好

- 使用 Python 3.10+ 和 openai 官方 SDK
- 偏好封装良好的模块化代码（src/ 库 + examples/ 示例 的结构）
- 重视错误处理和降级方案（如 /draw/completions 不可用时自动 fallback）
- 需要中文友好的文档和注释
