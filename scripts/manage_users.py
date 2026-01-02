"""
用户管理脚本
用法:
    # 列出所有用户
    uv run python -m scripts.manage_users --list
    
    # 查看某个用户的详细信息
    uv run python -m scripts.manage_users --info 1
    
    # 将用户设为管理员
    uv run python -m scripts.manage_users --set-admin 1
    
    # 取消用户管理员权限
    uv run python -m scripts.manage_users --remove-admin 1
    
    # 删除用户
    uv run python -m scripts.manage_users --delete 1
    
    # 强制删除用户（包括所有帖子、评论等）
    uv run python -m scripts.manage_users --delete 1 --force
    
    # 重置用户密码
    uv run python -m scripts.manage_users --reset-password 1 --new-password newpass123
"""
import argparse

from sqlalchemy import create_engine, select, delete, func
from sqlalchemy.orm import sessionmaker, selectinload

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, Follow
from app.models.post import Post, PostLike, PostFavorite
from app.models.comment import Comment, CommentLike

# 创建同步数据库引擎
sync_url = settings.DATABASE_URL.replace("+aiosqlite", "")
engine = create_engine(sync_url, echo=False)
SessionLocal = sessionmaker(bind=engine)


def list_users():
    """列出所有用户"""
    with SessionLocal() as db:
        result = db.execute(select(User).order_by(User.id))
        users = result.scalars().all()
        
    if not users:
        print("ℹ️  当前没有用户")
        return
    
    print(f"\n📋 用户列表 (共 {len(users)} 个)")
    print("=" * 100)
    print(f"{'ID':<6} {'用户名':<15} {'邮箱':<30} {'管理员':<8} {'创建时间':<20}")
    print("-" * 100)
    
    for user in users:
        admin_status = "✅ 是" if user.is_admin else "❌ 否"
        created_at = user.created_at.strftime("%Y-%m-%d %H:%M") if user.created_at else "N/A"
        print(f"{user.id:<6} {user.username:<15} {user.email:<30} {admin_status:<8} {created_at:<20}")
    
    print("=" * 100)
    print(f"提示: 使用 --info <ID> 查看用户详细信息")


