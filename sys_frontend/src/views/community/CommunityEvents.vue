<template>
  <div class="community-events">
    <h1>社区活动管理</h1>
    <p>管理社区活动，包括创建、编辑、状态控制等</p>

    <!-- 活动统计 -->
    <div class="stats-container">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statistics.totalEvents || 0 }}</div>
              <div class="stat-label">总活动数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number text-success">{{ statistics.activeEvents || 0 }}</div>
              <div class="stat-label">进行中</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number text-info">{{ statistics.upcomingEvents || 0 }}</div>
              <div class="stat-label">即将开始</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number text-warning">{{ statistics.totalParticipants || 0 }}</div>
              <div class="stat-label">总参与人数</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" @click="createEvent">
        <i class="el-icon-plus"></i> 创建活动
      </el-button>
      <el-button @click="refreshData">
        <i class="el-icon-refresh"></i> 刷新
      </el-button>
    </div>

    <!-- 筛选和搜索 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="搜索">
          <el-input v-model="filterForm.search" placeholder="搜索活动标题或描述" clearable @clear="handleSearch"
            @keyup.enter="handleSearch" style="width: 250px">
            <el-button slot="append" icon="el-icon-search" @click="handleSearch"></el-button>
          </el-input>
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable @change="handleSearch">
            <el-option label="全部" value=""></el-option>
            <el-option label="进行中" value="active"></el-option>
            <el-option label="即将开始" value="upcoming"></el-option>
            <el-option label="已结束" value="ended"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="置顶">
          <el-select v-model="filterForm.is_pinned" placeholder="全部" clearable @change="handleSearch">
            <el-option label="全部" value=""></el-option>
            <el-option label="置顶" value="true"></el-option>
            <el-option label="未置顶" value="false"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="时间范围">
          <el-select v-model="filterForm.date_range" placeholder="全部时间" clearable @change="handleSearch">
            <el-option label="全部" value=""></el-option>
            <el-option label="今天" value="today"></el-option>
            <el-option label="本周" value="week"></el-option>
            <el-option label="本月" value="month"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 活动列表 -->
    <el-card class="list-card">
      <div slot="header" class="card-header">
        <span>活动列表</span>
      </div>

      <el-table :data="eventList" v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>

        <el-table-column label="活动信息" min-width="300">
          <template slot-scope="scope">
            <div class="event-info">
              <div class="event-title">{{ scope.row.title }}</div>
              <div class="event-description">{{ scope.row.description }}</div>
              <div class="event-meta">
                <el-tag :type="getStatusType(scope.row.status)" size="mini">
                  {{ getStatusText(scope.row.status) }}
                </el-tag>
                <el-tag v-if="scope.row.is_pinned" type="warning" size="mini">置顶</el-tag>
                <span class="event-location" v-if="scope.row.location">
                  <i class="el-icon-location"></i> {{ scope.row.location }}
                </span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="时间" width="200" align="center">
          <template slot-scope="scope">
            <div class="event-time">
              <div v-if="scope.row.start_date">开始: {{ formatDate(scope.row.start_date) }}</div>
              <div v-if="scope.row.end_date">结束: {{ formatDate(scope.row.end_date) }}</div>
              <div v-if="!scope.row.start_date && !scope.row.end_date">无时间限制</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="参与人数" width="100" align="center">
          <template slot-scope="scope">
            <div class="participant-count">
              <span class="count">{{ scope.row.participant_count }}</span>
              <span class="unit">人参与</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="奖品信息" width="150" align="center">
          <template slot-scope="scope">
            <div class="prize-info" v-if="scope.row.prize_info">
              <el-tooltip :content="scope.row.prize_info" placement="top">
                <span class="prize-text">{{ truncateText(scope.row.prize_info, 20) }}</span>
              </el-tooltip>
            </div>
            <div v-else class="no-prize">无奖品</div>
          </template>
        </el-table-column>

        <el-table-column label="创建时间" width="160" align="center">
          <template slot-scope="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template slot-scope="scope">
            <el-button type="text" size="mini" @click="viewEvent(scope.row)">详情</el-button>
            <el-button type="text" size="mini" @click="editEvent(scope.row)">编辑</el-button>
            <el-button type="text" size="mini" @click="togglePin(scope.row)">
              {{ scope.row.is_pinned ? '取消置顶' : '置顶' }}
            </el-button>
            <el-button :type="getStatusButtonType(scope.row.status)" size="mini" @click="toggleStatus(scope.row)">
              {{ getStatusActionText(scope.row.status) }}
            </el-button>
            <el-button type="text" size="mini" @click="deleteEvent(scope.row)">删除</el-button>
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

    <!-- 活动详情对话框 -->
    <el-dialog title="活动详情" :visible.sync="detailDialogVisible" width="800px">
      <div v-if="currentEvent" class="event-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="活动ID">{{ currentEvent.id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentEvent.status)" size="small">
              {{ getStatusText(currentEvent.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="置顶">
            <el-tag v-if="currentEvent.is_pinned" type="warning" size="small">置顶</el-tag>
            <span v-else>否</span>
          </el-descriptions-item>
          <el-descriptions-item label="参与人数">{{ currentEvent.participant_count }} 人</el-descriptions-item>
          <el-descriptions-item label="开始时间" v-if="currentEvent.start_date">
            {{ formatDate(currentEvent.start_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间" v-if="currentEvent.end_date">
            {{ formatDate(currentEvent.end_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="活动地点" v-if="currentEvent.location">
            {{ currentEvent.location }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentEvent.created_at) }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <h4>活动标题</h4>
          <p>{{ currentEvent.title }}</p>
        </div>

        <div class="detail-section">
          <h4>活动描述</h4>
          <p>{{ currentEvent.description }}</p>
        </div>

        <div class="detail-section" v-if="currentEvent.prize_info">
          <h4>奖品信息</h4>
          <p>{{ currentEvent.prize_info }}</p>
        </div>

        <div class="detail-section" v-if="currentEvent.image">
          <h4>活动图片</h4>
          <img :src="currentEvent.image" alt="活动图片" class="event-image">
        </div>
      </div>

      <div slot="footer" class="dialog-footer">
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button v-if="currentEvent" :type="currentEvent.is_pinned ? 'warning' : 'primary'"
          @click="togglePin(currentEvent)">
          {{ currentEvent.is_pinned ? '取消置顶' : '置顶' }}
        </el-button>
        <el-button v-if="currentEvent" :type="getStatusButtonType(currentEvent.status)"
          @click="toggleStatus(currentEvent)">
          {{ getStatusActionText(currentEvent.status) }}
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'CommunityEvents',
  data() {
    return {
      loading: false,
      eventList: [],
      total: 0,
      currentPage: 1,
      pageSize: 10,
      filterForm: {
        search: '',
        status: '',
        is_pinned: '',
        date_range: ''
      },
      statistics: {
        totalEvents: 0,
        activeEvents: 0,
        upcomingEvents: 0,
        totalParticipants: 0
      },
      detailDialogVisible: false,
      currentEvent: null
    }
  },
  created() {
    this.loadData()
    this.loadStatistics()
  },
  methods: {
    async loadData() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize,
          search: this.filterForm.search,
          status: this.filterForm.status,
          is_pinned: this.filterForm.is_pinned
        }

        const response = await axios.get('/admin-api/community/events/', { params })

        if (response.data) {
          // 处理标准 DRF 分页格式
          if (response.data.results !== undefined) {
            this.eventList = response.data.results || []
            this.total = response.data.count || 0
          } else {
            // 处理可能的数组格式
            this.eventList = Array.isArray(response.data) ? response.data : (response.data.data || [])
            this.total = this.eventList.length
          }
        } else {
          this.eventList = []
          this.total = 0
        }
      } catch (error) {
        this.eventList = []
        this.total = 0
        // 只在不是取消操作的情况下显示错误消息
        if (error !== 'cancel') {
          this.$message.error('加载数据失败')
        }
      } finally {
        this.loading = false
      }
    },

    async loadStatistics() {
      try {
        const response = await axios.get('admin-api/community/events/statistics/')

        if (response.data) {
          // 处理可能的认证错误或数据格式
          if (response.data.code === 200) {
            this.statistics = response.data.data || {
              totalEvents: 0,
              activeEvents: 0,
              upcomingEvents: 0,
              totalParticipants: 0
            }
          } else if (response.data.detail) {
            // 认证错误或其他错误
            // 使用默认值
            this.statistics = {
              totalEvents: this.eventList.length,
              activeEvents: this.eventList.filter(e => e.status === 'active').length,
              upcomingEvents: this.eventList.filter(e => e.status === 'upcoming').length,
              totalParticipants: this.eventList.reduce((sum, e) => sum + (e.participant_count || 0), 0)
            }
          } else {
            // 直接数据格式
            this.statistics = response.data
          }
        } else {
          // 使用当前列表数据计算统计
          this.statistics = {
            totalEvents: this.eventList.length,
            activeEvents: this.eventList.filter(e => e.status === 'active').length,
            upcomingEvents: this.eventList.filter(e => e.status === 'upcoming').length,
            totalParticipants: this.eventList.reduce((sum, e) => sum + (e.participant_count || 0), 0)
          }
        }
      } catch (error) {
        // 使用当前列表数据计算统计作为后备
        this.statistics = {
          totalEvents: this.eventList.length,
          activeEvents: this.eventList.filter(e => e.status === 'active').length,
          upcomingEvents: this.eventList.filter(e => e.status === 'upcoming').length,
          totalParticipants: this.eventList.reduce((sum, e) => sum + (e.participant_count || 0), 0)
        }
      }
    },

    handleSearch() {
      this.currentPage = 1
      this.loadData()
    },

    resetFilter() {
      this.filterForm = {
        search: '',
        status: '',
        is_pinned: '',
        date_range: ''
      }
      this.currentPage = 1
      this.loadData()
    },

    handleSizeChange(val) {
      this.pageSize = val
      this.loadData()
    },

    handleCurrentChange(val) {
      this.currentPage = val
      this.loadData()
    },

    createEvent() {
      this.$message.info('创建活动功能开发中...')
    },

    viewEvent(event) {
      this.currentEvent = event
      this.detailDialogVisible = true
    },

    editEvent(event) {
      this.$message.info(`编辑活动: ${event.title}`)
    },

    async togglePin(event) {
      try {
        const action = event.is_pinned ? '取消置顶' : '置顶'
        await this.$confirm(`确定要${action}活动 "${event.title}" 吗？`, '确认', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        const response = await axios.post(`/admin-api/community/events/${event.id}/toggle_pin/`)
        if (response.data.code === 200) {
          event.is_pinned = !event.is_pinned
          this.$message.success(`${action}成功`)
        } else {
          this.$message.error('操作失败: ' + response.data.message)
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('切换置顶状态失败:', error)
          this.$message.error('操作失败')
        }
      }
    },

    async toggleStatus(event) {
      try {
        const action = this.getStatusActionText(event.status)
        await this.$confirm(`确定要${action}活动 "${event.title}" 吗？`, '确认', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        const response = await axios.post(`/admin-api/community/events/${event.id}/toggle_status/`)
        if (response.data.code === 200) {
          // 更新本地状态
          const statusTransitions = {
            'active': 'ended',
            'upcoming': 'active',
            'ended': 'upcoming'
          }
          event.status = statusTransitions[event.status] || 'upcoming'
          this.$message.success(`${action}成功`)
        } else {
          this.$message.error('操作失败: ' + response.data.message)
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('切换活动状态失败:', error)
          this.$message.error('操作失败')
        }
      }
    },

    async deleteEvent(event) {
      try {
        await this.$confirm(`确定要删除活动 "${event.title}" 吗？此操作不可恢复。`, '确认删除', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        const response = await axios.delete(`/admin-api/community/events/${event.id}/`)
        if (response.data.code === 200) {
          this.$message.success('活动删除成功')
          this.loadData()
        } else {
          this.$message.error('删除失败: ' + response.data.message)
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除活动失败:', error)
          this.$message.error('删除失败')
        }
      }
    },

    refreshData() {
      this.loadData()
      this.loadStatistics()
      this.$message.success('数据已刷新')
    },

    // 辅助方法
    getStatusType(status) {
      const types = {
        'active': 'success',
        'upcoming': 'info',
        'ended': 'danger'
      }
      return types[status] || 'info'
    },

    getStatusText(status) {
      const texts = {
        'active': '进行中',
        'upcoming': '即将开始',
        'ended': '已结束'
      }
      return texts[status] || status
    },

    getStatusButtonType(status) {
      const types = {
        'active': 'warning',
        'upcoming': 'success',
        'ended': 'primary'
      }
      return types[status] || 'primary'
    },

    getStatusActionText(status) {
      const actions = {
        'active': '结束活动',
        'upcoming': '开始活动',
        'ended': '重新激活'
      }
      return actions[status] || '操作'
    },

    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    truncateText(text, maxLength) {
      if (!text) return ''
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
    }
  }
}
</script>

<style lang="scss" scoped>
.community-events {
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

      &.text-info {
        color: #409EFF;
      }

      &.text-warning {
        color: #E6A23C;
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

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.event-info {
  .event-title {
    font-weight: bold;
    color: #303133;
    margin-bottom: 5px;
  }

  .event-description {
    color: #606266;
    margin-bottom: 8px;
    line-height: 1.5;
  }

  .event-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;

    .event-location {
      color: #909399;
      font-size: 12px;
    }
  }
}

.event-time {
  font-size: 12px;
  color: #606266;
  line-height: 1.6;
}

.participant-count {
  text-align: center;

  .count {
    font-size: 18px;
    font-weight: bold;
    color: #303133;
  }

  .unit {
    font-size: 12px;
    color: #909399;
  }
}

.prize-info {
  text-align: center;

  .prize-text {
    color: #606266;
    font-size: 12px;
  }
}

.no-prize {
  color: #909399;
  font-size: 12px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.event-detail {
  max-height: 60vh;
  overflow-y: auto;

  .detail-section {
    margin: 20px 0;

    h4 {
      margin-bottom: 10px;
      color: #303133;
      font-size: 16px;
    }

    p {
      color: #606266;
      line-height: 1.6;
      margin: 0;
    }
  }

  .event-image {
    max-width: 100%;
    max-height: 300px;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
}
</style>