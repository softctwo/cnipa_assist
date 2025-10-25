# 专利审查辅助程序技术原型

## 原型目标
验证关键技术可行性，包括：
1. 专利文档解析能力
2. 本地AI模型集成
3. 基础规则引擎
4. 用户界面框架
5. 数据存储方案

## 技术栈
- **后端**: Python 3.9+ + FastAPI
- **AI模型**: Ollama + Qwen2.5-7B
- **文档处理**: PyPDF2 + python-docx
- **数据库**: SQLite
- **前端**: React + TypeScript + Ant Design
- **桌面**: Electron

## 项目结构
```
prototype/
├── backend/                 # Python后端
│   ├── app/
│   │   ├── core/           # 核心业务逻辑
│   │   ├── api/            # API路由
│   │   ├── models/         # 数据模型
│   │   └── services/       # 业务服务
│   ├── tests/              # 测试文件
│   └── requirements.txt    # Python依赖
├── frontend/               # React前端
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── pages/          # 页面
│   │   ├── services/       # API服务
│   │   └── types/          # TypeScript类型
│   └── package.json        # 前端依赖
├── electron/               # Electron主进程
├── data/                   # 测试数据
└── docs/                   # 文档
```

## 快速开始
1. 安装依赖: `./scripts/setup.sh`
2. 启动后端: `cd backend && python main.py`
3. 启动前端: `cd frontend && npm start`
4. 启动桌面应用: `cd electron && npm start`

## 验证清单
- [ ] 文档解析功能
- [ ] AI模型调用
- [ ] 规则引擎执行
- [ ] 前后端通信
- [ ] 数据库操作
- [ ] 桌面应用打包