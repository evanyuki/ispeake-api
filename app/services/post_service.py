"""
Post朋友圈服务
处理Post相关的业务逻辑
"""
from typing import List, Dict, Any
from bson import ObjectId
from datetime import datetime

from app.database import Collections


class PostService:
    """Post服务类"""
    
    @staticmethod
    async def find_all(db) -> List[Dict[str, Any]]:
        """
        查询所有Post
        
        Args:
            db: 数据库连接
        
        Returns:
            Post列表
        """
        cursor = db[Collections.POSTS].find({}).sort("createdAt", -1)
        posts = await cursor.to_list(length=None)
        
        # 转换ObjectId为字符串
        for post in posts:
            post["_id"] = str(post["_id"])
        
        return posts
    
    @staticmethod
    async def create_one(
        db,
        title: str,
        link: str,
        author: str,
        avatar: str,
        rule: str = "",
        updated: datetime = None,
        created: datetime = None
    ) -> Dict[str, Any]:
        """
        创建Post
        
        Args:
            db: 数据库连接
            title: 文章标题
            link: 文章链接
            author: 作者名称
            avatar: 作者头像
            rule: 爬虫规则
            updated: 文章更新时间
            created: 文章创建时间
        
        Returns:
            创建的Post信息
        """
        post_data = {
            "title": title,
            "link": link,
            "author": author,
            "avatar": avatar,
            "rule": rule,
            "updated": updated or datetime.utcnow(),
            "created": created or datetime.utcnow(),
            "createdAt": datetime.utcnow()
        }
        
        result = await db[Collections.POSTS].insert_one(post_data)
        
        return {
            "_id": str(result.inserted_id),
            "title": title,
            "link": link,
            "author": author,
            "avatar": avatar,
            "rule": rule,
            "updated": post_data["updated"],
            "created": post_data["created"],
            "createdAt": post_data["createdAt"]
        }

