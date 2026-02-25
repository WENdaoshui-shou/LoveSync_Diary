<template>
  <div class="topic-management">

    <!-- 话题统计 -->
    <div class="stats-container">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon">
                <i class="el-icon-chat-dot-round"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ statistics.total_topics || 0 }}</div>
                <div class="stat-label">总话题数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon success">
                <i class="el-icon-sunny"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number text-success">{{ statistics.active_topics || 0 }}</div>
                <div class="stat-label">活跃话题</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon warning">
                <i class="el-icon-fire"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number text-warning">{{ statistics.hot_topics || 0 }}</div>
                <div class="stat-label">热门话题</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon info">
                <i class="el-icon-message"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number text-info">{{ statistics.total_discussions || 0 }}</div>
                <div class="stat-label">总讨论数</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选和搜索 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="搜索">
          <el-input v-model="searchKeyword" placeholder="搜索话题标题或描述" clearable @clear="searchTopics"
            @keyup.enter="searchTopics" style="width: 250px">
            <el-button slot="append" icon="el-icon-search" @click="searchTopics"></el-button>
          </el-input>
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="filterStatus" placeholder="全部状态" clearable @change="searchTopics">
            <el-option label="全部" value=""></el-option>
            <el-option label="活跃" value="active"></el-option>
            <el-option label="热门" value="hot"></el-option>
            <el-option label="普通" value="normal"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="searchTopics">搜索</el-button>
          <el-button @click="resetFilter">重置</el-button>
          <el-button type="primary" @click="createTopic">
              <i class="el-icon-plus"></i> 创建话题
            </el-button>
            <el-button @click="refreshData">
              <i class="el-icon-refresh"></i> 刷新
            </el-button>
        </el-form-item>
        
      </el-form>
    </el-card>

    <!-- 话题列表 -->
    <el-card class="list-card">

      <div class="topic-list">
        <div v-if="loading" class="loading-state">
          <i class="el-icon-loading"></i>
          <p>正在加载话题数据...</p>
        </div>

        <div v-else-if="topics.length === 0" class="empty-state">
          <i class="el-icon-chat-dot-round"></i>
          <p>暂无话题数据</p>
          <el-button type="primary" @click="createTopic" style="margin-top: 20px">
            <i class="el-icon-plus"></i> 创建第一个话题
          </el-button>
        </div>

        <div v-else class="topic-grid">
          <div v-for="topic in topics" :key="topic.id" class="topic-card"
            :class="{ 'hot-topic': topic.heat_level === 3, 'active-topic': topic.status === 'active' }">
            <div class="topic-header">
              <div class="topic-info">
                <div class="topic-title-row">
                  <h4 class="topic-title">{{ topic.title }}</h4>
                  <div class="topic-badges">
                    <el-tag v-if="topic.status === 'hot'" type="danger" size="mini" effect="dark">热门</el-tag>
                    <el-tag v-if="topic.status === 'active'" type="success" size="mini" effect="dark">活跃</el-tag>
                    <el-tag v-if="topic.status === 'normal'" type="info" size="mini" effect="dark">普通</el-tag>
                  </div>
                </div>
                <p class="topic-description">{{ truncateText(topic.description, 80) }}</p>
                <div class="topic-meta">
                  <el-tag :type="getStatusType(topic.status)" size="mini" class="status-tag">
                    {{ getStatusText(topic.status) }}
                  </el-tag>
                  <el-tag :type="getHeatType(topic.heat_level)" size="mini" class="heat-tag">
                    {{ getHeatText(topic.heat_level) }}
                  </el-tag>
                  <div class="topic-stats">
                    <span class="stat-item">
                      <i class="el-icon-view"></i> {{ topic.view_count || 0 }}
                    </span>
                    <span class="stat-item">
                      <i class="el-icon-chat-dot-round"></i> {{ topic.discussion_count || 0 }}
                    </span>
                    <span class="stat-item">
                      <i class="el-icon-thumb"></i> {{ topic.like_count || 0 }}
                    </span>
                  </div>
                </div>
                <div class="topic-time-info">
                  <span class="time-item">
                    <i class="el-icon-time"></i> 创建: {{ formatDate(topic.created_at) }}
                  </span>
                  <span class="time-item" v-if="topic.updated_at !== topic.created_at">
                    <i class="el-icon-refresh"></i> 更新: {{ formatDate(topic.updated_at) }}
                  </span>
                </div>
              </div>
            </div>

            <div class="topic-actions">
              <el-button type="primary" size="mini" plain @click="viewTopic(topic)" class="action-btn">
                <i class="el-icon-view"></i> 查看
              </el-button>
              <el-button type="success" size="mini" plain @click="editTopic(topic)" class="action-btn">
                <i class="el-icon-edit"></i> 编辑
              </el-button>
              <el-button type="danger" size="mini" plain @click="deleteTopic(topic)" class="action-btn">
                <i class="el-icon-delete"></i> 删除
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange" :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]" :page-size="pageSize" layout="total, sizes, prev, pager, next, jumper"
          :total="total" class="pagination"></el-pagination>
      </div>
    </el-card>

    <!-- 创建/编辑话题对话框 -->
    <el-dialog :title="isEditMode ? '编辑话题' : '创建话题'" :visible.sync="dialogVisible" width="500px" :modal="false"
      class="topic-dialog">
      <el-form ref="topicForm" :model="topicForm" :rules="topicRules" label-width="80px">
        <el-form-item label="话题名称" prop="title">
          <el-input v-model="topicForm.title" placeholder="请输入话题名称" maxlength="50"></el-input>
        </el-form-item>
        <el-form-item label="话题描述">
          <el-input v-model="topicForm.description" type="textarea" rows="4" placeholder="请输入话题描述"
            maxlength="200"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitTopic">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {
  getTopicList,
  getTopicDetail,
  createTopic,
  updateTopic,
  deleteTopic,
  getTopicStatistics
} from '@/api/community'

