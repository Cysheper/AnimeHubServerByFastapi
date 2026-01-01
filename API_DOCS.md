# 动漫Hub API文档

## 基本信息

- **Base URL**: `http://localhost:8080/api`
- **认证方式**: Bearer Token (JWT)
- **请求格式**: JSON
- **响应格式**: JSON

## 通用响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "Success",
  "data": {}
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "Error message",
  "data": null
}
```

### 状态码说明
- `200`: 成功
- `400`: 请求参数错误
- `401`: 未授权/token无效
- `403`: 无权限
- `404`: 资源不存在
- `500`: 服务器错误

---

## 认证接口

### 1. 用户注册
/site/stats
**POST** `/auth/register`

#### 请求参数
```json
{
  "username": "string",  // 用户名,3-20字符
  "password": "string",  // 密码,6-32字符
  "email": "string"      // 邮箱
}
```

#### 响应示例
```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=testuser",
      "createdAt": "2026-01-01T00:00:00.000Z"
    }
  }
}
```

---

### 2. 用户登录

**POST** `/auth/login`

#### 请求参数
```json
{
  "username": "string",  // 用户名
  "password": "string"   // 密码
}
```

#### 响应示例
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=testuser",
      "createdAt": "2026-01-01T00:00:00.000Z"
    }
  }
}
```

---

### 3. 获取当前用户信息

**GET** `/auth/user`

**需要认证**: 是

#### 响应示例
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=testuser",
    "createdAt": "2026-01-01T00:00:00.000Z"
  }
}
```

---

### 4. 用户登出

**POST** `/auth/logout`

**需要认证**: 是

#### 响应示例
```json
{
  "code": 200,
  "message": "登出成功",
  "data": null
}
```

---

## 帖子接口

### 5. 获取帖子列表

**GET** `/posts`

#### 查询参数
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | number | 否 | 1 | 页码 |
| limit | number | 否 | 20 | 每页数量 |

#### 响应示例
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "这是帖子标题",
        "content": "这是帖子内容...",
        "images": [
          "https://example.com/image1.jpg",
          "https://example.com/image2.jpg"
        ],
        "author": {
          "id": 1,
          "username": "testuser",
          "email": "test@example.com",
          "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=testuser",
          "createdAt": "2026-01-01T00:00:00.000Z"
        },
        "likes": 42,
        "commentCount": 10,
        "viewCount": 328,
        "isLiked": false,
        "createdAt": "2026-01-01T12:00:00.000Z",
        "updatedAt": "2026-01-01T12:00:00.000Z",
        "comments": []
      }
    ],
    "total": 100,
    "page": 1,
    "limit": 20,
    "hasMore": true
  }
}
```

---

### 6. 获取热门帖子

**GET** `/posts/hot`

#### 查询参数
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | number | 否 | 1 | 页码 |
| limit | number | 否 | 20 | 每页数量 |

#### 响应示例
同「获取帖子列表」

---

### 7. 获取推荐帖子

**GET** `/posts/recommended`

#### 查询参数
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | number | 否 | 1 | 页码 |
| limit | number | 否 | 20 | 每页数量 |

#### 响应示例
同「获取帖子列表」

---

### 8. 获取帖子详情

**GET** `/posts/:id`

#### 路径参数
| 参数 | 类型 | 说明 |
|------|------|------|
| id | number | 帖子ID |

