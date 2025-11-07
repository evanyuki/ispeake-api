"""
认证服务
处理用户认证相关的业务逻辑
"""
from typing import Optional, Dict, Any
import httpx

from app.core.security import verify_password, create_access_token
from app.services.user_service import UserService


class AuthService:
    """认证服务类"""
    
    @staticmethod
    async def validate_user(
        db, 
        username: str, 
        password: str
    ) -> Optional[Dict[str, Any]]:
        """
        验证用户凭证
        
        Args:
            db: 数据库连接
            username: 用户名
            password: 密码
        
        Returns:
            验证成功返回用户信息（包含_id），失败返回None
        """
        # 查询用户（需要密码字段）
        user = await UserService.find_one(
            db, 
            {"userName": username}, 
            include_password=True
        )
        
        if not user:
            return None
        
        # 验证密码
        if not verify_password(password, user["password"]):
            return None
        
        return user
    
    @staticmethod
    def create_token(user: Dict[str, Any]) -> str:
        """
        为用户创建JWT Token
        
        Args:
            user: 用户信息，必须包含_id和userName
        
        Returns:
            JWT Token字符串
        """
        token_data = {
            "userId": str(user["_id"]),
            "userName": user["userName"]
        }
        
        return create_access_token(token_data)
    
    @staticmethod
    async def github_oauth_login(
        db,
        code: str,
        client_id: str,
        client_secret: str
    ) -> Optional[Dict[str, Any]]:
        """
        GitHub OAuth登录
        
        Args:
            db: 数据库连接
            code: GitHub返回的授权码
            client_id: GitHub应用的Client ID
            client_secret: GitHub应用的Client Secret
        
        Returns:
            {
                "token": "jwt_token",
                "userId": "用户ID或'0'"
            }
        """
        try:
            # 1. 使用code换取access_token
            token_url = "https://github.com/login/oauth/access_token"
            token_params = {
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code
            }
            
            async with httpx.AsyncClient() as client:
                token_response = await client.post(
                    token_url,
                    params=token_params,
                    headers={"Accept": "application/json"}
                )
                token_data = token_response.json()
                
                if "access_token" not in token_data:
                    return None
                
                access_token = token_data["access_token"]
                
                # 2. 使用access_token获取GitHub用户信息
                user_url = "https://api.github.com/user"
                user_response = await client.get(
                    user_url,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/json"
                    }
                )
                github_user = user_response.json()
                
                if "id" not in github_user:
                    return None
                
                github_id = str(github_user["id"])
                
                # 3. 根据githubId查找本地用户
                user = await UserService.find_one(
                    db,
                    {"githubId": github_id}
                )
                
                # 4. 如果找到用户，生成JWT；否则返回userId为'0'
                if user:
                    token = AuthService.create_token(user)
                    return {
                        "token": token,
                        "userId": str(user["_id"])
                    }
                else:
                    return {
                        "token": "",
                        "userId": "0"
                    }
        
        except Exception as e:
            print(f"GitHub OAuth登录失败: {str(e)}")
            return None

