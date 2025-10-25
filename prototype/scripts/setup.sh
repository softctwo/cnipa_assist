#!/bin/bash

# 专利审查辅助程序原型环境搭建脚本

echo "🚀 开始搭建专利审查辅助程序原型环境..."

# 检查Python版本
echo "📋 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python 3.9+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python版本: $PYTHON_VERSION"

# 检查Node.js版本
echo "📋 检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo "❌ 未找到Node.js，请先安装Node.js 16+"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✅ Node.js版本: $NODE_VERSION"

# 创建Python虚拟环境
echo "🐍 创建Python虚拟环境..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虚拟环境创建成功"
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境并安装依赖
echo "📦 安装Python依赖..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Python依赖安装完成"

# 创建必要的目录
echo "📁 创建必要目录..."
mkdir -p data/uploads
mkdir -p data/models
echo "✅ 目录创建完成"

# 初始化数据库
echo "🗄️ 初始化数据库..."
python -c "
from app.core.database import init_db
init_db()
print('数据库初始化完成')
"

cd ..

# 安装前端依赖
echo "🎨 安装前端依赖..."
cd frontend
npm install
echo "✅ 前端依赖安装完成"

cd ..

# 检查Ollama是否安装
echo "🤖 检查AI模型环境..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama已安装"
    
    # 检查Ollama服务状态
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama服务正在运行"
        
        # 检查是否有可用模型
        MODELS=$(curl -s http://localhost:11434/api/tags | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    models = [m['name'] for m in data.get('models', [])]
    print(' '.join(models))
except:
    print('')
")
        
        if [ -n "$MODELS" ]; then
            echo "✅ 已安装的模型: $MODELS"
        else
            echo "⚠️  未找到已安装的模型"
            echo "💡 建议运行: ollama pull qwen2.5:7b"
        fi
    else
        echo "⚠️  Ollama服务未运行"
        echo "💡 请运行: ollama serve"
    fi
else
    echo "⚠️  未安装Ollama"
    echo "💡 请访问 https://ollama.ai 下载安装"
fi

# 创建启动脚本
echo "📝 创建启动脚本..."

# 后端启动脚本
cat > start-backend.sh << 'EOF'
#!/bin/bash
echo "🚀 启动后端服务..."
cd backend
source venv/bin/activate
python main.py
EOF

# 前端启动脚本
cat > start-frontend.sh << 'EOF'
#!/bin/bash
echo "🎨 启动前端服务..."
cd frontend
npm start
EOF

# 完整启动脚本
cat > start-all.sh << 'EOF'
#!/bin/bash
echo "🚀 启动专利审查辅助程序..."

# 检查Ollama服务
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama服务未运行，正在启动..."
    ollama serve &
    sleep 3
fi

# 启动后端
echo "🐍 启动后端服务..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!

# 等待后端启动
sleep 5

# 启动前端
echo "🎨 启动前端服务..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "✅ 服务启动完成!"
echo "📱 前端地址: http://localhost:3000"
echo "🔧 后端API: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"

# 等待用户中断
trap "echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF

chmod +x start-backend.sh start-frontend.sh start-all.sh

echo ""
echo "🎉 环境搭建完成!"
echo ""
echo "📋 下一步操作:"
echo "1. 启动完整服务: ./start-all.sh"
echo "2. 或分别启动:"
echo "   - 后端: ./start-backend.sh"
echo "   - 前端: ./start-frontend.sh"
echo ""
echo "🔗 访问地址:"
echo "   - 前端应用: http://localhost:3000"
echo "   - 后端API: http://localhost:8000"
echo "   - API文档: http://localhost:8000/docs"
echo ""
echo "🤖 AI模型建议:"
echo "   - 安装Ollama: https://ollama.ai"
echo "   - 下载模型: ollama pull qwen2.5:7b"
echo "   - 启动服务: ollama serve"
echo ""
echo "📖 更多信息请查看 README.md"