#### 响应示例
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "id": 1,
    "title": "这是帖子标题",
    "content": "这是帖子内容...",
    "images": [
      "https://example.com/image1.jpg"
    ],
    "author": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=testuser",
      "createdAt": "2026-01-01T00:00:00.000Z"
    },
    "likes": 42,
    "commentCount": 10,
    "viewCount": 328,
    "isLiked": false,
    "createdAt": "2026-01-01T12:00:00.000Z",
    "updatedAt": "2026-01-01T12:00:00.000Z",
    "comments": [
      {
        "id": 1,
        "postId": 1,
        "content": "这是一条评论",
        "author": {
          "id": 2,
          "username": "commenter",
          "email": "commenter@example.com",
          "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=commenter",
          "createdAt": "2026-01-01T00:00:00.000Z"
        },
        "likes": 5,
        "isLiked": false,
        "createdAt": "2026-01-01T13:00:00.000Z"
      }
    ]
  }
}
```

---

### 9. 创建帖子

**POST** `/posts`

**需要认证**: 是

#### 请求参数
```json
{
  "title": "string",      // 帖子标题,1-100字符
  "content": "string",    // 帖子内容,1-5000字符
  "images": ["string"]    // 可选,图片URL数组,最多9张
}
```

#### 响应示例
```json
{
  "code": 200,
  "message": "发布成功",
  "data": {
    "id": 1,
    "title": "这是帖子标题",
    "content": "这是帖子内容...",
    "images": [],
    "author": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=testuser",
      "createdAt": "2026-01-01T00:00:00.000Z"
    },
    "likes": 0,
    "commentCount": 0,
    "viewCount": 0,
    "isLiked": false,
    "createdAt": "2026-01-01T14:00:00.000Z",
    "updatedAt": "2026-01-01T14:00:00.000Z",
    "comments": []
  }
}
```

---

### 10. 点赞帖子

**POST** `/posts/:id/like`

**需要认证**: 是

#### 路径参数
| 参数 | 类型 | 说明 |
|------|------|------|
| id | number | 帖子ID |

#### 响应示例
```json
{
  "code": 200,
  "message": "点赞成功",
  "data": null
}
```

**注意**: 
- 如果已点赞,再次调用将取消点赞
- 前端需要根据业务逻辑处理点赞状态切换

---

## 评论接口

### 11. 创建评论

**POST** `/posts/:id/comments`

**需要认证**: 是

#### 路径参数
| 参数 | 类型 | 说明 |
|------|------|------|
| id | number | 帖子ID |

#### 请求参数
```json
{
  "content": "string"  // 评论内容,1-500字符
}
```

#### 响应示例
```json
{
  "code": 200,
  "message": "评论成功",
  "data": {
    "id": 1,
    "postId": 1,
    "content": "这是一条评论",
    "author": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=testuser",
      "createdAt": "2026-01-01T00:00:00.000Z"
    },
    "likes": 0,
    "isLiked": false,
    "createdAt": "2026-01-01T14:30:00.000Z"
  }
}
```

---

### 12. 点赞评论

**POST** `/comments/:id/like`

**需要认证**: 是

#### 路径参数
| 参数 | 类型 | 说明 |
|------|------|------|
| id | number | 评论ID |

#### 响应示例
```json
{
  "code": 200,
  "message": "点赞成功",
  "data": null
}
```

**注意**: 如果已点赞,再次调用将取消点赞

---

## 站点信息接口

### 13. 获取站点统计

**GET** `/site/stats`

#### 响应示例
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "totalPosts": 1523,      // 总帖子数
    "todayPosts": 42,        // 今日新帖
    "totalUsers": 8934,      // 注册用户数
    "onlineUsers": 157       // 在线用户数
  }
}
```

---

### 14. 获取今日运势

**GET** `/site/fortune`

