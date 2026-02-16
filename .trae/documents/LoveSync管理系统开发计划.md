<!-- @format -->

# LoveSync 后台管理系统开发计划

## 📋 项目基础信息

### 技术栈

- **后端**: Django 4.2 + Django REST Framework + JWT + MySQL

- **数据库**: `lovesync_diary` (数据库名)

- **前端**: Vue 2 + Element UI + Axios

- **管理系统**:
  - 后端: `sys_backend` (独立Django项目，端口8001)

  - 前端: `sys_frontend` (Vue2项目，已配置跨域代理)

原项目目录&#x20;

backend  根据原项目的视图代码和数据库模型，创建相应的后台管理接口

## 🎯 开发策略

采用**模块化开发**，逐个完成功能模块，确保每个模块都经过充分测试后再进行下一个。

## 📦 功能模块拆分

### 第一阶段：用户管理模块

**预计时间**: 3-4天

#### 后端开发 (sys_backend)

1. **创建user_manage应用**
   - 路径: `sys_backend/apps/user_manage/`

   - 接口前缀: `/admin-api/user/`

2. **API接口开发**
   - `GET /admin-api/user/list` - 分页查询用户（支持搜索和筛选）

   - `PUT /admin-api/user/status/{id}` - 修改用户状态

   - `DELETE /admin-api/user/{id}` - 删除用户（管理员权限）

   - `GET /admin-api/user/detail/{id}` - 用户详情

3. **技术要求**
   - 使用DRF ViewSet实现

   - JWT认证 + 管理员权限验证

   - 包含分页、搜索、筛选功能

#### 前端开发 (sys_frontend)

1. **用户列表页面**
   - 路径: `sys_frontend/src/views/user/UserList.vue`

   - 组件: Element UI Table + 搜索框 + 操作按钮

2. **功能实现**
   - 用户列表展示（分页）

   - 搜索功能（用户名/邮箱）

   - 状态管理（启用/禁用）

   - 删除操作（二次确认）

   - 加载状态和错误处理

### 第二阶段：动态管理模块

**预计时间**: 3-4天

#### 后端开发

1. **moment_manage应用**
   - 路径: `sys_backend/apps/moment_manage/`

   - 接口前缀: `/admin-api/moment/`

2. **API接口**
   - `GET /admin-api/moment/list` - 动态列表（支持状态筛选）

   - `PUT /admin-api/moment/status/{id}` - 审核动态

   - `DELETE /admin-api/moment/{id}` - 删除动态

   - `GET /admin-api/moment/detail/{id}` - 动态详情

#### 前端开发

1. **动态列表页面**
   - 路径: `sys_frontend/src/views/moment/MomentList.vue`

   - 包含内容预览、图片展示、审核状态

2. **审核功能**
   - 批量审核操作

   - 审核历史记录

   - 内容违规标记

### 第三阶段：数据统计模块

**预计时间**: 2-3天

#### 后端开发

1. **dashboard应用**
   - 用户增长统计

   - 动态发布统计

   - 活跃度分析

#### 前端开发

1. **仪表板页面**
   - 数据可视化图表

   - 关键指标展示

   - 趋势分析

### 第四阶段：系统管理模块

**预计时间**: 2-3天

#### 功能包括

- 管理员账号管理

- 系统日志查看

- 配置参数管理

- 数据备份恢复

## 🔧 开发环境准备

### 后端环境设置

```bash
cd sys_backend
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8001
```

### 前端环境设置

```bash
cd sys_frontend
npm install
npm run serve
```

## ✅ 质量保障措施

### 1. 代码规范

- 遵循PEP8规范（Python）

- 使用ESLint（JavaScript）

- 添加必要的注释和文档

### 2. 测试要求

- 每个API都需要测试

- 前端页面功能完整测试

- 边界条件处理

### 3. 安全检查

- 权限验证（管理员权限）

- 输入验证和过滤

- SQL注入防护

- XSS防护

## 📅 开发时间表

| 阶段 | 模块         | 预计时间 | 状态   |
| ---- | ------------ | -------- | ------ |
| 1    | 用户管理模块 | 3-4天    | 待开始 |
| 2    | 动态管理模块 | 3-4天    | 待开始 |
| 3    | 数据统计模块 | 2-3天    | 待开始 |
| 4    | 系统管理模块 | 2-3天    | 待开始 |

## 🚀 下一步行动

**立即开始第一阶段：用户管理模块**

1. 我先创建用户管理后端API
2. 然后开发对应的Vue前端页面
3. 进行完整的功能测试

请确认这个开发计划，我立即开始执行！
