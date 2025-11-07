# KKAPI FastAPI 重构版

## 📁 项目结构

```
fastapi-migration/
├── app/
│   ├── main.py                 # 主入口
│   ├── database.py            # MongoDB连接
│   ├── core/
│   │   ├── config.py          # 配置管理
│   │   ├── security.py        # JWT、密码加密
│   │   └── dependencies.py    # 依赖注入
│   ├── models/                # 数据库模型（待实现）
│   ├── schemas/               # Pydantic模型
│   │   ├── response.py        # 响应模型
│   │   └── user.py           # 用户模型
│   ├── routers/              # 路由
│   │   ├── user.py           # 用户路由
│   │   ├── token.py          # Token路由（待实现）
│   │   ├── ispeak.py         # ISpeak路由（待实现）
│   │   ├── ispeak_tag.py     # 标签路由（待实现）
│   │   ├── post.py           # 朋友圈路由（待实现）
│   │   └── openapi.py        # 开放API路由（待实现）
│   └── services/             # 业务逻辑（待实现）
├── requirements.txt          # Python依赖
├── vercel.json              # Vercel部署配置
├── .env.example             # 环境变量示例
└── README.md                # 本文件
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd fastapi-migration
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填写你的配置
```

### 3. 本地运行

```bash
uvicorn app.main:app --reload --port 8000
```

访问：

- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

### 4. Vercel 部署

```bash
# 安装Vercel CLI
npm i -g vercel

# 登录
vercel login

# 部署
vercel

# 设置环境变量（在Vercel Dashboard或使用CLI）
vercel env add DATABASE_URL
vercel env add SECRET_KEY
# ... 其他环境变量
```

## 📝 开发进度

### ✅ 已完成

- [x] 项目结构搭建
- [x] MongoDB 连接配置
- [x] JWT 认证系统
- [x] 密码加密（bcrypt）
- [x] 统一响应模型
- [x] 用户路由骨架
- [x] Vercel 部署配置
- [x] 登录异常处理和日志系统 (2025-11-07)
- [x] 用户 Service 层完整实现
- [x] Token 管理模块
- [x] 测试脚本

### 🚧 待实现

- [ ] ISpeak 模块
- [ ] ISpeak 标签模块
- [ ] 朋友圈模块
- [ ] 开放 API 模块
- [ ] GitHub OAuth 集成
- [ ] 通知推送集成
- [ ] 单元测试覆盖
- [ ] 专业日志系统（替换 print）

## 🔑 API 端点

### 用户模块 (`/api/user`)

- `GET /api/user/` - 获取用户列表 🔒
- `GET /api/user/id` - 获取当前用户 ID 🔒
- `GET /api/user/init` - 初始化用户 🔓
- `POST /api/user/login` - 用户登录 🔓
- `GET /api/user/getUserInfo` - 获取用户信息 🔒
- `PATCH /api/user/update` - 更新用户信息 🔒
- `PATCH /api/user/password` - 修改密码 🔒
- `GET /api/user/oauth/github` - GitHub 登录 🔓

🔒 需要 JWT 认证 | 🔓 公开接口

更多 API 详见：`../API_DOCUMENTATION.md`

## 🧪 测试和调试

### 运行测试脚本

```bash
# 测试登录功能
python test_login.py
```

测试脚本会验证：

- ✅ 密码加密和验证功能
- ✅ 数据库连接
- ✅ 用户查询
- ✅ 用户认证流程

### 查看日志

启动应用后，您会看到详细的日志输出：

```
✅ 已连接到MongoDB: kkapi
📝 收到登录请求: username=admin
🔍 正在验证用户: admin
✅ 找到用户: admin, 正在验证密码...
✅ 用户验证成功: admin
✅ 用户登录成功: admin
```

### 故障排查

如果遇到登录问题，请查看 `TROUBLESHOOTING.md` 文件获取详细的排查步骤。

常见问题：

1. **数据库连接失败** - 检查 `DATABASE_URL` 配置
2. **密码验证失败** - 确认用户密码是否正确
3. **Token 无效** - 检查 `SECRET_KEY` 配置

### 手动测试 API

```bash
# 初始化用户（首次使用）
curl "http://localhost:8000/api/user/init?userName=admin"

# 登录
curl -X POST http://localhost:8000/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'

# 获取用户信息（需要token）
curl http://localhost:8000/api/user/getUserInfo \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🛠️ 技术栈

- **FastAPI** - 现代异步 Web 框架
- **Motor** - 异步 MongoDB 驱动
- **Pydantic** - 数据验证
- **python-jose** - JWT 实现
- **passlib** - 密码加密（bcrypt）
- **httpx** - 异步 HTTP 客户端

## 📦 部署注意事项

### Vercel 环境

1. **连接池优化**: 已配置适合 Serverless 的连接池大小
2. **冷启动**: 首次请求可能较慢（2-3 秒），后续请求快速
3. **超时限制**: 免费版 10 秒，Pro 版 60 秒
4. **环境变量**: 必须在 Vercel Dashboard 配置

### MongoDB Atlas

建议使用 MongoDB Atlas 的 Serverless 实例：

- 按需计费
- 自动扩缩容
- 适合间歇性流量

## 🔧 迁移指南

详细迁移步骤请参考：`../API_DOCUMENTATION.md`

### 核心差异

| NestJS                     | FastAPI                              |
| -------------------------- | ------------------------------------ |
| `@Controller()`            | `APIRouter()`                        |
| `@Get()`                   | `@router.get()`                      |
| `@UseGuards(JwtAuthGuard)` | `Depends(get_current_user)`          |
| `@NoAuth()`                | 不添加依赖                           |
| `@IsLogin()`               | `Depends(get_current_user_optional)` |
| `class-validator`          | `Pydantic`                           |

### 示例对比

**NestJS:**

```typescript
@Controller("/user")
export class UserController {
  @Get("/")
  @UseGuards(JwtAuthGuard)
  async getUserList(@Request() req) {
    return await this.userService.findAll();
  }
}
```

**FastAPI:**

```python
@router.get("/user/")
async def get_user_list(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    users = await UserService.find_all(db)
    return SuccessResponse.create(data=users)
```

## 📚 参考资料

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Motor 文档](https://motor.readthedocs.io/)
- [Vercel 部署 Python](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [原 NestJS 项目](../src/)

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📄 许可证

同原项目