export default {
  name: 'CommunityTopics',
  data() {
    return {
      loading: false,
      statistics: {
        total_topics: 0,
        active_topics: 0,
        hot_topics: 0,
        total_discussions: 0
      },
      topics: [],
      searchKeyword: '',
      filterStatus: '',
      filterHeatLevel: '',
      currentPage: 1,
      pageSize: 10,
      total: 0,
      dialogVisible: false,
      topicForm: {
        title: '',
        description: ''
      },
      topicRules: {
        title: [
          { required: true, message: '请输入话题名称', trigger: 'blur' },
          { min: 2, max: 50, message: '话题名称长度在 2 到 50 个字符', trigger: 'blur' }
        ]
      },
      isEditMode: false,
      currentTopicId: null
    }
  },
  created() {
    this.loadData()
    this.loadStatistics()
  },
  methods: {
    // 加载话题列表
    async loadData() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize,
          search: this.searchKeyword,
          status: this.filterStatus,
          heat_level: this.filterHeatLevel
        }
        const response = await getTopicList(params)
        if (response.data) {
          this.topics = response.data.results || []
          this.total = response.data.count || 0
        }
      } catch (error) {
        this.$message.error('加载话题列表失败')
        console.error('加载话题列表失败:', error)
      } finally {
        this.loading = false
      }
    },

    // 加载统计数据
    async loadStatistics() {
      try {
        const response = await getTopicStatistics()
        if (response.data) {
          this.statistics = response.data
        }
      } catch (error) {
        console.error('加载话题统计数据失败:', error)
      }
    },

    // 搜索话题
    searchTopics() {
      this.currentPage = 1
      this.loadData()
    },

    // 刷新数据
    refreshData() {
      this.loadData()
      this.loadStatistics()
      this.$message.success('数据已刷新')
    },

    // 重置筛选
    resetFilter() {
      this.searchKeyword = ''
      this.filterStatus = ''
      this.filterHeatLevel = ''
      this.currentPage = 1
      this.loadData()
    },

    // 导出话题数据
    exportTopics() {
      this.$confirm('确定要导出话题数据吗？', '导出数据', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }).then(async () => {
        try {
          // 这里可以添加导出API调用
          this.$message.success('数据导出成功，请在下载中心查看')
        } catch (error) {
          console.error('导出数据失败:', error)
          this.$message.error('导出失败，请稍后重试')
        }
      }).catch(() => {
        // 取消导出
      })
    },

    // 获取图标样式类
    getIconClass(status, heatLevel) {
      if (status === 'hot' || heatLevel === 3) {
        return 'hot'
      }
      if (status === 'active') {
        return 'active'
      }
      return ''
    },

    // 文本截断
    truncateText(text, maxLength) {
      if (!text) return ''
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
    },

    // 日期格式化
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    // 创建话题
    createTopic() {
      this.isEditMode = false
      this.topicForm = {
        title: '',
        description: ''
      }
      this.dialogVisible = true
    },

    // 编辑话题
    editTopic(topic) {
      this.isEditMode = true
      this.currentTopicId = topic.id
      this.topicForm = {
        title: topic.title,
        description: topic.description || ''
      }
      this.dialogVisible = true
    },

    // 查看话题详情
    viewTopic(topic) {
      this.$message.info(`查看话题: ${topic.title}`)
    },

    // 删除话题
    deleteTopic(topic) {
      this.$confirm(`确定要删除话题 "${topic.title}" 吗？`, '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await deleteTopic(topic.id)
          this.$message.success('话题已删除')
          this.loadData()
          this.loadStatistics()
        } catch (error) {
          this.$message.error('删除话题失败')
          console.error('删除话题失败:', error)
        }
      }).catch(() => {
        // 取消删除
      })
    },

    // 提交话题表单
    submitTopic() {
      this.$refs.topicForm.validate(async (valid) => {
        if (valid) {
          try {
            if (this.isEditMode) {
              // 更新话题
              await updateTopic(this.currentTopicId, this.topicForm)
              this.$message.success('话题更新成功')
            } else {
              // 创建话题
              await createTopic(this.topicForm)
              this.$message.success('话题创建成功')
            }
            this.dialogVisible = false
            this.loadData()
            this.loadStatistics()
          } catch (error) {
            this.$message.error('操作失败')
            console.error('提交话题表单失败:', error)
          }
        }
      })
    },

    // 分页处理
    handleSizeChange(size) {
      this.pageSize = size
      this.loadData()
    },

    handleCurrentChange(current) {
      this.currentPage = current
      this.loadData()
    },

    // 状态样式
    getStatusType(status) {
      const types = {
        'active': 'success',
        'hot': 'danger',
        'normal': 'info'
      }
      return types[status] || 'info'
    },

    getStatusText(status) {
      const texts = {
        'active': '活跃',
        'hot': '热门',
        'normal': '普通'
      }
      return texts[status] || status
    },

    // 热度样式
    getHeatType(heatLevel) {
      const types = {
        1: 'info',
        2: 'warning',
        3: 'danger'
      }
      return types[heatLevel] || 'info'
    },

    getHeatText(heatLevel) {
      const texts = {
        1: '普通',
        2: '热门',
        3: '火爆'
      }
      return texts[heatLevel] || '未知'
    },

    // 获取话题详情
    getTopicDetail(topicId) {
      getTopicDetail(topicId)
        .then(response => {
          // 这里可以添加获取话题详情后的处理逻辑
          console.log('获取话题详情成功:', response.data)
          // 例如：显示话题详情对话框
          // this.topicDetail = response.data
          // this.topicDialogVisible = true
        })
        .catch(error => {
          this.$message.error('获取话题详情失败: ' + error.message)
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

.topic-management {
  padding: 20px;
  background-color: $bg-color;
  min-height: 100vh;
}

// 页面标题
.page-header {
  margin-bottom: 30px;

  .page-title {
    color: $text-color;
    margin-bottom: 10px;
    font-size: 24px;
    font-weight: 600;
  }

  .page-description {
    color: $info-color;
    margin-bottom: 0;
    font-size: 14px;
  }
}

// 统计卡片
.stats-container {
  margin-bottom: 30px;
}

.stat-card {
  text-align: left;
  border-radius: $border-radius;
  box-shadow: $shadow-base;
  transition: all 0.3s ease;

  &:hover {
    box-shadow: $shadow-hover;
    transform: translateY(-2px);
  }

  .stat-content {
    padding: 24px;
    display: flex;
    align-items: center;
    gap: 20px;

    .stat-icon {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background-color: rgba($primary-color, 0.1);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      color: $primary-color;

      &.success {
        background-color: rgba($success-color, 0.1);
        color: $success-color;
      }

      &.warning {
        background-color: rgba($warning-color, 0.1);
        color: $warning-color;
      }

      &.info {
        background-color: rgba($info-color, 0.1);
        color: $info-color;
      }
    }

    .stat-info {
      flex: 1;

      .stat-number {
        font-size: 32px;
        font-weight: bold;
        color: $text-color;
        margin-bottom: 4px;

        &.text-success {
          color: $success-color;
        }

        &.text-warning {
          color: $warning-color;
        }

        &.text-info {
          color: $info-color;
        }
      }

      .stat-label {
        font-size: 14px;
        color: $info-color;
      }
    }
  }
}

// 筛选卡片
.filter-card {
  margin-bottom: 20px;
  border-radius: $border-radius;
  box-shadow: $shadow-base;

  .filter-form {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 16px;
    padding: 20px;

    @media (max-width: 768px) {
      flex-direction: column;
      align-items: stretch;
    }
  }
}

// 操作按钮
.action-buttons {
  display: flex;
  gap: 10px;
  align-items: center;

  .el-button {
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-1px);
    }
  }
}

// 话题列表
.list-card {
  margin-bottom: 20px;
  border-radius: $border-radius;
  box-shadow: $shadow-base;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid $border-color;

  .card-title {
    font-size: 16px;
    font-weight: 600;
    color: $text-color;
  }

  .card-actions {
    display: flex;
    gap: 10px;
  }
}

// 加载和空状态
.loading-state {
  text-align: center;
  padding: 80px 20px;
  color: $info-color;

  i {
    font-size: 64px;
    margin-bottom: 20px;
    display: block;
    animation: spin 2s linear infinite;
  }

  p {
    margin: 0;
    font-size: 16px;
  }
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: $info-color;

  i {
    font-size: 80px;
    margin-bottom: 20px;
    display: block;
    color: rgba($info-color, 0.5);
  }

  p {
    margin: 0 0 20px 0;
    font-size: 16px;
  }
}

// 话题网格
.topic-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin: 20px 0;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

// 话题卡片
.topic-card {
  background: $card-bg;
  border-radius: $border-radius;
  padding: 16px;
  box-shadow: $shadow-base;
  transition: all 0.3s ease;
  border: 1px solid $border-color;

  &:hover {
    transform: translateY(-2px);
    box-shadow: $shadow-hover;
    border-color: $primary-color;
  }

  &.hot-topic {
    border-left: 3px solid $danger-color;
  }

  &.active-topic {
    border-left: 3px solid $success-color;
  }

  .topic-header {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;

    .topic-icon {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background-color: rgba($primary-color, 0.1);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      color: $primary-color;
      flex-shrink: 0;
      transition: all 0.3s ease;
      border: 1px solid rgba($primary-color, 0.2);

      &.hot {
        background-color: rgba($danger-color, 0.1);
        color: $danger-color;
        border-color: rgba($danger-color, 0.2);
      }

      &.active {
        background-color: rgba($success-color, 0.1);
        color: $success-color;
        border-color: rgba($success-color, 0.2);
      }

      i {
        font-size: 20px;
      }
    }

    .topic-info {
      flex: 1;

      .topic-title-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 6px;
        gap: 8px;
      }

      .topic-title {
        font-size: 16px;
        font-weight: 600;
        color: $text-color;
        margin: 0;
        flex: 1;
        line-height: 1.4;
      }

      .topic-badges {
        display: flex;
        gap: 4px;
        flex-shrink: 0;
      }

      .topic-description {
        font-size: 12px;
        color: $text-color-secondary;
        line-height: 1.5;
        margin: 0 0 12px 0;
      }

      .topic-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 8px;

        .status-tag,
        .heat-tag {
          margin-bottom: 2px;
          font-size: 11px;
        }

        .topic-stats {
          display: flex;
          align-items: center;
          gap: 12px;
          font-size: 11px;
          color: $info-color;

          .stat-item {
            display: flex;
            align-items: center;
            gap: 3px;

            i {
              font-size: 11px;
            }
          }
        }
      }

      .topic-time-info {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 11px;
        color: $info-color;
        margin-top: 6px;
        padding-top: 8px;
        border-top: 1px dashed $border-color;

        .time-item {
          display: flex;
          align-items: center;
          gap: 3px;

          i {
            font-size: 11px;
          }
        }
      }
    }
  }

  .topic-actions {
    display: flex;
    justify-content: flex-end;
    gap: 6px;
    padding-top: 12px;
    border-top: 1px solid $border-color;
    flex-wrap: wrap;

    .action-btn {
      min-width: 50px;
      padding: 4px 8px;
      font-size: 12px;
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-1px);
      }

      i {
        font-size: 12px;
        margin-right: 2px;
      }
    }
  }
}

// 分页
.pagination-container {
  margin-top: 0;
  text-align: right;
  padding: 20px;
  background-color: $card-bg;
  border-top: 1px solid $border-color;

  .pagination {
    display: inline-flex;
    align-items: center;
  }
}

// 对话框
.topic-dialog {
  .el-dialog__header {
    border-bottom: 1px solid $border-color;
    padding: 20px;
  }

  .el-dialog__body {
    padding: 24px;
  }

  .el-dialog__footer {
    border-top: 1px solid $border-color;
    padding: 16px 24px;
  }
}

// 动画
@keyframes spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .topic-management {
    padding: 10px;
  }

  .stats-container {
    .el-col {
      flex: 1;
      min-width: calc(50% - 10px);
    }
  }

  .filter-form {
    flex-direction: column;
    align-items: stretch;
  }

  .topic-grid {
    grid-template-columns: 1fr;
  }

  .topic-card {
    padding: 20px;

    .topic-header {
      gap: 12px;

      .topic-icon {
        width: 48px;
        height: 48px;
        font-size: 24px;
      }
    }
  }
}
</style>