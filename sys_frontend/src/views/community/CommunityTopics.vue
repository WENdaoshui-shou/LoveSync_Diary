<template>
  <div class="topic-management">
    <h1>热门话题管理</h1>
    <p>管理社区热门话题和讨论</p>

    <!-- 话题统计 -->
    <div class="stats-container">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statistics.total_topics || 0 }}</div>
              <div class="stat-label">总话题数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number text-success">{{ statistics.active_topics || 0 }}</div>
              <div class="stat-label">活跃话题</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number text-warning">{{ statistics.hot_topics || 0 }}</div>
              <div class="stat-label">热门话题</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number text-info">{{ statistics.total_discussions || 0 }}</div>
              <div class="stat-label">总讨论数</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" @click="createTopic">
        <i class="el-icon-plus"></i> 创建话题
      </el-button>
      <el-button @click="refreshData">
        <i class="el-icon-refresh"></i> 刷新
      </el-button>
    </div>

    <!-- 话题列表 -->
    <el-card>
      <div slot="header" class="card-header">
        <span>话题列表</span>
        <div class="header-actions">
          <el-input v-model="searchKeyword" placeholder="搜索话题" prefix-icon="el-icon-search"
            style="width: 200px; margin-right: 10px" @keyup.enter="searchTopics"></el-input>
          <el-select v-model="filterStatus" placeholder="状态筛选" style="width: 120px; margin-right: 10px">
            <el-option label="全部" value=""></el-option>
            <el-option label="活跃" value="active"></el-option>
            <el-option label="热门" value="hot"></el-option>
            <el-option label="普通" value="normal"></el-option>
          </el-select>
          <el-select v-model="filterHeatLevel" placeholder="热度筛选" style="width: 120px; margin-right: 10px">
            <el-option label="全部热度" value=""></el-option>
            <el-option label="火爆" value="3"></el-option>
            <el-option label="热门" value="2"></el-option>
            <el-option label="普通" value="1"></el-option>
          </el-select>
          <el-button type="primary" size="small" @click="searchTopics">搜索</el-button>
        </div>
      </div>

      <div class="topic-list">
        <div v-if="loading" class="loading-state">
          <i class="el-icon-loading"></i>
          <p>正在加载话题数据...</p>
        </div>

        <div v-else-if="topics.length === 0" class="empty-state">
          <i class="el-icon-chat-dot-round"></i>
          <p>暂无话题数据</p>
        </div>

        <div v-else class="topic-grid">
          <div v-for="topic in topics" :key="topic.id" class="topic-card">
            <div class="topic-header">
              <div class="topic-icon">
                <i :class="topic.icon || 'el-icon-chat-dot-round'"></i>
              </div>
              <div class="topic-info">
                <h4>{{ topic.title }}</h4>
                <p>{{ topic.description }}</p>
                <div class="topic-meta">
                  <el-tag :type="getStatusType(topic.status)" size="mini">
                    {{ getStatusText(topic.status) }}
                  </el-tag>
                  <el-tag :type="getHeatType(topic.heat_level)" size="mini">
                    {{ getHeatText(topic.heat_level) }}
                  </el-tag>
                  <span class="topic-stats">
                    <i class="el-icon-view"></i> {{ topic.view_count || 0 }}
                    <i class="el-icon-chat-dot-round"></i> {{ topic.discussion_count || 0 }}
                    <i class="el-icon-thumb"></i> {{ topic.like_count || 0 }}
                  </span>
                </div>
              </div>
            </div>

            <div class="topic-actions">
              <el-button type="text" size="mini" @click="viewTopic(topic)">查看</el-button>
              <el-button type="text" size="mini" @click="editTopic(topic)">编辑</el-button>
              <el-button type="text" size="mini" @click="deleteTopic(topic)">删除</el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination 
          @size-change="handleSizeChange" 
          @current-change="handleCurrentChange" 
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]" 
          :page-size="pageSize" 
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"></el-pagination>
      </div>
    </el-card>

    <!-- 创建/编辑话题对话框 -->
    <el-dialog
      title="创建话题"
      :visible.sync="dialogVisible"
      width="500px"
    >
      <el-form ref="topicForm" :model="topicForm" :rules="topicRules" label-width="80px">
        <el-form-item label="话题名称" prop="title">
          <el-input v-model="topicForm.title" placeholder="请输入话题名称"></el-input>
        </el-form-item>
        <el-form-item label="话题描述">
          <el-input v-model="topicForm.description" type="textarea" rows="3" placeholder="请输入话题描述"></el-input>
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
    }
  }
}
</script>

<style lang="scss" scoped>
.topic-management {
  padding: 20px;

  h1 {
    color: #303133;
    margin-bottom: 10px;
  }

  p {
    color: #909399;
    margin-bottom: 30px;
  }
}

.stats-container {
  margin-bottom: 30px;
}

.stat-card {
  text-align: center;

  .stat-content {
    padding: 20px 0;

    .stat-number {
      font-size: 32px;
      font-weight: bold;
      color: #303133;
      margin-bottom: 10px;

      &.text-success {
        color: #67C23A;
      }

      &.text-warning {
        color: #E6A23C;
      }

      &.text-info {
        color: #409EFF;
      }
    }

    .stat-label {
      font-size: 14px;
      color: #909399;
    }
  }
}

.action-bar {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;

  i {
    font-size: 48px;
    margin-bottom: 20px;
    display: block;
  }

  p {
    margin: 0;
    font-size: 16px;
  }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;

  i {
    font-size: 64px;
    margin-bottom: 20px;
    display: block;
  }

  p {
    margin: 0;
    font-size: 16px;
  }
}

.topic-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.topic-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  }

  .topic-header {
    display: flex;
    align-items: flex-start;
    gap: 15px;
    margin-bottom: 15px;

    .topic-icon {
      font-size: 32px;
      color: #409EFF;
      width: 40px;
      text-align: center;
    }

    .topic-info {
      flex: 1;

      h4 {
        margin: 0 0 8px 0;
        color: #303133;
        font-size: 16px;
      }

      p {
        margin: 0 0 10px 0;
        color: #606266;
        font-size: 14px;
        line-height: 1.5;
      }

      .topic-meta {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;

        .topic-stats {
          font-size: 12px;
          color: #909399;
          display: flex;
          align-items: center;
          gap: 15px;

          i {
            margin-right: 3px;
          }
        }
      }
    }
  }

  .topic-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.dialog-footer {
  text-align: right;
}
</style>