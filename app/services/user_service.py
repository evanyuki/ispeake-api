"""
用户服务
处理用户相关的业务逻辑
"""
from typing import Optional, List, Dict, Any
from bson import ObjectId
from datetime import datetime

from app.database import Collections
from app.core.security import hash_password


class UserService:
    """用户服务类"""
    
    @staticmethod
    async def find_all(db, exclude_password: bool = True) -> List[Dict[str, Any]]:
        """
        查询所有用户
        
        Args:
            db: 数据库连接
            exclude_password: 是否排除密码字段
        
        Returns:
            用户列表
        """
        projection = {"password": 0} if exclude_password else None
        cursor = db[Collections.USERS].find({}, projection)
        users = await cursor.to_list(length=None)
        
        # 转换ObjectId为字符串
        for user in users:
            user["_id"] = str(user["_id"])
        
        return users
    
    @staticmethod
    async def find_by_id(
        db, 
        user_id: str, 
        include_password: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        根据ID查询用户
        
        Args:
            db: 数据库连接
            user_id: 用户ID
            include_password: 是否包含密码字段
        
        Returns:
            用户信息，不存在返回None
        """
        projection = None if include_password else {"password": 0}
        
        user = await db[Collections.USERS].find_one(
            {"_id": ObjectId(user_id)},
            projection
        )
        
        if user:
            user["_id"] = str(user["_id"])
        
        return user
    
    @staticmethod
    async def find_one(
        db, 
        query: Dict[str, Any], 
        include_password: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        根据条件查询单个用户
        
        Args:
            db: 数据库连接
            query: 查询条件
            include_password: 是否包含密码字段
        
        Returns:
            用户信息，不存在返回None
        """
        projection = None if include_password else {"password": 0}
        
        user = await db[Collections.USERS].find_one(query, projection)
        
        if user:
            user["_id"] = str(user["_id"])
        
        return user
    
    @staticmethod
    async def create_one(
        db, 
        userName: str, 
        password: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建用户
        
        Args:
            db: 数据库连接
            userName: 用户名
            password: 密码，如果不提供则使用默认密码
        
        Returns:
            创建的用户信息
        """
        # 默认密码hash（原始密码为空或默认值）
        default_password_hash = "$2a$10$TVk79hQVVpmfu2BOupaIl.lw80Wlwvnpwl0oOjjLH180fi16F9p0K"
        
        user_data = {
            "userName": userName,
            "nickName": "",
            "avatar": "",
            "desc": "",
            "link": "",
            "email": "",
            "password": hash_password(password) if password else default_password_hash,
            "homePath": "/about/index",
            "status": "0",
            "speakToken": "",
            "githubId": "",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = await db[Collections.USERS].insert_one(user_data)
        
        return {
            "_id": str(result.inserted_id),
            "userName": userName
        }
    
    @staticmethod
    async def update_one(
        db, 
        user_id: str, 
        update_data: Dict[str, Any]
    ) -> Any:
        """
        更新用户信息
        
        Args:
            db: 数据库连接
            user_id: 用户ID
            update_data: 更新的数据
        
        Returns:
            更新结果
        """
        # 添加更新时间
        update_data["updatedAt"] = datetime.utcnow()
        
        result = await db[Collections.USERS].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        return {
            "acknowledged": result.acknowledged,
            "matchedCount": result.matched_count,
            "modifiedCount": result.modified_count
        }
    
    @staticmethod
    async def update_password(
        db, 
        user_id: str, 
        hashed_password: str
    ) -> Any:
        """
        更新用户密码
        
        Args:
            db: 数据库连接
            user_id: 用户ID
            hashed_password: 加密后的密码
        
        Returns:
            更新结果
        """
        result = await db[Collections.USERS].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "password": hashed_password,
                "updatedAt": datetime.utcnow()
            }}
        )
        
        return {
            "acknowledged": result.acknowledged,
            "matchedCount": result.matched_count,
            "modifiedCount": result.modified_count
        }
    
    @staticmethod
    async def count_users(db) -> int:
        """
        统计用户数量
        
        Args:
            db: 数据库连接
        
        Returns:
            用户总数
        """
        return await db[Collections.USERS].count_documents({})