#### 响应示例
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "id": 1,
    "title": "大吉",
    "content": "今天是个好日子,适合追番和交友!",
    "type": "great",         // great | good | normal | bad
    "icon": "🎉"
  }
}
```

**注意**: 
- 每个用户每天只能抽取一次运势
- 可以使用用户ID+日期作为种子生成固定的运势结果

---

### 15. 获取开发者信息

**GET** `/site/developers`

#### 响应示例
```json
{
  "code": 200,
  "message": "Success",
  "data": [
    {
      "id": 1,
      "name": "主开发者",
      "role": "全栈工程师",
      "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=developer1",
      "github": "https://github.com/developer1",
      "email": "dev@animehub.com",
      "description": "负责项目架构和核心功能开发"
    },
    {
      "id": 2,
      "name": "UI设计师",
      "role": "视觉设计师",
      "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=designer",
      "email": "designer@animehub.com",
      "description": "负责界面设计和用户体验"
    }
  ]
}
```

---

## 数据模型

### User (用户)
```typescript
{
  id: number              // 用户ID
  username: string        // 用户名
  email: string          // 邮箱
  avatar: string         // 头像URL
  signature?: string     // 个性签名
  postsCount?: number    // 发帖数
  likesCount?: number    // 获赞数
  followersCount?: number // 粉丝数
  followingCount?: number // 关注数
  createdAt: string      // 创建时间
}
```

### Post (帖子)
```typescript
{
  id: number              // 帖子ID
  title: string           // 标题
  content: string         // 内容
  images?: string[]       // 图片URL数组
  author: User           // 作者信息
  likes: number          // 点赞数
  commentCount: number   // 评论数
  viewCount: number      // 浏览数
  isLiked: boolean       // 当前用户是否已点赞
  createdAt: string      // 创建时间
  updatedAt: string      // 更新时间
  comments: Comment[]    // 评论列表(详情接口返回)
}
```

### Comment (评论)
```typescript
{
  id: number              // 评论ID
  postId: number         // 所属帖子ID
  content: string        // 内容
  author: User          // 作者信息
  likes: number         // 点赞数
  isLiked: boolean      // 当前用户是否已点赞
  createdAt: string     // 创建时间
}
```

### PaginatedResponse (分页响应)
```typescript
{
  items: T[]            // 数据列表
  total: number         // 总数
  page: number          // 当前页码
  limit: number         // 每页数量
  hasMore: boolean      // 是否还有更多
}
```

---

## 请求头要求

### 认证请求
所有需要认证的接口需要在请求头中携带 token:

```
Authorization: Bearer <your_token_here>
```

### 通用请求头
```
Content-Type: application/json
Accept: application/json
```

---

## 错误处理示例

### 401 未授权
```json
{
  "code": 401,
  "message": "未授权,请先登录",
  "data": null
}
```

### 404 资源不存在
```json
{
  "code": 404,
  "message": "帖子不存在",
  "data": null
}
```

### 400 参数错误
```json
{
  "code": 400,
  "message": "标题不能为空",
  "data": null
}
```

---

## 注意事项

1. **认证**: 所有需要认证的接口都需要在请求头中携带有效的 JWT token
2. **分页**: 默认每页20条数据,最大100条
3. **图片上传**: 图片需要先上传到存储服务,然后将URL传给接口(可选择实现图片上传接口)
4. **时间格式**: 所有时间字段使用 ISO 8601 格式 (`YYYY-MM-DDTHH:mm:ss.sssZ`)
5. **头像**: 可以使用 [DiceBear](https://api.dicebear.com/) 生成默认头像
6. **点赞**: 点赞接口为切换式,同一接口处理点赞和取消点赞
7. **CORS**: 需要在后端配置 CORS 允许前端域名访问
8. **Rate Limiting**: 建议实现接口限流,防止恶意请求

---

## 可选扩展接口

以下接口可根据需求选择性实现:

1. **图片上传**: `POST /upload/image`
2. **用户资料更新**: `PUT /auth/user`
3. **帖子编辑**: `PUT /posts/:id`
4. **帖子删除**: `DELETE /posts/:id`
5. **评论删除**: `DELETE /comments/:id`
6. **用户关注**: `POST /users/:id/follow`
7. **搜索帖子**: `GET /posts/search?q=keyword`
8. **通知系统**: `GET /notifications`

---

## 个人主页接口

### 1. 获取用户资料

**GET** `/users/:id/profile`

#### 请求参数
- `id`: 用户ID (路径参数)

#### 响应示例
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "id": 1,
    "username": "animelover",
    "email": "user@example.com",
    "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=user",
    "signature": "热爱动漫，享受生活 ✨",
    "postsCount": 42,
    "likesCount": 328,
    "followersCount": 89,
    "followingCount": 156,
    "createdAt": "2025-06-15T10:30:00.000Z"
  }
}
```

---

### 2. 更新用户资料

**PUT** `/users/profile`

#### 请求头
```
Authorization: Bearer {token}
```

#### 请求参数
```json
{
  "username": "string",      // 可选,用户名,3-20字符
  "email": "string",         // 可选,邮箱
  "signature": "string"      // 可选,个性签名,最多200字符
}
```

#### 响应示例
```json
{
  "code": 200,
  "message": "资料更新成功",
  "data": {
    "id": 1,
    "username": "newname",
    "email": "newemail@example.com",
    "signature": "新的个性签名",
    "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=newname",
    "createdAt": "2025-06-15T10:30:00.000Z"
  }
}
```

---

### 3. 更改密码

**PUT** `/users/password`

#### 请求头
```
Authorization: Bearer {token}
```

#### 请求参数
```json
{
  "currentPassword": "string",  // 当前密码
  "newPassword": "string"       // 新密码,6-32字符
}
```

#### 响应示例
```json
{
  "code": 200,
  "message": "密码修改成功",
  "data": null
}
```

#### 错误响应
```json
{
  "code": 400,
  "message": "当前密码错误",
  "data": null
}
```

---

### 4. 上传头像

**POST** `/users/avatar`

#### 请求头
```
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

#### 请求参数
- `avatar`: 图片文件 (FormData)
  - 支持格式: jpg, jpeg, png, gif
  - 最大大小: 5MB
  - 推荐尺寸: 300x300

#### 响应示例
```json
{
  "code": 200,
  "message": "头像上传成功",
  "data": {
    "avatarUrl": "https://cdn.animehub.com/avatars/user1_20260101.jpg"
  }
}
```

---

### 5. 获取用户发布的帖子

**GET** `/users/:id/posts`

#### 请求参数
- `id`: 用户ID (路径参数)
- `page`: 页码,默认1
- `pageSize`: 每页数量,默认20

#### 响应示例
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "帖子标题",
        "content": "帖子内容...",
        "images": ["https://example.com/image1.jpg"],
        "author": {
          "id": 1,
          "username": "animelover",
          "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=user"
        },
        "likes": 42,
        "commentCount": 10,
        "viewCount": 328,
        "isLiked": false,
        "createdAt": "2026-01-01T12:00:00.000Z",
        "updatedAt": "2026-01-01T12:00:00.000Z"
      }
    ],
    "total": 42,
    "page": 1,
    "pageSize": 20
  }
}
```

