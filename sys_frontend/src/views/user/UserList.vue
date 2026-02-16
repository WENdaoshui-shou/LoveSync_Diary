<template>
  <div class="user-list">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">用户管理</h2>
      <div class="page-stats">
        <el-tag type="info">总用户数: {{ stats.total_users }}</el-tag>
        <el-tag type="success">活跃用户: {{ stats.active_users }}</el-tag>
        <el-tag type="warning">禁用用户: {{ stats.inactive_users }}</el-tag>
      </div>
    </div>

    <!-- 搜索和操作栏 -->
    <el-card class="search-card">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-input v-model="searchForm.search" placeholder="请输入用户名或邮箱" clearable @clear="handleSearch"
            @keyup.enter="handleSearch">
            <template #prefix>
              <i class="el-icon-search"></i>
            </template>
          </el-input>
        </el-col>
        <el-col :span="6">
          <el-select v-model="searchForm.is_active" placeholder="用户状态" clearable @change="handleSearch">
            <el-option label="全部" value=""></el-option>
            <el-option label="启用" :value="true"></el-option>
            <el-option label="禁用" :value="false"></el-option>
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="searchForm.role" placeholder="用户角色" clearable @change="handleSearch">
            <el-option label="全部" value=""></el-option>
            <el-option label="超级管理员" value="superuser"></el-option>
            <el-option label="管理员" value="staff"></el-option>
            <el-option label="普通用户" value="normal"></el-option>
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 用户列表表格 -->
    <el-card class="table-card">
      <el-table v-loading="loading" :data="userList" border style="width: 100%"
        @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column prop="username" label="手机号" min-width="120"></el-table-column>
        <el-table-column prop="name" label="姓名" min-width="120"></el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="180"></el-table-column>
        <el-table-column prop="status_display" label="状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180"></el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template slot-scope="scope">
            <el-button size="mini" :type="scope.row.is_active ? 'danger' : 'success'"
              @click="handleStatusToggle(scope.row)">
              {{ scope.row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button size="mini" type="primary" @click="handleViewDetail(scope.row)">详情</el-button>
            <el-button v-if="!scope.row.is_superuser" size="mini" type="danger"
              @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange" :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]" :page-size="pageSize" layout="total, sizes, prev, pager, next, jumper"
          :total="total"></el-pagination>
      </div>
    </el-card>

    <!-- 用户详情对话框 -->
    <el-dialog title="用户详情" :visible.sync="detailDialogVisible" width="600px">
      <div v-if="currentUser" class="user-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ currentUser.id }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ currentUser.username }}</el-descriptions-item>
          <el-descriptions-item label="姓名">{{ currentUser.name }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ currentUser.email }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ currentUser.status_display }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentUser.create_time }}</el-descriptions-item>
          <el-descriptions-item label="最后登录">{{ currentUser.last_login_time }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getUserList, updateUserStatus, deleteUser, getUserStats } from '@/api/user'

export default {
  name: 'UserList',
  data() {
    return {
      loading: false,
      userList: [],
      total: 0,
      currentPage: 1,
      pageSize: 20,
      searchForm: {
        search: '',
        is_active: '',
        role: ''
      },
      detailDialogVisible: false,
      currentUser: null,
      stats: {
        total_users: 0,
        active_users: 0,
        inactive_users: 0
      }
    }
  },
  created() {
    this.loadUserList()
    this.loadUserStats()
  },
  methods: {
    // 加载用户列表
    async loadUserList() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize,
          ...this.searchForm
        }
        const response = await getUserList(params)
        if (response.data) {
          // 检查是否是分页数据格式
          if (response.data.results !== undefined) {
            this.userList = response.data.results
            this.total = response.data.count || response.data.results.length || 0
          } else {
            // 标准响应格式
            if (response.data.success) {
              this.userList = response.data.results || response.data.data
              this.total = response.data.count || response.data.total
            } else {
              this.$message.error(response.data.message || '获取用户列表失败')
            }
          }
        } else {
          this.$message.error('获取用户列表失败')
        }
      } catch (error) {
        this.$message.error('加载用户列表失败')
      } finally {
        this.loading = false
      }
    },

    // 加载用户统计
    async loadUserStats() {
      try {
        const response = await getUserStats()
        if (response.data) {
          // 检查是否有统计数据
          if (response.data.data !== undefined) {
            this.stats = response.data.data
          } else {
            // 直接返回数据
            this.stats = response.data
          }
        }
      } catch (error) {
        // 静默处理统计错误
      }
    },

    // 搜索处理
    handleSearch() {
      this.currentPage = 1
      this.loadUserList()
    },

    // 重置处理
    handleReset() {
      this.searchForm = {
        search: '',
        is_active: '',
        role: ''
      }
      this.handleSearch()
    },

    // 分页处理
    handleSizeChange(val) {
      this.pageSize = val
      this.loadUserList()
    },

    handleCurrentChange(val) {
      this.currentPage = val
      this.loadUserList()
    },

    // 状态切换
    async handleStatusToggle(row) {
      const action = row.is_active ? '禁用' : '启用'
      try {
        await this.$confirm(`确定要${action}用户 "${row.username}" 吗？`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        const response = await updateUserStatus(row.id, { is_active: !row.is_active })
        if (response.data.success) {
          this.$message.success(`${action}成功`)
          this.loadUserList()
          this.loadUserStats()
        } else {
          this.$message.error(response.data.message || `${action}失败`)
        }
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error(`${action}失败`)
        }
      }
    },

    // 查看详情
    handleViewDetail(row) {
      this.currentUser = row
      this.detailDialogVisible = true
    },

    // 删除用户
    async handleDelete(row) {
      try {
        await this.$confirm(`确定要删除用户 "${row.username}" 吗？此操作不可恢复！`, '警告', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        const response = await deleteUser(row.id)
        if (response.data.success) {
          this.$message.success('删除成功')
          this.loadUserList()
          this.loadUserStats()
        } else {
          this.$message.error(response.data.message || '删除失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('删除失败')
        }
      }
    },

    // 表格选择处理
    handleSelectionChange(val) {
      this.selectedUsers = val
    }
  }
}
</script>

<style lang="scss" scoped>
.user-list {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: calc(100vh - 84px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  .page-title {
    font-size: 24px;
    font-weight: 500;
    color: #303133;
    margin: 0;
  }

  .page-stats {
    display: flex;
    gap: 10px;
  }
}

.search-card {
  margin-bottom: 20px;

  .el-row {
    align-items: center;
  }
}

.table-card {
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.user-detail {
  padding: 20px;

  .el-descriptions {
    margin-bottom: 20px;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .user-list {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;

    .page-stats {
      flex-wrap: wrap;
    }
  }

  .search-card .el-col {
    margin-bottom: 10px;
  }
}
</style>