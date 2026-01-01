"""
管理员账号管理脚本
用法:
    # 添加管理员
    uv run python -m scripts.add_admin --username admin --password admin123 --email admin@example.com
    
    # 将现有用户设为管理员
    uv run python -m scripts.add_admin --username existing_user --set-admin
    
    # 取消管理员权限
    uv run python -m scripts.add_admin --username admin --remove-admin
"""
import asyncio
import argparse

from sqlalchemy import select, update

from app.core.database import AsyncSessionLocal, init_db
from app.core.security import get_password_hash
from app.models.user import User
# 导入所有模型以确保关系正确初始化
from app.models.post import Post, PostLike, PostFavorite
from app.models.comment import Comment, CommentLike


async def add_admin(username: str, password: str, email: str):
    """创建新的管理员账号"""
    await init_db()
    
    async with AsyncSessionLocal() as db:
        # 检查用户名是否已存在
        result = await db.execute(select(User).where(User.username == username))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"❌ 用户名 '{username}' 已存在!")
            print(f"   如需将其设为管理员，请使用: --username {username} --set-admin")
            return False
        
        # 检查邮箱是否已存在
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            print(f"❌ 邮箱 '{email}' 已被使用!")
            return False
        
        # 创建管理员用户
        admin_user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            avatar=f"https://api.dicebear.com/7.x/avataaars/svg?seed={username}",
            is_admin=True,
            signature="系统管理员"
        )
        
        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)
        
        print(f"✅ 管理员账号创建成功!")
        print(f"   用户名: {username}")
        print(f"   邮箱: {email}")
        print(f"   ID: {admin_user.id}")
        return True


async def set_admin(username: str, is_admin: bool = True):
    """设置/取消用户的管理员权限"""
    await init_db()
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ 用户 '{username}' 不存在!")
            return False
        
        if user.is_admin == is_admin:
            status = "已经是" if is_admin else "已经不是"
            print(f"ℹ️  用户 '{username}' {status}管理员")
            return True
        
        user.is_admin = is_admin
        await db.commit()
        
        action = "设为" if is_admin else "取消"
        print(f"✅ 已将用户 '{username}' {action}管理员")
        return True


async def list_admins():
    """列出所有管理员"""
    await init_db()
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.is_admin == True))
        admins = result.scalars().all()
        
    if not admins:
        print("ℹ️  当前没有管理员账号")
        return
    
    print(f"📋 管理员列表 (共 {len(admins)} 个):")
    print("-" * 50)
    for admin in admins:
        print(f"   ID: {admin.id} | 用户名: {admin.username} | 邮箱: {admin.email}")
    print("-" * 50)


def main():
    parser = argparse.ArgumentParser(description="管理员账号管理工具")
    parser.add_argument("--username", "-u", help="用户名")
    parser.add_argument("--password", "-p", help="密码 (创建新管理员时需要)")
    parser.add_argument("--email", "-e", help="邮箱 (创建新管理员时需要)")
    parser.add_argument("--set-admin", action="store_true", help="将现有用户设为管理员")
    parser.add_argument("--remove-admin", action="store_true", help="取消用户的管理员权限")
    parser.add_argument("--list", "-l", action="store_true", help="列出所有管理员")
    
    args = parser.parse_args()
    
    if args.list:
        asyncio.run(list_admins())
        return
    
    if not args.username:
        parser.print_help()
        print("\n❌ 错误: 需要提供 --username 参数")
        return
    
    if args.set_admin:
        asyncio.run(set_admin(args.username, True))
    elif args.remove_admin:
        asyncio.run(set_admin(args.username, False))
    else:
        # 创建新管理员
        if not args.password:
            print("❌ 错误: 创建新管理员需要提供 --password 参数")
            return
        if not args.email:
            print("❌ 错误: 创建新管理员需要提供 --email 参数")
            return
        asyncio.run(add_admin(args.username, args.password, args.email))


if __name__ == "__main__":
    main()
