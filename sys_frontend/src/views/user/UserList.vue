<template>
  <div class="user-list">
    <!-- 页面标题和操作区 -->
    <div class="page-header">
      <div class="header-right">
        <div class="page-stats">
          <el-tag class="stat-tag info-tag" type="info" effect="light">
            <i class="el-icon-user"></i>
            <span>总用户数: {{ stats.total_users }}</span>
          </el-tag>
          <el-tag class="stat-tag success-tag" type="success" effect="light">
            <i class="el-icon-check"></i>
            <span>活跃用户: {{ stats.active_users }}</span>
          </el-tag>
          <el-tag class="stat-tag warning-tag" type="warning" effect="light">
            <i class="el-icon-close"></i>
            <span>禁用用户: {{ stats.inactive_users }}</span>
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 搜索和操作栏 -->
    <div class="search-section">
      <el-card class="search-card">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-input v-model="searchForm.search" placeholder="请输入用户名或邮箱" clearable @clear="handleSearch"
              @keyup.enter="handleSearch" class="search-input">
              <template #prefix>
                <i class="el-icon-search"></i>
              </template>
            </el-input>
          </el-col>
          <el-col :span="6">
            <el-select v-model="searchForm.is_active" placeholder="用户状态" clearable @change="handleSearch"
              class="status-select">
              <el-option label="全部" value=""></el-option>
              <el-option label="启用" :value="true"></el-option>
              <el-option label="禁用" :value="false"></el-option>
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-select v-model="searchForm.role" placeholder="用户角色" clearable @change="handleSearch"
              class="role-select">
              <el-option label="全部" value=""></el-option>
              <el-option label="超级管理员" value="superuser"></el-option>
              <el-option label="管理员" value="staff"></el-option>
              <el-option label="普通用户" value="normal"></el-option>
            </el-select>
          </el-col>
          <el-col :span="4">
            <div class="button-group">
              <el-button type="primary" class="search-btn" @click="handleSearch">
                <i class="el-icon-search"></i>
                <span>搜索</span>
              </el-button>
              <el-button class="reset-btn" @click="handleReset">
                <i class="el-icon-refresh"></i>
                <span>重置</span>
              </el-button>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 用户列表表格 -->
    <div class="table-section">
      <el-card class="table-card">
        <div class="header-info">
          <el-tag size="small">总计: {{ total }} 个用户</el-tag>
        </div>

        <el-table v-loading="loading" :data="userList" border style="width: 100%"
          @selection-change="handleSelectionChange" class="user-table">
          <el-table-column type="selection" width="55"></el-table-column>
          <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
          <el-table-column prop="username" label="手机号" min-width="120"></el-table-column>
          <el-table-column prop="name" label="姓名" min-width="120"></el-table-column>
          <el-table-column prop="email" label="邮箱" min-width="180"></el-table-column>
          <el-table-column label="状态" width="120" align="center">
            <template slot-scope="scope">
              <el-tag :type="parseInt(scope.row.is_active) === 1 ? 'success' : 'danger'" effect="plain"
                class="status-tag">
                {{ parseInt(scope.row.is_active) === 1 ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="创建时间" width="200" align="center">
            <template slot-scope="scope">
              <span>{{ formatDateTime(scope.row.date_joined) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="220" fixed="right" align="center">
            <template slot-scope="scope">
              <el-button size="mini" :type="parseInt(scope.row.is_active) === 1 ? 'danger' : 'success'"
                @click="handleStatusToggle(scope.row)" class="action-btn status-btn">
                {{ parseInt(scope.row.is_active) === 1 ? '禁用' : '启用' }}
              </el-button>
              <el-button size="mini" type="primary" @click="handleViewDetail(scope.row)" class="action-btn detail-btn">
                详情
              </el-button>
              <el-button v-if="!scope.row.is_superuser" size="mini" type="danger" @click="handleDelete(scope.row)"
                class="action-btn delete-btn">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange"
            :current-page="currentPage" :page-sizes="[10, 20, 50, 100]" :page-size="pageSize"
            layout="total, sizes, prev, pager, next, jumper" :total="total" class="pagination"></el-pagination>
        </div>
      </el-card>
    </div>

    <!-- 用户详情对话框 -->
    <el-dialog title="用户详情" :visible.sync="detailDialogVisible" width="700px" :modal="false" class="detail-dialog">
      <div v-if="currentUser" class="user-detail">
        <div class="detail-header">
          <h3 class="detail-title">{{ currentUser.name }} ({{ currentUser.username }})</h3>
          <el-tag :type="parseInt(currentUser.is_active) === 1 ? 'success' : 'danger'">
            {{ parseInt(currentUser.is_active) === 1 ? '启用' : '禁用' }}
          </el-tag>
        </div>
        <el-descriptions :column="2" border class="detail-descriptions">
          <el-descriptions-item label="用户ID">{{ currentUser.id }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ currentUser.username }}</el-descriptions-item>
          <el-descriptions-item label="姓名">{{ currentUser.name }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ currentUser.email }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDateTime(currentUser.date_joined) }}</el-descriptions-item>
          <el-descriptions-item label="最后登录">{{ formatDateTime(currentUser.last_login) }}</el-descriptions-item>
          <el-descriptions-item label="用户角色">
            <el-tag :type="currentUser.is_superuser ? 'danger' : currentUser.is_staff ? 'warning' : 'info'">
              {{ currentUser.is_superuser ? '超级管理员' : currentUser.is_staff ? '管理员' : '普通用户' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="账号状态">
            <el-tag :type="parseInt(currentUser.is_active) === 1 ? 'success' : 'danger'">
              {{ parseInt(currentUser.is_active) === 1 ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button class="close-btn" @click="detailDialogVisible = false">关闭</el-button>
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
    // 格式化时间为年月日时分秒
    formatDateTime(timeString) {
      if (!timeString) return '无';
      const date = new Date(timeString);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      const seconds = String(date.getSeconds()).padStart(2, '0');
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    },

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
      const isActive = parseInt(row.is_active) === 1
      const action = isActive ? '禁用' : '启用'
      try {
        await this.$confirm(`确定要${action}用户 "${row.username}" 吗？`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        const response = await updateUserStatus(row.id, {})
        if (response.data) {
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
        // 204 No Content 表示删除成功
        if (response.status === 204) {
          this.$message.success('删除成功')
          this.loadUserList()
          this.loadUserStats()
        } else if (response.data.success) {
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
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;

  .header-left {
    .page-title {
      font-size: 24px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 4px 0;
    }

    .page-subtitle {
      font-size: 14px;
      color: #909399;
      margin: 0;
    }
  }

  .header-right {
    .page-stats {
      display: flex;
      gap: 16px;

      .stat-tag {
        font-size: 13px;
        padding: 8px 12px;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        i {
          margin-right: 6px;
        }
      }
    }
  }
}

.search-section {
  margin-bottom: 24px;

  .search-card {
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
    transition: box-shadow 0.3s ease;

    &:hover {
      box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.08);
    }

    .el-row {
      align-items: center;
      padding: 4px 0;
    }

    .search-input,
    .status-select,
    .role-select {
      width: 100%;
    }

    .button-group {
      display: flex;
      gap: 10px;

      .search-btn {
        margin-right: 0;
      }
    }
  }
}

.table-section {
  .table-card {
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
    overflow: hidden;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 20px;
      background-color: #fafafa;
      border-bottom: 1px solid #e4e7ed;

      .card-title {
        font-size: 16px;
        font-weight: 500;
        color: #303133;
      }

      .card-count {
        font-size: 14px;
        color: #909399;
      }
    }

    .user-table {
      border-radius: 0;

      .el-table__header-wrapper th {
        background-color: #fafafa;
        font-weight: 500;
        color: #303133;
      }

      .el-table__body-wrapper tr {
        transition: background-color 0.2s ease;

        &:hover {
          background-color: #f5f7fa !important;
        }
      }

      .status-tag {
        font-size: 12px;
        padding: 2px 10px;
        border-radius: 10px;
      }

      .action-btn {
        font-size: 12px;
        padding: 6px 12px;
        border-radius: 4px;
        margin-right: 8px;
        transition: all 0.3s ease;

        &:hover {
          transform: translateY(-1px);
        }
      }
    }
  }
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;

  .pagination {
    display: flex;
    justify-content: flex-end;
  }
}

.detail-dialog {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;

  .el-dialog__header {
    background-color: #fafafa;
    border-bottom: 1px solid #e4e7ed;
    padding: 16px 20px;
  }

  .el-dialog__title {
    font-size: 16px;
    font-weight: 500;
    color: #303133;
  }

  .el-dialog__body {
    padding: 24px;
  }

  .el-dialog__footer {
    background-color: #fafafa;
    border-top: 1px solid #e4e7ed;
    padding: 16px 20px;
    text-align: right;
  }
}

.user-detail {
  .detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid #e4e7ed;

    .detail-title {
      font-size: 18px;
      font-weight: 500;
      color: #303133;
      margin: 0;
    }
  }

  .detail-descriptions {
    margin-bottom: 20px;

    .el-descriptions__label {
      font-weight: 500;
      color: #606266;
    }

    .el-descriptions__content {
      color: #303133;
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
    padding-bottom: 16px;
  }
}

@media (max-width: 768px) {
  .user-list {
    padding: 12px;
  }

  .page-header {
    .header-right {
      .page-stats {
        flex-wrap: wrap;
        gap: 8px;

        .stat-tag {
          font-size: 12px;
          padding: 6px 10px;
        }
      }
    }
  }

  .search-card {
    .el-row {
      .el-col {
        margin-bottom: 12px;

        &:last-child {
          margin-bottom: 0;
        }
      }
    }
  }

  .table-card {
    .user-table {
      .action-btn {
        margin-right: 4px;
        padding: 4px 8px;
        font-size: 11px;
      }
    }
  }

  .detail-dialog {
    width: 90% !important;

    .el-dialog__body {
      padding: 16px;
    }
  }
}
</style>