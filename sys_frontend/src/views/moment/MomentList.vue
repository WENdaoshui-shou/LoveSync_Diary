<template>
  <div class="moment-list">

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="statistics-row">
      <el-col :span="6">
        <el-card class="statistics-card">
          <div class="statistics-item">
            <div class="statistics-label">总动态数</div>
            <div class="statistics-value">{{ statistics.total_moments || 0 }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="statistics-card">
          <div class="statistics-item">
            <div class="statistics-label">已分享动态</div>
            <div class="statistics-value">{{ statistics.shared_moments || 0 }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="statistics-card">
          <div class="statistics-item">
            <div class="statistics-label">今日新增</div>
            <div class="statistics-value">{{ statistics.today_moments || 0 }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="statistics-card">
          <div class="statistics-item">
            <div class="statistics-label">本周新增</div>
            <div class="statistics-value">{{ statistics.week_moments || 0 }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="搜索">
          <el-input v-model="filterForm.search" placeholder="搜索动态内容、用户名、邮箱" clearable @clear="handleSearch"
            @keyup.enter="handleSearch" style="width: 250px">
            <el-button slot="append" icon="el-icon-search" @click="handleSearch"></el-button>
          </el-input>
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable @change="handleSearch"
            style="width: 110px">
            <el-option label="全部" value=""></el-option>
            <el-option label="已分享" value="shared"></el-option>
            <el-option label="未分享" value="unshared"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="时间范围">
          <el-select v-model="filterForm.date_range" placeholder="全部时间" clearable @change="handleSearch"
            style="width: 110px">
            <el-option label="全部" value=""></el-option>
            <el-option label="今天" value="today"></el-option>
            <el-option label="本周" value="week"></el-option>
            <el-option label="本月" value="month"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="排序">
          <el-select v-model="filterForm.hot" placeholder="默认排序" clearable @change="handleSearch" style="width: 110px">
            <el-option label="默认排序" value=""></el-option>
            <el-option label="热度最高" value="high"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 动态列表 -->
    <el-card class="list-card">
      <el-table :data="momentList" v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>

        <el-table-column label="用户信息" min-width="150">
          <template slot-scope="scope">
            <div class="user-info" v-if="scope.row">
              <div class="user-name">{{ scope.row.name }}</div>
              <div class="user-email">{{ scope.row.email }}</div>
            </div>
            <div v-else>用户数据缺失</div>
          </template>
        </el-table-column>

        <el-table-column label="动态内容" min-width="300">
          <template slot-scope="scope">
            <div class="moment-content" v-if="scope.row">
              <div class="content-text">
                <template v-if="scope.row.content && scope.row.content.length > 100">
                  <span v-if="!scope.row.showFullContent">{{ scope.row.content.substring(0, 100) }}...</span>
                  <span v-else>{{ scope.row.content }}</span>
                  <el-button type="text" size="mini" @click="scope.row.showFullContent = !scope.row.showFullContent"
                    class="expand-btn">
                    {{ scope.row.showFullContent ? '收起' : '展开' }}
                  </el-button>
                </template>
                <template v-else>
                  {{ scope.row.content || '无内容' }}
                </template>
              </div>
              <div class="content-images" v-if="scope.row.images && scope.row.images.length > 0">
                <el-image v-for="(image, index) in scope.row.images.slice(0, 3)" :key="index" :src="image"
                  :preview-src-list="scope.row.images" fit="cover" class="content-image"></el-image>
                <span v-if="scope.row.images.length > 3" class="image-count">+{{ scope.row.images.length - 3 }}</span>
              </div>
              <div class="content-tags" v-if="scope.row.tags && scope.row.tags.length > 0">
                <el-tag v-for="tag in scope.row.tags" :key="tag" size="mini" type="info" class="content-tag">{{ tag
                }}</el-tag>
              </div>
            </div>
            <div v-else>动态数据缺失</div>
          </template>
        </el-table-column>

        <el-table-column label="互动数据" width="120" align="center">
          <template slot-scope="scope">
            <div class="interaction-stats" v-if="scope.row">
              <div class="stat-item">
                <span class="like-icon">♡</span>
                <span>{{ scope.row.likes }}</span>
              </div>
              <div class="stat-item">
                <i class="el-icon-chat-dot-round"></i>
                <span>{{ scope.row.comments }}</span>
              </div>
              <div class="stat-item">
                <i class="el-icon-star-off"></i>
                <span>{{ scope.row.favorites }}</span>
              </div>
              <div class="stat-item">
                <i class="el-icon-view"></i>
                <span>{{ scope.row.view_count }}</span>
              </div>
            </div>
            <div v-else>数据缺失</div>
          </template>
        </el-table-column>

        <el-table-column label="发布时间" width="200" align="center">
          <template slot-scope="scope">
            <span>{{ formatDateTime(scope.row.created_at) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="80" align="center">
          <template slot-scope="scope">
            <el-tag v-if="scope.row" :type="scope.row.is_shared ? 'success' : 'info'" size="mini">
              {{ scope.row.is_shared ? '已分享' : '未分享' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template slot-scope="scope">
            <div class="action-buttons" v-if="scope.row">
              <el-button type="primary" size="mini" @click="viewDetail(scope.row)"
                class="action-btn detail-btn">详情</el-button>
              <el-button :type="scope.row.is_shared ? 'warning' : 'success'" size="mini" @click="toggleShare(scope.row)"
                class="action-btn share-btn">{{ scope.row.is_shared ? '取消分享' : '分享' }}</el-button>
              <el-button type="danger" size="mini" @click="deleteMoment(scope.row)"
                class="action-btn delete-btn">删除</el-button>
            </div>
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

    <!-- 动态详情对话框 -->
    <el-dialog title="动态详情" :visible.sync="detailDialogVisible" width="800px" top="5vh" :modal="false">
      <div v-if="currentMoment" class="moment-detail">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="detail-section">
              <h4>基本信息</h4>
              <el-form label-width="100px">
                <el-form-item label="动态ID:">{{ currentMoment.id }}</el-form-item>
                <el-form-item label="发布者:">{{ currentMoment.name || currentMoment.username }} ({{ currentMoment.username
                }})</el-form-item>
                <el-form-item label="邮箱:">{{ currentMoment.email }}</el-form-item>
                <el-form-item label="发布时间:">{{ formatDateTime(currentMoment.created_at) }}</el-form-item>
                <el-form-item label="状态:">
                  <el-tag v-if="currentMoment" :type="currentMoment.is_shared ? 'success' : 'info'" size="small">
                    {{ currentMoment.is_shared ? '已分享' : '未分享' }}
                  </el-tag>
                </el-form-item>
                <el-form-item label="热度值:">{{ currentMoment.hot_score ? currentMoment.hot_score.toFixed(2) : '0.00'
                  }}</el-form-item>
              </el-form>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="detail-section">
              <h4>互动数据</h4>
              <el-form label-width="100px">
                <el-form-item label="点赞数:">{{ currentMoment.likes }}</el-form-item>
                <el-form-item label="评论数:">{{ currentMoment.comments }}</el-form-item>
                <el-form-item label="收藏数:">{{ currentMoment.favorites }}</el-form-item>
                <el-form-item label="浏览数:">{{ currentMoment.view_count }}</el-form-item>
              </el-form>
            </div>
          </el-col>
        </el-row>

        <div class="detail-section">
          <h4>动态内容</h4>
          <div class="content-detail">{{ currentMoment.content }}</div>
        </div>

        <div class="detail-section" v-if="currentMoment.images && currentMoment.images.length > 0">
          <h4>图片</h4>
          <div class="image-list">
            <el-image v-for="(image, index) in currentMoment.images" :key="index" :src="image.url"
              :preview-src-list="currentMoment.images.map(img => img.url)" fit="cover"
              style="width: 100px; height: 100px; margin-right: 10px; margin-bottom: 10px; cursor: pointer;"></el-image>
          </div>
        </div>

        <div class="detail-section" v-if="currentMoment.tags && currentMoment.tags.length > 0">
          <h4>标签</h4>
          <div class="tag-list">
            <el-tag v-for="tag in currentMoment.tags" :key="tag.id" size="small"
              style="margin-right: 10px; margin-bottom: 5px;">{{ tag.name }}</el-tag>
          </div>
        </div>

        <div class="detail-section" v-if="comments && comments.length > 0">
          <h4>评论 ({{ comments.length }})</h4>
          <div class="comment-list">
            <div v-for="comment in validComments" :key="comment.id" class="comment-item">
              <div class="comment-header" v-if="comment.user">
                <span class="comment-user">{{ comment.user.name }} ({{ comment.user.username }})</span>
                <span class="comment-time">{{ formatDateTime(comment.created_at) }}</span>
              </div>
              <div class="comment-content" v-if="comment.content">{{ comment.content }}</div>
              <div class="comment-stats" v-if="comment.likes !== undefined">
                <span><span class="like-icon">♡</span> {{ comment.likes }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div slot="footer" class="dialog-footer">
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button v-if="currentMoment" :type="currentMoment.is_shared ? 'warning' : 'success'"
          @click="toggleShare(currentMoment)">{{
            currentMoment.is_shared ? '取消分享' : '分享' }}</el-button>
        <el-button type="danger" @click="deleteMoment(currentMoment)">删除动态</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getMomentList, getMomentDetail, toggleMomentShare, deleteMoment, getMomentStatistics } from '@/api/moment'

export default {
  name: 'MomentList',
  data() {
    return {
      loading: false,
      momentList: [],
      total: 0,
      currentPage: 1,
      pageSize: 10,
      filterForm: {
        search: '',
        status: '',
        date_range: '',
        hot: ''
      },
      statistics: {
        total_moments: 0,
        shared_moments: 0,
        today_moments: 0,
        week_moments: 0
      },
      detailDialogVisible: false,
      currentMoment: null,
      comments: []
    }
  },
  computed: {
    // 计算属性：有效的评论
    validComments() {
      return this.comments ? this.comments.filter(comment => comment && comment.user) : []
    }
  },
  created() {
    this.loadData()
    this.loadStatistics()
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

    // 加载数据
    async loadData() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize,
          ...this.filterForm
        }
        const response = await getMomentList(params)
        if (response.data) {
          // 检查是否是分页数据格式
          if (response.data.results !== undefined) {
            this.momentList = response.data.results
            this.total = response.data.count || response.data.results.length || 0
          } else {
            // 标准响应格式
            if (response.data.code === 200) {
              this.momentList = response.data.data.results || response.data.data
              this.total = response.data.data.count || response.data.data.length || 0
            } else {
              this.$message.error(response.data.message || '获取动态列表失败')
            }
          }
        } else {
          this.$message.error('获取动态列表失败')
        }
      } catch (error) {
        this.$message.error('加载动态列表失败')
      } finally {
        this.loading = false
      }
    },

    // 加载统计信息
    async loadStatistics() {
      try {
        const response = await getMomentStatistics()
        if (response.data) {
          // 适配后端返回的格式
          this.statistics = {
            total_moments: response.data.total_moments || 0,
            shared_moments: response.data.total_shared || 0,
            today_moments: 0, // 后端暂时没有返回今日新增
            week_moments: 0 // 后端暂时没有返回本周新增
          }
        }
      } catch (error) {
        console.error('获取统计数据失败:', error)
      }
    },

    // 搜索
    handleSearch() {
      this.currentPage = 1
      this.loadData()
    },

    // 重置筛选
    resetFilter() {
      this.filterForm = {
        search: '',
        status: '',
        date_range: '',
        hot: ''
      }
      this.currentPage = 1
      this.loadData()
    },

    // 分页
    handleSizeChange(val) {
      this.pageSize = val
      this.loadData()
    },

    handleCurrentChange(val) {
      this.currentPage = val
      this.loadData()
    },

    // 查看详情
    async viewDetail(row) {
      try {
        const response = await getMomentDetail(row.id)
        if (response.data) {
          // 适配后端返回的格式
          this.currentMoment = response.data
          // 后端返回的comments是数字，需要初始化为空数组
          this.comments = []
          this.detailDialogVisible = true
        } else {
          this.$message.error('获取动态详情失败')
        }
      } catch (error) {
        console.error('获取动态详情失败:', error)
        this.$message.error('获取动态详情失败')
      }
    },

    // 切换分享状态
    async toggleShare(row) {
      try {
        const response = await toggleMomentShare(row.id)
        if (response.data) {
          // 适配后端返回的格式
          this.$message.success('操作成功')
          // 直接切换状态，因为API返回的是更新后的数据
          row.is_shared = response.data.is_shared
          // 如果在详情页，也更新详情数据
          if (this.currentMoment && this.currentMoment.id === row.id) {
            this.currentMoment.is_shared = response.data.is_shared
          }
          // 重新加载统计信息
          this.loadStatistics()
        } else {
          this.$message.error('操作失败')
        }
      } catch (error) {
        console.error('切换分享状态失败:', error)
        this.$message.error('操作失败')
      }
    },

    // 删除动态
    deleteMoment(row) {
      this.$confirm('确定要删除这条动态吗？此操作不可恢复。', '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          const response = await deleteMoment(row.id)
          // 204 No Content 表示删除成功
          if (response.status === 204) {
            this.$message.success('动态删除成功')
            this.loadData()
            this.loadStatistics()
            // 如果删除的是当前查看详情的动态，关闭详情对话框
            if (this.currentMoment && this.currentMoment.id === row.id) {
              this.detailDialogVisible = false
            }
          } else if (response.data) {
            this.$message.success('动态删除成功')
            this.loadData()
            this.loadStatistics()
            // 如果删除的是当前查看详情的动态，关闭详情对话框
            if (this.currentMoment && this.currentMoment.id === row.id) {
              this.detailDialogVisible = false
            }
          } else {
            this.$message.error('删除失败')
          }
        } catch (error) {
          console.error('删除动态失败:', error)
          this.$message.error('删除失败')
        }
      }).catch(() => {
        // 用户取消删除
      })
    }
  }
}
</script>

<style lang="scss" scoped>
// 变量定义
$primary-color: #409EFF;
$success-color: #67C23A;
$warning-color: #E6A23C;
$danger-color: #F56C6C;
$info-color: #909399;
$text-color: #303133;
$text-color-secondary: #606266;
$border-color: #e4e7ed;
$bg-color: #f5f5f5;
$card-bg: #ffffff;
$hover-bg: #f5f7fa;
$shadow-base: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
$shadow-hover: 0 4px 16px 0 rgba(0, 0, 0, 0.08);
$border-radius: 8px;
$transition-base: all 0.3s ease;

// 基础样式
.moment-list {
  padding: 20px;
  background-color: $bg-color;
  min-height: calc(100vh - 84px);
}

// 页面标题和操作区
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid $border-color;

  .page-title {
    font-size: 24px;
    font-weight: 600;
    color: $text-color;
    margin: 0 0 4px 0;
  }

  .page-subtitle {
    font-size: 14px;
    color: $info-color;
    margin: 0;
  }
}

// 统计卡片
.statistics-row {
  margin-bottom: 24px;
}

// 操作按钮
.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
}

.action-btn {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 4px;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
}

.detail-btn {
  background-color: #409EFF;
  border-color: #409EFF;

  &:hover {
    background-color: #66b1ff;
    border-color: #66b1ff;
  }
}

.share-btn {
  &.el-button--success {
    background-color: #67C23A;
    border-color: #67C23A;

    &:hover {
      background-color: #85ce61;
      border-color: #85ce61;
    }
  }

  &.el-button--warning {
    background-color: #E6A23C;
    border-color: #E6A23C;

    &:hover {
      background-color: #ebb563;
      border-color: #ebb563;
    }
  }
}

.delete-btn {
  background-color: #F56C6C;
  border-color: #F56C6C;

  &:hover {
    background-color: #f78989;
    border-color: #f78989;
  }
}

.statistics-card {
  border-radius: $border-radius;
  box-shadow: $shadow-base;
  transition: box-shadow $transition-base;
  overflow: hidden;

  &:hover {
    box-shadow: $shadow-hover;
  }
}

.statistics-item {
  padding: 20px 0;
  text-align: center;
}

.statistics-label {
  font-size: 14px;
  color: $info-color;
  margin-bottom: 8px;
}

.statistics-value {
  font-size: 28px;
  font-weight: 600;
  color: $text-color;
  transition: $transition-base;

  &:hover {
    transform: scale(1.05);
  }
}

// 搜索和筛选
.filter-card {
  margin-bottom: 24px;
  border-radius: $border-radius;
  box-shadow: $shadow-base;
  transition: box-shadow $transition-base;

  &:hover {
    box-shadow: $shadow-hover;
  }
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  padding: 4px 0;
}

// 动态列表
.list-card {
  margin-bottom: 24px;
  border-radius: $border-radius;
  box-shadow: $shadow-base;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background-color: #fafafa;
  border-bottom: 1px solid $border-color;

  span {
    font-size: 16px;
    font-weight: 500;
    color: $text-color;
  }
}

// 表格样式
.el-table {
  border-radius: 0;

  .el-table__header-wrapper th {
    background-color: #fafafa;
    font-weight: 500;
    color: $text-color;
  }

  .el-table__body-wrapper tr {
    transition: background-color 0.2s ease;

    &:hover {
      background-color: $hover-bg !important;
    }
  }
}

// 用户信息
.user-info {
  line-height: 1.5;
}

.user-name {
  font-weight: 500;
  color: $text-color;
  margin-bottom: 4px;
}

.user-email {
  font-size: 12px;
  color: $info-color;
}

// 动态内容
.moment-content {
  line-height: 1.6;
}

.content-text {
  margin-bottom: 10px;
  word-break: break-word;
  color: $text-color;
  line-height: 1.5;
}

.expand-btn {
  font-size: 12px;
  color: $primary-color;
  margin-left: 5px;
  padding: 0;
  height: auto;
  line-height: inherit;

  &:hover {
    color: #66b1ff;
    text-decoration: underline;
  }
}

.content-images {
  margin-top: 8px;
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.content-image {
  width: 50px;
  height: 50px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s ease;

  &:hover {
    transform: scale(1.05);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
}

.image-count {
  font-size: 12px;
  color: $info-color;
  margin-left: 5px;
  align-self: center;
  background-color: $hover-bg;
  padding: 2px 8px;
  border-radius: 10px;
}

.content-tags {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.content-tag {
  margin-right: 5px !important;
  margin-top: 5px !important;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
}

// 互动数据
.interaction-stats {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: $info-color;
  transition: color 0.2s ease;

  &:hover {
    color: $primary-color;
  }
}

// 分页
.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
}

// 详情对话框
.el-dialog {
  border-radius: $border-radius;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;

  .el-dialog__header {
    background-color: #fafafa;
    border-bottom: 1px solid $border-color;
    padding: 16px 20px;
  }

  .el-dialog__title {
    font-size: 16px;
    font-weight: 500;
    color: $text-color;
  }

  .el-dialog__body {
    padding: 24px;
  }

  .el-dialog__footer {
    background-color: #fafafa;
    border-top: 1px solid $border-color;
    padding: 16px 20px;
    text-align: right;
  }
}

// 详情内容
.moment-detail {
  max-height: 60vh;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 24px;

  h4 {
    margin-bottom: 16px;
    color: $text-color;
    border-bottom: 1px solid $border-color;
    padding-bottom: 10px;
    font-size: 14px;
    font-weight: 500;
  }
}

.content-detail {
  background-color: $hover-bg;
  padding: 16px;
  border-radius: 6px;
  line-height: 1.6;
  word-break: break-word;
  color: $text-color;
  transition: $transition-base;

  &:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  }
}

.image-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

// 评论列表
.comment-list {
  max-height: 300px;
  overflow-y: auto;
}

.comment-item {
  border-bottom: 1px solid $border-color;
  padding: 16px 0;
  transition: $transition-base;

  &:hover {
    background-color: #fafafa;
  }

  &:last-child {
    border-bottom: none;
  }
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.comment-user {
  font-weight: 500;
  color: $text-color;
}

.comment-time {
  font-size: 12px;
  color: $info-color;
}

.comment-content {
  margin-bottom: 10px;
  line-height: 1.5;
  word-break: break-word;
  color: $text-color;
}

.comment-stats {
  font-size: 12px;
  color: $info-color;
  transition: color 0.2s ease;

  &:hover {
    color: $primary-color;
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .moment-list {
    padding: 16px;
  }

  .filter-form {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .statistics-row {
    .el-col {
      margin-bottom: 16px;

      &:last-child {
        margin-bottom: 0;
      }
    }
  }
}

@media (max-width: 768px) {
  .moment-list {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding-bottom: 12px;
  }

  .statistics-row {
    .el-col {
      &:nth-child(n) {
        flex: 1;
        max-width: 100%;
      }
    }
  }

  .list-card {
    .el-table {
      .el-table__body-wrapper {
        .action-btn {
          margin-right: 4px;
          padding: 4px 8px;
          font-size: 11px;
        }
      }
    }
  }

  .el-dialog {
    width: 90% !important;

    .el-dialog__body {
      padding: 16px;
    }
  }
}
</style>