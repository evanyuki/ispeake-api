"""
ISpeak服务
处理ISpeak相关的业务逻辑，包括可见性控制
"""
from typing import Optional, List, Dict, Any
from bson import ObjectId
from datetime import datetime

from app.database import Collections


class IspeakService:
    """ISpeak服务类"""
    
    @staticmethod
    def _process_visibility(
        item: Dict[str, Any],
        current_user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        处理ISpeak可见性
        
        type=0: 公开，所有人可见
        type=1: 需要登录，未登录显示"该内容需登录后查看"
        type=2: 私密，仅作者可见，其他人显示"该内容仅作者可见"
        
        Args:
            item: ISpeak项
            current_user_id: 当前用户ID（可选）
        
        Returns:
            处理后的ISpeak项
        """
        item_type = item.get("type", "0")
        author_id = str(item.get("author", {}).get("_id", "")) if isinstance(item.get("author"), dict) else str(item.get("author", ""))
        
        # type=0: 所有人可见，不做处理
        if item_type == "0":
            return item
        
        # type=1: 需要登录
        if item_type == "1":
            if not current_user_id:
                # 未登录，隐藏内容
                item["content"] = "该内容需登录后查看"
                item["title"] = ""
            return item
        
        # type=2: 仅作者可见
        if item_type == "2":
            if not current_user_id or current_user_id != author_id:
                # 不是作者，隐藏内容
                item["content"] = "该内容仅作者可见"
                item["title"] = ""
            return item
        
        return item
    
    @staticmethod
    async def get_by_page(
        db,
        author: str,
        page: int = 1,
        page_size: int = 10,
        current_user: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        分页获取ISpeak（公开接口，带可见性控制）
        
        Args:
            db: 数据库连接
            author: 作者ID
            page: 页码
            page_size: 每页数量
            current_user: 当前用户信息（可选）
        
        Returns:
            {total: 总数, items: ISpeak列表, isLogin: 用户ID或null}
        """
        query = {"author": ObjectId(author)}
        current_user_id = current_user.get("userId") if current_user else None
        
        # 计算总数
        total = await db[Collections.ISPEAK].count_documents(query)
        
        # 分页查询，使用聚合管道关联author和tag
        skip = (page - 1) * page_size
        pipeline = [
            {"$match": query},
            {"$sort": {"createdAt": -1}},  # 按创建时间倒序
            {"$skip": skip},
            {"$limit": page_size},
            # 关联作者信息
            {
                "$lookup": {
                    "from": Collections.USERS,
                    "localField": "author",
                    "foreignField": "_id",
                    "as": "authorInfo"
                }
            },
            {
                "$unwind": {
                    "path": "$authorInfo",
                    "preserveNullAndEmptyArrays": True
                }
            },
            # 关联标签信息
            {
                "$lookup": {
                    "from": Collections.ISPEAK_TAGS,
                    "localField": "tag",
                    "foreignField": "_id",
                    "as": "tagInfo"
                }
            },
            {
                "$unwind": {
                    "path": "$tagInfo",
                    "preserveNullAndEmptyArrays": True
                }
            },
            # 投影字段
            {
                "$project": {
                    "_id": 1,
                    "title": 1,
                    "content": 1,
                    "type": 1,
                    "showComment": 1,
                    "createdAt": 1,
                    "updatedAt": 1,
                    "author": {
                        "_id": "$authorInfo._id",
                        "nickName": "$authorInfo.nickName",
                        "avatar": "$authorInfo.avatar"
                    },
                    "tag": {
                        "_id": "$tagInfo._id",
                        "name": "$tagInfo.name",
                        "bgColor": "$tagInfo.bgColor"
                    }
                }
            }
        ]
        
        cursor = db[Collections.ISPEAK].aggregate(pipeline)
        items = await cursor.to_list(length=page_size)
        
        # 处理可见性和ID转换
        processed_items = []
        for item in items:
            item["_id"] = str(item["_id"])
            if item.get("author") and item["author"].get("_id"):
                item["author"]["_id"] = str(item["author"]["_id"])
            if item.get("tag") and item["tag"].get("_id"):
                item["tag"]["_id"] = str(item["tag"]["_id"])
            
            # 应用可见性规则
            item = IspeakService._process_visibility(item, current_user_id)
            processed_items.append(item)
        
        return {
            "total": total,
            "items": processed_items,
            "isLogin": current_user_id
        }
    
    @staticmethod
    async def get_by_page_admin(
        db,
        page: int = 1,
        page_size: int = 10,
        author: Optional[str] = None,
        query_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        分页获取ISpeak（管理接口，不应用可见性控制）
        
        Args:
            db: 数据库连接
            page: 页码
            page_size: 每页数量
            author: 作者ID（可选）
            query_params: 其他查询参数
        
        Returns:
            {total: 总数, items: ISpeak列表}
        """
        query = query_params or {}
        if author:
            query["author"] = ObjectId(author)
        
        # 计算总数
        total = await db[Collections.ISPEAK].count_documents(query)
        
        # 分页查询
        skip = (page - 1) * page_size
        pipeline = [
            {"$match": query},
            {"$sort": {"createdAt": -1}},
            {"$skip": skip},
            {"$limit": page_size},
            # 关联作者信息
            {
                "$lookup": {
                    "from": Collections.USERS,
                    "localField": "author",
                    "foreignField": "_id",
                    "as": "authorInfo"
                }
            },
            {
                "$unwind": {
                    "path": "$authorInfo",
                    "preserveNullAndEmptyArrays": True
                }
            },
            # 关联标签信息
            {
                "$lookup": {
                    "from": Collections.ISPEAK_TAGS,
                    "localField": "tag",
                    "foreignField": "_id",
                    "as": "tagInfo"
                }
            },
            {
                "$unwind": {
                    "path": "$tagInfo",
                    "preserveNullAndEmptyArrays": True
                }
            }
        ]
        
        cursor = db[Collections.ISPEAK].aggregate(pipeline)
        items = await cursor.to_list(length=page_size)
        
        # 转换ObjectId为字符串
        for item in items:
            item["_id"] = str(item["_id"])
            item["author"] = str(item["author"])
            item["tag"] = str(item["tag"])
            if "authorInfo" in item and item["authorInfo"]:
                item["authorInfo"]["_id"] = str(item["authorInfo"]["_id"])
            if "tagInfo" in item and item["tagInfo"]:
                item["tagInfo"]["_id"] = str(item["tagInfo"]["_id"])
        
        return {
            "total": total,
            "items": items
        }
    
    @staticmethod
    async def add_one(
        db,
        author_id: str,
        content: str,
        tag_id: str,
        title: str = "",
        ispeak_type: str = "0",
        show_comment: str = "1"
    ) -> Dict[str, Any]:
        """
        添加ISpeak
        
        Args:
            db: 数据库连接
            author_id: 作者ID
            content: 内容
            tag_id: 标签ID
            title: 标题
            ispeak_type: 类型
            show_comment: 是否可评论
        
        Returns:
            创建的ISpeak信息
        """
        # 验证tag_id是否有效
        if not ObjectId.is_valid(tag_id):
            raise ValueError("无效的标签ID")
        
        ispeak_data = {
            "title": title,
            "content": content,
            "type": ispeak_type,
            "tag": ObjectId(tag_id),
            "showComment": show_comment,
            "author": ObjectId(author_id),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        result = await db[Collections.ISPEAK].insert_one(ispeak_data)
        
        return {
            "_id": str(result.inserted_id),
            "title": title,
            "content": content,
            "type": ispeak_type,
            "tag": tag_id,
            "showComment": show_comment,
            "author": author_id,
            "createdAt": ispeak_data["createdAt"],
            "updatedAt": ispeak_data["updatedAt"]
        }
    
    @staticmethod
    async def update_one(
        db,
        ispeak_id: str,
        author_id: str,
        update_data: Dict[str, Any]
    ) -> Any:
        """
        更新ISpeak
        
        Args:
            db: 数据库连接
            ispeak_id: ISpeak ID
            author_id: 作者ID（权限验证）
            update_data: 更新的数据
        
        Returns:
            更新结果
        """
        # 如果更新tag，需要转换为ObjectId
        if "tag" in update_data and update_data["tag"]:
            if not ObjectId.is_valid(update_data["tag"]):
                raise ValueError("无效的标签ID")
            update_data["tag"] = ObjectId(update_data["tag"])
        
        # 添加更新时间
        update_data["updatedAt"] = datetime.utcnow()
        
        # 只能更新自己的ISpeak
        result = await db[Collections.ISPEAK].update_one(
            {
                "_id": ObjectId(ispeak_id),
                "author": ObjectId(author_id)
            },
            {"$set": update_data}
        )
        
        return {
            "acknowledged": result.acknowledged,
            "matchedCount": result.matched_count,
            "modifiedCount": result.modified_count
        }
    
    @staticmethod
    async def update_status(
        db,
        ispeak_id: str,
        author_id: str,
        show_comment: str
    ) -> Any:
        """
        更新ISpeak评论状态
        
        Args:
            db: 数据库连接
            ispeak_id: ISpeak ID
            author_id: 作者ID（权限验证）
            show_comment: 是否可评论
        
        Returns:
            更新结果
        """
        result = await db[Collections.ISPEAK].update_one(
            {
                "_id": ObjectId(ispeak_id),
                "author": ObjectId(author_id)
            },
            {
                "$set": {
                    "showComment": show_comment,
                    "updatedAt": datetime.utcnow()
                }
            }
        )
        
        return {
            "acknowledged": result.acknowledged,
            "matchedCount": result.matched_count,
            "modifiedCount": result.modified_count
        }
    
    @staticmethod
    async def delete_one(db, ispeak_id: str, author_id: str) -> Any:
        """
        删除ISpeak
        
        Args:
            db: 数据库连接
            ispeak_id: ISpeak ID
            author_id: 作者ID（权限验证）
        
        Returns:
            删除结果
        """
        result = await db[Collections.ISPEAK].delete_one({
            "_id": ObjectId(ispeak_id),
            "author": ObjectId(author_id)
        })
        
        return {
            "acknowledged": result.acknowledged,
            "deletedCount": result.deleted_count
        }
    
    @staticmethod
    async def find_by_id(db, ispeak_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID查询ISpeak
        
        Args:
            db: 数据库连接
            ispeak_id: ISpeak ID
        
        Returns:
            ISpeak信息，不存在返回None
        """
        ispeak = await db[Collections.ISPEAK].find_one({"_id": ObjectId(ispeak_id)})
        
        if ispeak:
            ispeak["_id"] = str(ispeak["_id"])
            ispeak["author"] = str(ispeak["author"])
            ispeak["tag"] = str(ispeak["tag"])
        
        return ispeak

