"""
Token服务
处理Token管理相关的业务逻辑
"""
from typing import Optional, List, Dict, Any
from bson import ObjectId
from datetime import datetime

from app.database import Collections


class TokenService:
    """Token服务类"""
    
    @staticmethod
    async def get_all(db, user_id: str) -> List[Dict[str, Any]]:
        """
        获取用户的所有Token
        
        Args:
            db: 数据库连接
            user_id: 用户ID
        
        Returns:
            Token列表
        """
        cursor = db[Collections.TOKENS].find({"user": ObjectId(user_id)})
        tokens = await cursor.to_list(length=None)
        
        # 转换ObjectId为字符串
        for token in tokens:
            token["_id"] = str(token["_id"])
            token["user"] = str(token["user"])
        
        return tokens
    
    @staticmethod
    async def get_one(db, token_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个Token
        
        Args:
            db: 数据库连接
            token_id: Token ID
        
        Returns:
            Token信息，不存在返回None
        """
        token = await db[Collections.TOKENS].find_one({"_id": ObjectId(token_id)})
        
        if token:
            token["_id"] = str(token["_id"])
            token["user"] = str(token["user"])
        
        return token
    
    @staticmethod
    async def find_one(db, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        根据条件查询单个Token
        
        Args:
            db: 数据库连接
            query: 查询条件
        
        Returns:
            Token信息，不存在返回None
        """
        token = await db[Collections.TOKENS].find_one(query)
        
        if token:
            token["_id"] = str(token["_id"])
            if "user" in token and isinstance(token["user"], ObjectId):
                token["user"] = str(token["user"])
        
        return token
    
    @staticmethod
    async def add_one(
        db, 
        user_id: str, 
        title: str, 
        value: str
    ) -> Dict[str, Any]:
        """
        添加Token
        
        Args:
            db: 数据库连接
            user_id: 用户ID
            title: Token标题
            value: Token值
        
        Returns:
            创建的Token信息
        """
        # 检查是否已存在相同标题的Token
        existing = await db[Collections.TOKENS].find_one({
            "user": ObjectId(user_id),
            "title": title
        })
        
        if existing:
            raise ValueError(f"Token标题 '{title}' 已存在")
        
        token_data = {
            "title": title,
            "value": value,
            "user": ObjectId(user_id),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = await db[Collections.TOKENS].insert_one(token_data)
        
        return {
            "_id": str(result.inserted_id),
            "title": title,
            "value": value,
            "user": user_id,
            "createdAt": token_data["createdAt"],
            "updatedAt": token_data["updatedAt"]
        }
    
    @staticmethod
    async def update_one(
        db, 
        token_id: str, 
        user_id: str,
        update_data: Dict[str, Any]
    ) -> Any:
        """
        更新Token
        
        Args:
            db: 数据库连接
            token_id: Token ID
            user_id: 用户ID（权限验证）
            update_data: 更新的数据
        
        Returns:
            更新结果
        """
        # 添加更新时间
        update_data["updatedAt"] = datetime.utcnow()
        
        # 只能更新自己的Token
        result = await db[Collections.TOKENS].update_one(
            {
                "_id": ObjectId(token_id),
                "user": ObjectId(user_id)
            },
            {"$set": update_data}
        )
        
        return {
            "acknowledged": result.acknowledged,
            "matchedCount": result.matched_count,
            "modifiedCount": result.modified_count
        }
    
    @staticmethod
    async def delete_one(db, token_id: str, user_id: str) -> Any:
        """
        删除Token
        
        Args:
            db: 数据库连接
            token_id: Token ID
            user_id: 用户ID（权限验证）
        
        Returns:
            删除结果
        """
        # 只能删除自己的Token
        result = await db[Collections.TOKENS].delete_one({
            "_id": ObjectId(token_id),
            "user": ObjectId(user_id)
        })
        
        return {
            "acknowledged": result.acknowledged,
            "deletedCount": result.deleted_count
        }
    
    @staticmethod
    async def validate_token(
        db, 
        title: str, 
        value: str
    ) -> Optional[Dict[str, Any]]:
        """
        验证Token并返回对应用户信息
        
        Args:
            db: 数据库连接
            title: Token标题
            value: Token值
        
        Returns:
            Token信息（包含user字段），验证失败返回None
        """
        token = await db[Collections.TOKENS].find_one({
            "title": title,
            "value": value
        })
        
        if token:
            token["_id"] = str(token["_id"])
            if isinstance(token["user"], ObjectId):
                token["user"] = str(token["user"])
        
        return token