def get_user_info(user_id: int):
    """获取用户详细信息"""
    with SessionLocal() as db:
        # 查询用户
        result = db.execute(
            select(User)
            .options(
                selectinload(User.posts),
                selectinload(User.comments),
                selectinload(User.followers),
                selectinload(User.following)
            )
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ 用户 ID={user_id} 不存在!")
            return None
        
        # 统计点赞数
        post_likes_result = db.execute(
            select(func.count(PostLike.id)).where(PostLike.user_id == user_id)
        )
        post_likes_count = post_likes_result.scalar() or 0
        
        comment_likes_result = db.execute(
            select(func.count(CommentLike.id)).where(CommentLike.user_id == user_id)
        )
        comment_likes_count = comment_likes_result.scalar() or 0
        
        # 统计收藏数
        favorites_result = db.execute(
            select(func.count(PostFavorite.id)).where(PostFavorite.user_id == user_id)
        )
        favorites_count = favorites_result.scalar() or 0
        
    print(f"\n{'='*60}")
    print(f"📌 用户详细信息 (ID: {user.id})")
    print(f"{'='*60}")
    print(f"  用户名:     {user.username}")
    print(f"  邮箱:       {user.email}")
    print(f"  头像:       {user.avatar or '默认'}")
    print(f"  个性签名:   {user.signature or '无'}")
    print(f"  管理员:     {'✅ 是' if user.is_admin else '❌ 否'}")
    print(f"  创建时间:   {user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else 'N/A'}")
    print(f"  更新时间:   {user.updated_at.strftime('%Y-%m-%d %H:%M:%S') if user.updated_at else 'N/A'}")
    print(f"{'-'*60}")
    print(f"📊 统计信息:")
    print(f"  发帖数:     {len(user.posts)}")
    print(f"  评论数:     {len(user.comments)}")
    print(f"  粉丝数:     {len(user.followers)}")
    print(f"  关注数:     {len(user.following)}")
    print(f"  点赞帖子:   {post_likes_count}")
    print(f"  点赞评论:   {comment_likes_count}")
    print(f"  收藏帖子:   {favorites_count}")
    print(f"{'='*60}\n")
    
    return user


def set_admin_by_id(user_id: int, is_admin: bool):
    """通过ID设置/取消用户的管理员权限"""
    with SessionLocal() as db:
        result = db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ 用户 ID={user_id} 不存在!")
            return False
        
        if user.is_admin == is_admin:
            status = "已经是" if is_admin else "已经不是"
            print(f"ℹ️  用户 '{user.username}' (ID={user_id}) {status}管理员")
            return True
        
        user.is_admin = is_admin
        db.commit()
        
        action = "设为" if is_admin else "取消"
        print(f"✅ 已将用户 '{user.username}' (ID={user_id}) {action}管理员")
        return True


def reset_password(user_id: int, new_password: str):
    """重置用户密码"""
    with SessionLocal() as db:
        result = db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ 用户 ID={user_id} 不存在!")
            return False
        
        # 验证密码长度
        if len(new_password) < 6:
            print(f"❌ 密码长度至少6个字符!")
            return False
        
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        
        print(f"✅ 用户 '{user.username}' (ID={user_id}) 密码已重置")
        return True


def delete_user(user_id: int, force: bool = False):
    """删除用户"""
    with SessionLocal() as db:
        # 查询用户
        result = db.execute(
            select(User)
            .options(selectinload(User.posts), selectinload(User.comments))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ 用户 ID={user_id} 不存在!")
            return False
        
        post_count = len(user.posts)
        comment_count = len(user.comments)
        
        # 如果用户有内容且没有 --force，提示确认
        if (post_count > 0 or comment_count > 0) and not force:
            print(f"⚠️  用户 '{user.username}' (ID={user_id}) 有以下内容:")
            print(f"   - 帖子: {post_count} 篇")
            print(f"   - 评论: {comment_count} 条")
            print(f"\n   删除用户将同时删除所有相关内容!")
            print(f"   如需强制删除，请添加 --force 参数")
            return False
        
        # 开始删除流程
        print(f"🗑️  正在删除用户 '{user.username}' (ID={user_id})...")
        
        # 1. 删除用户的评论点赞
        db.execute(delete(CommentLike).where(CommentLike.user_id == user_id))
        print("   ✓ 删除评论点赞记录")
        
        # 2. 删除用户评论下的其他人点赞
        user_comment_ids = [c.id for c in user.comments]
        if user_comment_ids:
            db.execute(delete(CommentLike).where(CommentLike.comment_id.in_(user_comment_ids)))
        
        # 3. 删除用户的评论
        db.execute(delete(Comment).where(Comment.author_id == user_id))
        print("   ✓ 删除评论")
        
        # 4. 删除用户的帖子点赞
        db.execute(delete(PostLike).where(PostLike.user_id == user_id))
        print("   ✓ 删除帖子点赞记录")
        
        # 5. 删除用户的帖子收藏
        db.execute(delete(PostFavorite).where(PostFavorite.user_id == user_id))
        print("   ✓ 删除帖子收藏记录")
        
        # 6. 删除用户帖子相关的点赞、收藏、评论
        user_post_ids = [p.id for p in user.posts]
        if user_post_ids:
            # 删除帖子下的评论点赞
            post_comment_result = db.execute(
                select(Comment.id).where(Comment.post_id.in_(user_post_ids))
            )
            post_comment_ids = [row[0] for row in post_comment_result.fetchall()]
            if post_comment_ids:
                db.execute(delete(CommentLike).where(CommentLike.comment_id.in_(post_comment_ids)))
            
            # 删除帖子下的评论
            db.execute(delete(Comment).where(Comment.post_id.in_(user_post_ids)))
            
            # 删除帖子的点赞和收藏
            db.execute(delete(PostLike).where(PostLike.post_id.in_(user_post_ids)))
            db.execute(delete(PostFavorite).where(PostFavorite.post_id.in_(user_post_ids)))
        
        # 7. 删除用户的帖子
        db.execute(delete(Post).where(Post.author_id == user_id))
        print("   ✓ 删除帖子")
        
        # 8. 删除关注关系
        db.execute(delete(Follow).where(Follow.follower_id == user_id))
        db.execute(delete(Follow).where(Follow.following_id == user_id))
        print("   ✓ 删除关注关系")
        
        # 9. 删除用户
        db.delete(user)
        db.commit()
        
        print(f"\n✅ 用户 '{user.username}' (ID={user_id}) 已删除!")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="用户管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --list                    列出所有用户
  %(prog)s --info 1                  查看用户ID=1的详细信息
  %(prog)s --set-admin 1             将用户ID=1设为管理员
  %(prog)s --remove-admin 1          取消用户ID=1的管理员权限
  %(prog)s --delete 1                删除用户ID=1
  %(prog)s --delete 1 --force        强制删除用户ID=1（包括所有内容）
  %(prog)s --reset-password 1 --new-password abc123  重置用户ID=1的密码
        """
    )
    
    parser.add_argument("--list", "-l", action="store_true", help="列出所有用户")
    parser.add_argument("--info", "-i", type=int, metavar="ID", help="查看用户详细信息")
    parser.add_argument("--set-admin", "-s", type=int, metavar="ID", help="将用户设为管理员")
    parser.add_argument("--remove-admin", "-r", type=int, metavar="ID", help="取消用户管理员权限")
    parser.add_argument("--delete", "-d", type=int, metavar="ID", help="删除用户")
    parser.add_argument("--force", "-f", action="store_true", help="强制删除（跳过确认）")
    parser.add_argument("--reset-password", "-p", type=int, metavar="ID", help="重置用户密码")
    parser.add_argument("--new-password", type=str, metavar="PASSWORD", help="新密码（与--reset-password一起使用）")
    
    args = parser.parse_args()
    
    # 如果没有提供任何参数，显示帮助
    if not any([args.list, args.info, args.set_admin, args.remove_admin, args.delete, args.reset_password]):
        parser.print_help()
        return
    
    if args.list:
        list_users()
    
    if args.info:
        get_user_info(args.info)
    
    if args.set_admin:
        set_admin_by_id(args.set_admin, True)
    
    if args.remove_admin:
        set_admin_by_id(args.remove_admin, False)
    
    if args.delete:
        delete_user(args.delete, args.force)
    
    if args.reset_password:
        if not args.new_password:
            print("❌ 错误: 需要提供 --new-password 参数")
            return
        reset_password(args.reset_password, args.new_password)


if __name__ == "__main__":
    main()