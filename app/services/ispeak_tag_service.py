"""
ISpeak标签服务
处理ISpeak标签相关的业务逻辑
"""
from typing import Optional, List, Dict, Any
from bson import ObjectId
from datetime import datetime

from app.database import Collections


class IspeakTagService:
    """ISpeak标签服务类"""
    
    @staticmethod
    async def get_list(db, user_id: str) -> List[Dict[str, Any]]:
        """
        获取用户的标签列表（按orderNo排序）
        
        Args:
            db: 数据库连接
            user_id: 用户ID
        
        Returns:
            标签列表
        """
        cursor = db[Collections.ISPEAK_TAGS].find(
            {"user": ObjectId(user_id)}
        ).sort("orderNo", 1)  # 按orderNo升序排序
        
        tags = await cursor.to_list(length=None)
        
        # 转换ObjectId为字符串
        for tag in tags:
            tag["_id"] = str(tag["_id"])
            tag["user"] = str(tag["user"])
        
        return tags
    
    @staticmethod
    async def get_by_page(
        db, 
        user_id: str,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        分页获取标签
        
        Args:
            db: 数据库连接
            user_id: 用户ID
            page: 页码
            page_size: 每页数量
        
        Returns:
            {total: 总数, items: 标签列表}
        """
        query = {"user": ObjectId(user_id)}
        
        # 计算总数
        total = await db[Collections.ISPEAK_TAGS].count_documents(query)
        
        # 分页查询
        skip = (page - 1) * page_size
        cursor = db[Collections.ISPEAK_TAGS].find(query).sort("orderNo", 1).skip(skip).limit(page_size)
        items = await cursor.to_list(length=page_size)
        
        # 转换ObjectId为字符串
        for item in items:
            item["_id"] = str(item["_id"])
            item["user"] = str(item["user"])
        
        return {
            "total": total,
            "items": items
        }
    
    @staticmethod
    async def find_one(
        db, 
        query: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        根据条件查询单个标签
        
        Args:
            db: 数据库连接
            query: 查询条件
        
        Returns:
            标签信息，不存在返回None
        """
        tag = await db[Collections.ISPEAK_TAGS].find_one(query)
        
        if tag:
            tag["_id"] = str(tag["_id"])
            if "user" in tag and isinstance(tag["user"], ObjectId):
                tag["user"] = str(tag["user"])
        
        return tag
    
    @staticmethod
    async def add_one(
        db, 
        user_id: str,
        name: str,
        bg_color: str = "#DB2828",
        order_no: int = 0,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        添加标签
        
        Args:
            db: 数据库连接
            user_id: 用户ID
            name: 标签名称
            bg_color: 背景颜色
            order_no: 排序序号
            description: 描述
        
        Returns:
            创建的标签信息
        """
        # 检查标签名是否已存在
        existing = await db[Collections.ISPEAK_TAGS].find_one({
            "user": ObjectId(user_id),
            "name": name
        })
        
        if existing:
            raise ValueError(f"标签名 '{name}' 已存在")
        
        tag_data = {
            "name": name,
            "bgColor": bg_color,
            "user": ObjectId(user_id),
            "orderNo": order_no,
            "description": description,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = await db[Collections.ISPEAK_TAGS].insert_one(tag_data)
        
        return {
            "_id": str(result.inserted_id),
            "name": name,
            "bgColor": bg_color,
            "user": user_id,
            "orderNo": order_no,
            "description": description,
            "createdAt": tag_data["createdAt"],
            "updatedAt": tag_data["updatedAt"]
        }
    
    @staticmethod
    async def update_one(
        db, 
        tag_id: str,
        user_id: str,
        update_data: Dict[str, Any]
    ) -> Any:
        """
        更新标签
        
        Args:
            db: 数据库连接
            tag_id: 标签ID
            user_id: 用户ID（权限验证）
            update_data: 更新的数据
        
        Returns:
            更新结果
        """
        # 如果更新标签名，需要检查是否重复
        if "name" in update_data:
            existing = await db[Collections.ISPEAK_TAGS].find_one({
                "user": ObjectId(user_id),
                "name": update_data["name"],
                "_id": {"$ne": ObjectId(tag_id)}
            })
            
            if existing:
                raise ValueError(f"标签名 '{update_data['name']}' 已存在")
        
        # 添加更新时间
        update_data["updatedAt"] = datetime.utcnow()
        
        # 只能更新自己的标签
        result = await db[Collections.ISPEAK_TAGS].update_one(
            {
                "_id": ObjectId(tag_id),
                "user": ObjectId(user_id)
            },
            {"$set": update_data}
        )
        
        return {
            "acknowledged": result.acknowledged,
            "matchedCount": result.matched_count,
            "modifiedCount": result.modified_count
        }