---

### 6. 获取用户收藏的帖子

**GET** `/users/favorites`

#### 请求头
```
Authorization: Bearer {token}
```

#### 请求参数
- `page`: 页码,默认1
- `pageSize`: 每页数量,默认20

#### 响应示例
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "收藏的帖子标题",
        "content": "帖子内容...",
        "author": {
          "id": 2,
          "username": "otheuser",
          "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=other"
        },
        "likes": 100,
        "commentCount": 25,
        "viewCount": 500,
        "isLiked": true,
        "favoriteAt": "2026-01-01T10:00:00.000Z",
        "createdAt": "2025-12-25T12:00:00.000Z"
      }
    ],
    "total": 15,
    "page": 1,
    "pageSize": 20
  }
}
```

---

### 7. 收藏/取消收藏帖子

**POST** `/posts/:id/favorite`

#### 请求头
```
Authorization: Bearer {token}
```

#### 请求参数
- `id`: 帖子ID (路径参数)

#### 响应示例
```json
{
  "code": 200,
  "message": "收藏成功",
  "data": {
    "isFavorited": true
  }
}
```

#### 取消收藏
再次调用相同接口会取消收藏:
```json
{
  "code": 200,
  "message": "已取消收藏",
  "data": {
    "isFavorited": false
  }
}
```

---

### 8. 获取用户设置

**GET** `/users/settings`

#### 请求头
```
Authorization: Bearer {token}
```

#### 响应示例
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "emailNotifications": true,
    "messageNotifications": true,
    "publicProfile": true
  }
}
```

---

### 9. 更新用户设置

**PUT** `/users/settings`

#### 请求头
```
Authorization: Bearer {token}
```

#### 请求参数
```json
{
  "emailNotifications": true,    // 可选,邮箱通知
  "messageNotifications": true,  // 可选,私信通知
  "publicProfile": true          // 可选,公开资料
}
```

#### 响应示例
```json
{
  "code": 200,
  "message": "设置已更新",
  "data": {
    "emailNotifications": true,
    "messageNotifications": true,
    "publicProfile": true
  }
}
```

---

### 10. 删除账号

**DELETE** `/users/account`

#### 请求头
```
Authorization: Bearer {token}
```

#### 请求参数
```json
{
  "password": "string"  // 需要输入密码确认
}
```

#### 响应示例
```json
{
  "code": 200,
  "message": "账号已删除",
  "data": null
}
```

#### 注意事项
- 删除账号将永久删除所有用户数据
- 包括发布的帖子、评论、点赞记录等
- 此操作不可逆，请谨慎使用

---

### 11. 关注用户

**POST** `/users/:id/follow`

#### 请求头
```
Authorization: Bearer {token}
```

#### 请求参数
- `id`: 要关注的用户ID (路径参数)

#### 响应示例
```json
{
  "code": 200,
  "message": "关注成功",
  "data": {
    "isFollowing": true
  }
}
```

#### 取消关注
再次调用相同接口会取消关注:
```json
{
  "code": 200,
  "message": "已取消关注",
  "data": {
    "isFollowing": false
  }
}
```

---

### 12. 获取粉丝列表

**GET** `/users/:id/followers`

#### 请求参数
- `id`: 用户ID (路径参数)
- `page`: 页码,默认1
- `pageSize`: 每页数量,默认20

#### 响应示例
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "items": [
      {
        "id": 2,
        "username": "follower1",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=follower1",
        "signature": "动漫爱好者",
        "isFollowing": false,
        "followedAt": "2025-12-20T10:00:00.000Z"
      }
    ],
    "total": 89,
    "page": 1,
    "pageSize": 20
  }
}
```

---

### 13. 获取关注列表

**GET** `/users/:id/following`

#### 请求参数
- `id`: 用户ID (路径参数)
- `page`: 页码,默认1
- `pageSize`: 每页数量,默认20

#### 响应示例
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "items": [
      {
        "id": 3,
        "username": "following1",
        "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=following1",
        "signature": "二次元世界最棒！",
        "isFollowing": true,
        "followedAt": "2025-12-15T08:30:00.000Z"
      }
    ],
    "total": 156,
    "page": 1,
    "pageSize": 20
  }
}
```

