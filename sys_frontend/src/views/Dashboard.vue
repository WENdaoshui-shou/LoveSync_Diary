<template>
  <div class="community-dashboard">
    <h1>LoveSync 社区管理中心</h1>
    <p>管理社区活动、成就系统、热门话题和用户举报</p>

    <!-- 社区统计概览 -->
    <div class="stats-container">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card" @click.native="$router.push('/community/events')">
            <div class="stat-icon">
              <i class="el-icon-calendar"></i>
            </div>
            <div class="stat-content">
              <h3>社区活动</h3>
              <p>管理社区活动</p>
              <el-button type="primary">进入管理</el-button>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card" @click.native="$router.push('/community/achievements')">
            <div class="stat-icon">
              <i class="el-icon-trophy"></i>
            </div>
            <div class="stat-content">
              <h3>成就系统</h3>
              <p>管理用户成就</p>
              <el-button type="primary">进入管理</el-button>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card" @click.native="$router.push('/community/topics')">
            <div class="stat-icon">
              <i class="el-icon-chat-dot-round"></i>
            </div>
            <div class="stat-content">
              <h3>热门话题</h3>
              <p>管理热门话题</p>
              <el-button type="primary">进入管理</el-button>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card" @click.native="$router.push('/community/reports')">
            <div class="stat-icon">
              <i class="el-icon-warning"></i>
            </div>
            <div class="stat-content">
              <h3>举报管理</h3>
              <p>处理用户举报</p>
              <el-button type="primary">进入管理</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 快速统计面板 -->
    <div class="quick-stats">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="quick-stat-card">
            <div class="quick-stat-header">
              <h4>活动统计</h4>
              <el-tag type="success">实时</el-tag>
            </div>
            <div class="quick-stat-content">
              <div class="stat-item">
                <span class="stat-label">进行中活动:</span>
                <span class="stat-value">{{ stats.activeEvents || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">即将开始:</span>
                <span class="stat-value">{{ stats.upcomingEvents || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">总参与人数:</span>
                <span class="stat-value">{{ stats.totalParticipants || 0 }}</span>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="quick-stat-card">
            <div class="quick-stat-header">
              <h4>举报统计</h4>
              <el-tag type="warning">待处理</el-tag>
            </div>
            <div class="quick-stat-content">
              <div class="stat-item">
                <span class="stat-label">待处理举报:</span>
                <span class="stat-value text-warning">{{ stats.pendingReports || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">今日新增:</span>
                <span class="stat-value">{{ stats.todayReports || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">处理率:</span>
                <span class="stat-value">{{ stats.reportResolutionRate || '0%' }}</span>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="quick-stat-card">
            <div class="quick-stat-header">
              <h4>成就统计</h4>
              <el-tag type="info">系统</el-tag>
            </div>
            <div class="quick-stat-content">
              <div class="stat-item">
                <span class="stat-label">总成就数:</span>
                <span class="stat-value">{{ stats.totalAchievements || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">用户获得:</span>
                <span class="stat-value">{{ stats.userAchievements || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">完成率:</span>
                <span class="stat-value">{{ stats.achievementCompletionRate || '0%' }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 最近活动列表 -->
    <div class="recent-activities">
      <el-card>
        <div slot="header" class="card-header">
          <span>最近活动</span>
          <el-button type="text" @click="$router.push('/community/events')">查看全部</el-button>
        </div>
        <div v-if="recentEvents.length > 0" class="activity-list">
          <div v-for="event in recentEvents" :key="event.id" class="activity-item">
            <div class="activity-info">
              <h5>{{ event.title }}</h5>
              <p>{{ event.description }}</p>
              <div class="activity-meta">
                <el-tag :type="getEventStatusType(event.status)" size="mini">
                  {{ getEventStatusText(event.status) }}
                </el-tag>
                <span class="activity-date">{{ formatDate(event.created_at) }}</span>
              </div>
            </div>
            <div class="activity-actions">
              <el-button type="text" size="mini" @click="editEvent(event)">编辑</el-button>
              <el-button type="text" size="mini" @click="toggleEventStatus(event)">
                {{ getEventActionText(event.status) }}
              </el-button>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <i class="el-icon-calendar"></i>
          <p>暂无最近活动</p>
        </div>
      </el-card>
    </div>

    <!-- 待处理举报 -->
    <div class="pending-reports">
      <el-card>
        <div slot="header" class="card-header">
          <span>待处理举报</span>
          <el-button type="text" @click="$router.push('/community/reports')">查看全部</el-button>
        </div>
        <div v-if="pendingReports.length > 0" class="report-list">
          <div v-for="report in pendingReports" :key="report.id" class="report-item">
            <div class="report-info">
              <h5>{{ report.title }}</h5>
              <p>{{ report.description }}</p>
              <div class="report-meta">
                <el-tag :type="getReportTypeType(report.type)" size="mini">
                  {{ getReportTypeText(report.type) }}
                </el-tag>
                <span class="report-date">{{ formatDate(report.created_at) }}</span>
              </div>
            </div>
            <div class="report-actions">
              <el-button type="text" size="mini" @click="handleReport(report)">处理</el-button>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <i class="el-icon-warning"></i>
          <p>暂无待处理举报</p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CommunityDashboard',
  data() {
    return {
      stats: {
        activeEvents: 0,
        upcomingEvents: 0,
        totalParticipants: 0,
        pendingReports: 0,
        todayReports: 0,
        reportResolutionRate: '0%',
        totalAchievements: 0,
        userAchievements: 0,
        achievementCompletionRate: '0%'
      },
      recentEvents: [],
      pendingReports: []
    }
  },
  created() {
    this.loadDashboardData()
  },
  methods: {
    async loadDashboardData() {
    },

    getEventStatusType(status) {
      const types = {
        'active': 'success',
        'upcoming': 'info',
        'ended': 'danger'
      }
      return types[status] || 'info'
    },

    getEventStatusText(status) {
      const texts = {
        'active': '进行中',
        'upcoming': '即将开始',
        'ended': '已结束'
      }
      return texts[status] || status
    },

    getEventActionText(status) {
      const actions = {
        'active': '结束活动',
        'upcoming': '开始活动',
        'ended': '重新激活'
      }
      return actions[status] || '操作'
    },

    getReportTypeType(type) {
      const types = {
        'content': 'danger',
        'harassment': 'warning',
        'spam': 'info',
        'other': 'info'
      }
      return types[type] || 'info'
    },

    getReportTypeText(type) {
      const texts = {
        'content': '内容举报',
        'harassment': '骚扰举报',
        'spam': '垃圾信息',
        'other': '其他举报'
      }
      return texts[type] || type
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

    editEvent(event) {
      this.$router.push(`/community/events/${event.id}/edit`)
    },

    toggleEventStatus(event) {
      // 这里可以添加切换活动状态的逻辑
      this.$message.success(`已${this.getEventActionText(event.status)}: ${event.title}`)
    },

    handleReport(report) {
      this.$router.push(`/community/reports/${report.id}`)
    }
  }
}
</script>

<style lang="scss" scoped>
.community-dashboard {
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
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .stat-icon {
    font-size: 48px;
    color: #409EFF;
    margin-bottom: 15px;
  }

  .stat-content {
    h3 {
      margin: 0 0 10px 0;
      color: #303133;
      font-size: 18px;
    }

    p {
      color: #909399;
      margin-bottom: 15px;
      font-size: 14px;
    }
  }
}

.quick-stats {
  margin-bottom: 30px;
}

.quick-stat-card {
  .quick-stat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;

    h4 {
      margin: 0;
      color: #303133;
      font-size: 16px;
    }
  }

  .quick-stat-content {
    .stat-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
      padding: 8px 0;
      border-bottom: 1px solid #f0f0f0;

      &:last-child {
        border-bottom: none;
        margin-bottom: 0;
      }

      .stat-label {
        color: #606266;
        font-size: 14px;
      }

      .stat-value {
        color: #303133;
        font-weight: bold;
        font-size: 16px;

        &.text-warning {
          color: #E6A23C;
        }
      }
    }
  }
}

.recent-activities,
.pending-reports {
  margin-bottom: 30px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .activity-list,
  .report-list {

    .activity-item,
    .report-item {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      padding: 15px 0;
      border-bottom: 1px solid #f0f0f0;

      &:last-child {
        border-bottom: none;
      }

      .activity-info,
      .report-info {
        flex: 1;
        margin-right: 20px;

        h5 {
          margin: 0 0 8px 0;
          color: #303133;
          font-size: 15px;
        }

        p {
          margin: 0 0 10px 0;
          color: #606266;
          font-size: 13px;
          line-height: 1.5;
        }

        .activity-meta,
        .report-meta {
          display: flex;
          align-items: center;
          gap: 10px;

          .activity-date,
          .report-date {
            color: #909399;
            font-size: 12px;
          }
        }
      }

      .activity-actions,
      .report-actions {
        display: flex;
        flex-direction: column;
        gap: 5px;
      }
    }
  }

  .empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #909399;

    i {
      font-size: 48px;
      margin-bottom: 15px;
      display: block;
    }

    p {
      margin: 0;
      font-size: 14px;
    }
  }
}
</style>