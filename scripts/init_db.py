"""
数据库初始化脚本 - 创建管理员账号和测试数据
"""
import asyncio
import random
from datetime import datetime, timezone, timedelta

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, init_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.post import Post, PostLike
from app.models.comment import Comment


# 测试用户数据
TEST_USERS = [
    {"username": "admin", "email": "admin@animehub.com", "password": "admin123", "is_admin": True},
    {"username": "testuser", "email": "test@animehub.com", "password": "test123456", "is_admin": False},
    {"username": "animelover", "email": "animelover@example.com", "password": "password123", "is_admin": False},
    {"username": "otaku_master", "email": "otaku@example.com", "password": "password123", "is_admin": False},
    {"username": "manga_fan", "email": "manga@example.com", "password": "password123", "is_admin": False},
]

# 测试帖子标题和内容
TEST_POSTS = [
    {
        "title": "《鬼灭之刃》第四季完结撒花!",
        "content": "柱稽古篇真的太精彩了!每一集的战斗场面都让人热血沸腾,特别是最后几集的剧情,看得我眼泪都出来了。大家觉得这一季怎么样?"
    },
    {
        "title": "推荐一些治愈系动漫",
        "content": "最近工作压力有点大,想看一些治愈系的动漫放松一下。目前看过《夏目友人帐》和《水星领航员》,大家还有什么推荐吗?"
    },
    {
        "title": "关于《进击的巨人》结局的讨论",
        "content": "刚刚补完《进击的巨人》,对结局有很多想法。艾伦的选择让我思考了很久,大家是怎么理解他的决定的?"
    },
    {
        "title": "新番《葬送的芙莉莲》太神了!",
        "content": "这部番的画面太美了,剧情也很有深度。芙莉莲的角色塑造太棒了,每一集都有新的感动。强烈推荐还没看的朋友!"
    },
    {
        "title": "分享我收藏的动漫周边",
        "content": "终于收到了等了三个月的手办!是《JOJO的奇妙冒险》承太郎的景品,做工真的很精细。晒一下我的收藏,欢迎交流~"
    },
    {
        "title": "《间谍过家家》第二季什么时候出?",
        "content": "等第二季等到花都谢了,阿尼亚太可爱了!有人知道什么时候播出吗?"
    },
    {
        "title": "老番重温:《钢之炼金术师FA》",
        "content": "第N次重温钢炼了,每次看都有新的感悟。这部作品真的是神作,剧情、角色、世界观都是顶级的。"
    },
    {
        "title": "求推荐类似《紫罗兰永恒花园》的番",
        "content": "刚看完紫罗兰,哭得稀里哗啦的。想找类似风格的动漫,画面精美、剧情感人的那种。"
    },
    {
        "title": "动漫音乐分享会",
        "content": "来分享一下你们最喜欢的动漫OST吧!我先来:《你的名字》的《前前前世》,每次听都会起鸡皮疙瘩。"
    },
    {
        "title": "《咒术回战》涩谷事变太虐了",
        "content": "刚追到涩谷事变篇,心态有点崩。这个作者是不是对角色有什么误解?太虐了吧!"
    },
]

# 测试评论
TEST_COMMENTS = [
    "说得太对了,完全同意!",
    "这部番确实很棒,强烈推荐!",
    "哈哈哈,我也是这么想的",
    "感谢分享,马上去看!",
    "我也超喜欢这部作品的",
    "期待后续更新~",
    "太感动了😭",
    "同好+1",
    "收藏了,谢谢楼主!",
    "这个分析很到位",
]


async def create_test_data():
    """创建测试数据"""
    await init_db()
    
    async with AsyncSessionLocal() as db:
        # 检查是否已有数据
        result = await db.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("数据库已有数据,跳过初始化")
            return
        
        print("开始创建测试数据...")
        
        # 创建用户
        users = []
        for user_data in TEST_USERS:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                avatar=f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_data['username']}",
                is_admin=user_data["is_admin"],
                signature=f"我是{user_data['username']},热爱动漫!" if not user_data["is_admin"] else "系统管理员"
            )
            db.add(user)
            users.append(user)
        
        await db.flush()
        print(f"✅ 创建了 {len(users)} 个用户")
        
        # 创建帖子
        posts = []
        for i, post_data in enumerate(TEST_POSTS):
            author = random.choice(users[1:])  # 排除admin
            post = Post(
                title=post_data["title"],
                content=post_data["content"],
                author_id=author.id,
                view_count=random.randint(50, 500),
                created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))
            )
            db.add(post)
            posts.append(post)
        
        await db.flush()
        print(f"✅ 创建了 {len(posts)} 个帖子")
        
        # 创建点赞
        likes_count = 0
        for post in posts:
            # 随机给帖子点赞
            for user in random.sample(users, k=random.randint(1, len(users))):
                if user.id != post.author_id:  # 不能给自己点赞
                    like = PostLike(user_id=user.id, post_id=post.id)
                    db.add(like)
                    likes_count += 1
        
        await db.flush()
        print(f"✅ 创建了 {likes_count} 个点赞")
        
        # 创建评论
        comments_count = 0
        for post in posts:
            # 随机给帖子添加评论
            for _ in range(random.randint(1, 5)):
                author = random.choice(users)
                comment = Comment(
                    content=random.choice(TEST_COMMENTS),
                    author_id=author.id,
                    post_id=post.id,
                    created_at=post.created_at + timedelta(hours=random.randint(1, 48))
                )
                db.add(comment)
                comments_count += 1
        
        await db.commit()
        print(f"✅ 创建了 {comments_count} 条评论")
        
        print("\n📋 测试账号信息:")
        print("=" * 40)
        print("管理员账号: admin / admin123")
        print("测试账号: testuser / test123456")
        print("=" * 40)
        print("\n✨ 测试数据创建完成!")


if __name__ == "__main__":
    asyncio.run(create_test_data())