---

## 管理员接口

管理员接口需要管理员权限，请求头中需要携带管理员 token。

### 1. 删除帖子

**DELETE** `/admin/posts/:id`

#### 请求头
```
Authorization: Bearer {admin_token}
```

#### 请求参数
- `id`: 帖子ID (路径参数)

#### 响应示例
```json
{
  "code": 200,
  "message": "帖子删除成功",
  "data": null
}
```

#### 错误响应
```json
{
  "code": 403,
  "message": "无权限操作",
  "data": null
}
```

---

### 2. 删除评论

**DELETE** `/admin/comments/:id`

#### 请求头
```
Authorization: Bearer {admin_token}
```

#### 请求参数
- `id`: 评论ID (路径参数)

#### 响应示例
```json
{
  "code": 200,
  "message": "评论删除成功",
  "data": null
}
```

---

### 3. 获取所有帖子（管理员）

**GET** `/admin/posts`

#### 请求头
```
Authorization: Bearer {admin_token}
```

#### 请求参数
- `page`: 页码,默认1
- `pageSize`: 每页数量,默认20
- `sortBy`: 排序方式,可选值: latest(最新), oldest(最早), mostLiked(最多点赞), mostCommented(最多评论)
- `search`: 搜索关键词,可选

#### 响应示例
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "帖子标题",
        "content": "帖子内容...",
        "author": {
          "id": 1,
          "username": "user1",
          "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=user1"
        },
        "likes": 42,
        "commentCount": 10,
        "viewCount": 328,
        "createdAt": "2026-01-01T10:00:00.000Z",
        "comments": [
          {
            "id": 1,
            "postId": 1,
            "content": "评论内容",
            "author": {
              "id": 2,
              "username": "user2",
              "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=user2"
            },
            "likes": 5,
            "createdAt": "2026-01-01T10:30:00.000Z"
          }
        ]
      }
    ],
    "total": 100,
    "page": 1,
    "pageSize": 20
  }
}
```

---

### 4. 获取所有评论（管理员）

**GET** `/admin/comments`

#### 请求头
```
Authorization: Bearer {admin_token}
```

#### 请求参数
- `page`: 页码,默认1
- `pageSize`: 每页数量,默认20
- `sortBy`: 排序方式,可选值: latest(最新), oldest(最早)
- `search`: 搜索关键词,可选

#### 响应示例
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "items": [
      {
        "id": 1,
        "postId": 1,
        "content": "评论内容",
        "author": {
          "id": 2,
          "username": "user2",
          "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=user2"
        },
        "likes": 5,
        "createdAt": "2026-01-01T10:30:00.000Z"
      }
    ],
    "total": 500,
    "page": 1,
    "pageSize": 20
  }
}
```

---

### 5. 获取管理员统计数据

**GET** `/admin/stats`

#### 请求头
```
Authorization: Bearer {admin_token}
```

#### 响应示例
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "totalPosts": 1250,
    "totalComments": 3890,
    "totalUsers": 456,
    "activeUsers": 89,
    "todayPosts": 25,
    "todayComments": 78
  }
}
```

---

### 6. 批量删除帖子

**DELETE** `/admin/posts/batch`

#### 请求头
```
Authorization: Bearer {admin_token}
```

#### 请求参数
```json
{
  "postIds": [1, 2, 3, 4, 5]  // 帖子ID数组
}
```

#### 响应示例
```json
{
  "code": 200,
  "message": "批量删除成功",
  "data": {
    "deletedCount": 5
  }
}
```

---

### 7. 批量删除评论

**DELETE** `/admin/comments/batch`

#### 请求头
```
Authorization: Bearer {admin_token}
```

#### 请求参数
```json
{
  "commentIds": [1, 2, 3, 4, 5]  // 评论ID数组
}
```

#### 响应示例
```json
{
  "code": 200,
  "message": "批量删除成功",
  "data": {
    "deletedCount": 5
  }
}
```

---

## 测试建议

### 测试用户账号
```json
{
  "username": "testuser",
  "password": "test123456",
  "email": "test@animehub.com"
}
```

### 管理员测试账号
```json
{
  "username": "admin",
  "password": "admin123",
  "email": "admin@animehub.com",
  "isAdmin": true
}
```

### Mock数据建议
- 创建10-20个测试用户
- 生成50-100条测试帖子
- 为帖子添加随机评论和点赞
- 使用随机动漫相关内容作为测试数据
- 至少创建1个管理员账号用于测试

---

**文档版本**: v1.1.0  
**最后更新**: 2026-01-01  
**联系方式**: dev@animehub.com
