<template>
  <div class="dashboard">
    <!-- 核心数据概览 -->
    <div class="overview-section">
      <el-row :gutter="20">
        <!-- 关键指标卡片 -->
        <el-col :span="6">
          <div class="metric-card primary-card">
            <div class="metric-header">
              <i class="el-icon-user metric-icon"></i>
              <h4>用户统计</h4>
            </div>
            <div class="metric-value">{{ stats.totalUsers || 0 }}</div>
            <div class="metric-footer">
              <span class="metric-label">总用户数</span>
              <el-tag size="mini" type="primary">活跃: {{ stats.activeUsers || 0 }}</el-tag>
            </div>
          </div>
        </el-col>

        <el-col :span="6">
          <div class="metric-card secondary-card">
            <div class="metric-header">
              <i class="el-icon-news metric-icon"></i>
              <h4>动态统计</h4>
            </div>
            <div class="metric-value">{{ stats.totalMoments || 0 }}</div>
            <div class="metric-footer">
              <span class="metric-label">总动态数</span>
              <el-tag size="mini" type="info">今日: {{ stats.todayMoments || 0 }}</el-tag>
            </div>
          </div>
        </el-col>

        <el-col :span="6">
          <div class="metric-card success-card">
            <div class="metric-header">
              <i class="el-icon-document metric-icon"></i>
              <h4>文章统计</h4>
            </div>
            <div class="metric-value">{{ stats.totalArticles || 0 }}</div>
            <div class="metric-footer">
              <span class="metric-label">总文章数</span>
              <el-tag size="mini" type="success">专栏: {{ stats.totalColumns || 0 }}</el-tag>
            </div>
          </div>
        </el-col>

        <el-col :span="6">
          <div class="metric-card warning-card">
            <div class="metric-header">
              <i class="el-icon-alarm-clock metric-icon"></i>
              <h4>活动统计</h4>
            </div>
            <div class="metric-value">{{ stats.activeEvents || 0 }}</div>
            <div class="metric-footer">
              <span class="metric-label">进行中活动</span>
              <el-tag size="mini" type="warning">参与: {{ stats.totalParticipants || 0 }}</el-tag>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 详细数据面板 -->
    <div class="details-section">
      <el-row :gutter="20">
        <!-- 左侧统计卡片 -->
        <el-col :span="12">
          <div class="stats-grid">
            <div class="stat-card couple-card">
              <div class="stat-card-header">
                <i class="el-icon-connection stat-icon"></i>
                <h5>情侣统计</h5>
              </div>
              <div class="stat-card-content">
                <div class="stat-item">
                  <span class="stat-key">情侣数</span>
                  <span class="stat-val">{{ stats.totalCouples || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-key">推荐数</span>
                  <span class="stat-val">{{ stats.totalRecommendations || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-key">测试参与</span>
                  <span class="stat-val">{{ stats.totalTests || 0 }}</span>
                </div>
              </div>
            </div>

            <div class="stat-card mall-card">
              <div class="stat-card-header">
                <i class="el-icon-s-shop stat-icon"></i>
                <h5>商城统计</h5>
              </div>
              <div class="stat-card-content">
                <div class="stat-item">
                  <span class="stat-key">商品数</span>
                  <span class="stat-val">{{ stats.totalProducts || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-key">订单数</span>
                  <span class="stat-val">{{ stats.totalOrders || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-key">今日销售</span>
                  <span class="stat-val">{{ stats.todaySales || 0 }}</span>
                </div>
              </div>
            </div>

            <div class="stat-card system-card">
              <div class="stat-card-header">
                <i class="el-icon-cpu stat-icon"></i>
                <h5>系统状态</h5>
              </div>
              <div class="stat-card-content">
                <div class="stat-item">
                  <span class="stat-key">在线用户</span>
                  <span class="stat-val">{{ stats.onlineUsers || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-key">今日访问</span>
                  <span class="stat-val">{{ stats.todayVisits || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-key">系统版本</span>
                  <span class="stat-val">{{ stats.systemVersion || 'v1.0.0' }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-col>

        <!-- 右侧通知面板 -->
        <el-col :span="12">
          <!-- 待处理举报 -->
          <div class="notification-card urgent-card">
            <div class="notification-header">
              <i class="el-icon-warning notification-icon"></i>
              <h5>待处理举报</h5>
              <el-button type="text" size="mini" @click="$router.push('/community/reports')">查看全部</el-button>
            </div>
            <div class="notification-content">
              <div v-if="pendingReports.length > 0" class="report-list">
                <div v-for="report in pendingReports" :key="report.id" class="report-item">
                  <div class="report-priority" :class="{ 'urgent': report.is_urgent }"></div>
                  <div class="report-body">
                    <h6>{{ report.title }}</h6>
                    <p>{{ report.description }}</p>
                    <div class="report-meta">
                      <el-tag :type="getReportTypeType(report.report_type)" size="mini">
                        {{ getReportTypeText(report.report_type) }}
                      </el-tag>
                      <span class="report-time">{{ formatDate(report.created_at) }}</span>
                    </div>
                  </div>
                  <div class="report-actions">
                    <el-button type="text" size="mini" @click="handleReport(report)">处理</el-button>
                  </div>
                </div>
              </div>
              <div v-else class="empty-state">
                <i class="el-icon-success"></i>
                <p>暂无待处理举报</p>
              </div>
            </div>
          </div>

          <!-- 最近活动 -->
          <div class="notification-card activity-card">
            <div class="notification-header">
              <i class="el-icon-calendar notification-icon"></i>
              <h5>最近活动</h5>
              <el-button type="text" size="mini" @click="$router.push('/community/events')">查看全部</el-button>
            </div>
            <div class="notification-content">
              <div v-if="recentEvents.length > 0" class="event-list">
                <div v-for="event in recentEvents" :key="event.id" class="event-item">
                  <div class="event-status" :class="event.status"></div>
                  <div class="event-body">
                    <h6>{{ event.title }}</h6>
                    <p>{{ event.description }}</p>
                    <div class="event-meta">
                      <el-tag :type="getEventStatusType(event.status)" size="mini">
                        {{ getEventStatusText(event.status) }}
                      </el-tag>
                      <span class="event-time">{{ formatDate(event.created_at) }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="empty-state">
                <i class="el-icon-info"></i>
                <p>暂无最近活动</p>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 数据刷新按钮 -->
    <div class="refresh-section">
      <el-button type="primary" plain @click="refreshData" :loading="refreshing">
        <i class="el-icon-refresh"></i>
        <span>{{ refreshing ? '刷新中...' : '刷新数据' }}</span>
      </el-button>
    </div>
  </div>
</template>

<script>
import { getEventStatistics, getEventList, getReportStatistics, getReportList } from '@/api/community'

export default {
  name: 'Dashboard',
  data() {
    return {
      stats: {
        // 用户统计
        totalUsers: 0,
        activeUsers: 0,
        todayRegister: 0,
        // 动态统计
        totalMoments: 0,
        todayMoments: 0,
        totalLikes: 0,
        // 文章统计
        totalArticles: 0,
        totalColumns: 0,
        totalArticleViews: 0,
        // 活动统计
        activeEvents: 0,
        upcomingEvents: 0,
        totalParticipants: 0,
        // 情侣统计
        totalCouples: 0,
        totalRecommendations: 0,
        totalTests: 0,
        // 商城统计
        totalProducts: 0,
        totalOrders: 0,
        todaySales: 0,
        // 举报统计
        pendingReports: 0,
        todayReports: 0,
        reportResolutionRate: '0%',
        // 系统状态
        onlineUsers: 0,
        todayVisits: 0,
        systemVersion: 'v1.0.0'
      },
      recentEvents: [],
      pendingReports: [],
      refreshing: false
    }
  },
  created() {
    this.loadDashboardData()
  },
  methods: {
    async loadDashboardData() {
      try {
        // 获取用户统计数据
        try {
          const userStatsResponse = await this.$axios.get('/admin-api/user/users/statistics/')
          if (userStatsResponse && userStatsResponse.data) {
            this.stats.totalUsers = userStatsResponse.data.total_users || 0
            this.stats.activeUsers = userStatsResponse.data.active_users || 0
            this.stats.todayRegister = userStatsResponse.data.today_users || 0
          }
        } catch (error) {
          console.error('获取用户统计数据失败:', error)
        }

        // 获取动态统计数据
        try {
          const momentStatsResponse = await this.$axios.get('/admin-api/moment/moments/statistics/')
          if (momentStatsResponse && momentStatsResponse.data) {
            this.stats.totalMoments = momentStatsResponse.data.total_moments || 0
            this.stats.totalLikes = momentStatsResponse.data.total_likes || 0
            this.stats.todayMoments = momentStatsResponse.data.daily_data?.[momentStatsResponse.data.daily_data?.length - 1]?.count || 0
          }
        } catch (error) {
          console.error('获取动态统计数据失败:', error)
        }

        // 获取文章统计数据
        try {
          const articleStatsResponse = await this.$axios.get('/admin-api/articles_manage/statistics/')
          if (articleStatsResponse && articleStatsResponse.data && articleStatsResponse.data.data) {
            this.stats.totalArticles = articleStatsResponse.data.data.total_articles || 0
            this.stats.totalColumns = articleStatsResponse.data.data.total_columns || 0
            this.stats.totalArticleViews = articleStatsResponse.data.data.total_views || 0
          }
        } catch (error) {
          console.error('获取文章统计数据失败:', error)
        }

        // 获取活动统计数据
        const eventStatsResponse = await getEventStatistics()
        if (eventStatsResponse && eventStatsResponse.data) {
          const eventStats = eventStatsResponse.data
          this.stats.activeEvents = eventStats.activeEvents || 0
          this.stats.upcomingEvents = eventStats.upcomingEvents || 0
          this.stats.totalParticipants = eventStats.totalParticipants || 0
        }

        // 获取举报统计数据
        const reportStatsResponse = await getReportStatistics()
        if (reportStatsResponse && reportStatsResponse.data) {
          const reportStats = reportStatsResponse.data
          this.stats.pendingReports = reportStats.pendingReports || 0
          this.stats.todayReports = reportStats.todayReports || 0
          this.stats.reportResolutionRate = reportStats.reportResolutionRate || '0%'
        }

        // 获取情侣统计数据
        try {
          const coupleStatsResponse = await this.$axios.get('/admin-api/couple/recommended-couples/statistics/')
          if (coupleStatsResponse && coupleStatsResponse.data) {
            this.stats.totalCouples = coupleStatsResponse.data.totalCouples || 0
            this.stats.totalRecommendations = coupleStatsResponse.data.totalRecommendations || 0
            this.stats.totalTests = coupleStatsResponse.data.totalTests || 0
          }
        } catch (error) {
          console.error('获取情侣统计数据失败:', error)
        }

        // 获取商城统计数据
        try {
          const mallStatsResponse = await this.$axios.get('/admin-api/mall/products/statistics/')
          if (mallStatsResponse && mallStatsResponse.data) {
            this.stats.totalProducts = mallStatsResponse.data.totalProducts || 0
            this.stats.totalOrders = mallStatsResponse.data.totalOrders || 0
            this.stats.todaySales = mallStatsResponse.data.todaySales || 0
          }
        } catch (error) {
          console.error('获取商城统计数据失败:', error)
        }

        // 获取系统状态数据
        try {
          const systemStatsResponse = await this.$axios.get('/admin-api/user/users/system_status/')
          if (systemStatsResponse && systemStatsResponse.data) {
            this.stats.onlineUsers = systemStatsResponse.data.onlineUsers || 0
            this.stats.todayVisits = systemStatsResponse.data.todayVisits || 0
            this.stats.systemVersion = systemStatsResponse.data.systemVersion || 'v1.0.0'
          }
        } catch (error) {
          console.error('获取系统状态数据失败:', error)
        }

        // 获取最近活动
        const eventsResponse = await getEventList({ page: 1, page_size: 5 })
        if (eventsResponse && eventsResponse.data) {
          this.recentEvents = eventsResponse.data.results || []
        }

        // 获取待处理举报
        const reportsResponse = await getReportList({ page: 1, page_size: 5, status: 'pending' })
        if (reportsResponse && reportsResponse.data) {
          this.pendingReports = reportsResponse.data.results || []
        }
      } catch (error) {
        console.error('加载仪表盘数据失败:', error)
        this.$message.error('加载数据失败，请稍后重试')
      }
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
      // 打开社区活动管理页面并编辑指定活动
      this.$router.push({
        path: '/community/events',
        query: { edit: event.id }
      })
    },

    toggleEventStatus(event) {
      // 这里可以添加切换活动状态的逻辑
      this.$message.success(`已${this.getEventActionText(event.status)}: ${event.title}`)
    },

    handleReport(report) {
      // 打开举报管理页面并查看指定举报
      this.$router.push({
        path: '/community/reports',
        query: { view: report.id }
      })
    },

    previewReport(report) {
      this.$confirm(
        `<div class="report-preview">
          <el-form label-position="top">
            <el-form-item label="举报标题">
              <el-input value="${report.title}" disabled style="width: 100%; margin-bottom: 10px;" />
            </el-form-item>
            <el-form-item label="举报描述">
              <el-input type="textarea" value="${report.description}" disabled rows="4" style="width: 100%; margin-bottom: 10px;" />
            </el-form-item>
            <el-form-item label="举报类型">
              <el-tag type="${this.getReportTypeType(report.report_type)}" style="margin-right: 10px;">
                ${this.getReportTypeText(report.report_type)}
              </el-tag>
            </el-form-item>
            <el-form-item label="紧急程度">
              <el-tag type="${report.is_urgent ? 'danger' : 'info'}" style="margin-right: 10px;">
                ${report.is_urgent ? '紧急' : '普通'}
              </el-tag>
            </el-form-item>
            <el-form-item label="举报时间">
              <el-input value="${this.formatDate(report.created_at)}" disabled style="width: 100%; margin-bottom: 10px;" />
            </el-form-item>
            <el-form-item label="举报人">
              <el-input value="${report.reporter_username}" disabled style="width: 100%; margin-bottom: 10px;" />
            </el-form-item>
            <el-form-item label="被举报人">
              <el-input value="${report.reported_user_username}" disabled style="width: 100%; margin-bottom: 10px;" />
            </el-form-item>
          </el-form>
        </div>`,
        '举报详情',
        {
          confirmButtonText: '处理举报',
          cancelButtonText: '关闭',
          type: 'info',
          dangerouslyUseHTMLString: true,
          center: true,
          width: '600px'
        }
      ).then(() => {
        this.handleReport(report)
      }).catch(() => {
        // 取消操作，不做任何处理
      })
    },

    // 刷新数据方法
    async refreshData() {
      try {
        // 显示刷新中状态
        this.refreshing = true
        // 执行数据加载
        await this.loadDashboardData()
        // 显示成功消息
        this.$message({
          message: '数据刷新成功',
          type: 'success'
        })
      } catch (error) {
        // 显示错误消息
        this.$message({
          message: '刷新数据失败，请稍后重试',
          type: 'error'
        })
      } finally {
        // 恢复按钮状态
        this.refreshing = false
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: calc(100vh - 120px);
}

/* 核心数据概览区域 */
.overview-section {
  margin-bottom: 30px;
}

/* 关键指标卡片 */
.metric-card {
  border-radius: 16px;
  padding: 24px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: 1px solid rgba(255, 107, 139, 0.1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 249, 250, 0.95) 100%);

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    border-radius: 16px 16px 0 0;
  }

  &:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
    border-color: rgba(255, 107, 139, 0.2);
  }

  .metric-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;

    .metric-icon {
      font-size: 24px;
      width: 48px;
      height: 48px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 12px;
      background-color: rgba(255, 107, 139, 0.1);
      color: #FF6B8B;
    }

    h4 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
  }

  .metric-value {
    font-size: 36px;
    font-weight: 700;
    color: #303133;
    margin-bottom: 16px;
    line-height: 1;
  }

  .metric-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .metric-label {
      font-size: 14px;
      color: #606266;
      font-weight: 400;
    }
  }
}

/* 不同类型的指标卡片 */
.primary-card::before {
  background: linear-gradient(90deg, #FF6B8B 0%, #722ED1 100%);
}

.secondary-card::before {
  background: linear-gradient(90deg, #409EFF 0%, #69c0ff 100%);
}

.success-card::before {
  background: linear-gradient(90deg, #67C23A 0%, #85ce61 100%);
}

.warning-card::before {
  background: linear-gradient(90deg, #E6A23C 0%, #ebb563 100%);
}

/* 详细数据区域 */
.details-section {
  margin-bottom: 30px;
}

/* 左侧统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
  height: 100%;
}

/* 详细统计卡片 */
.stat-card {
  border-radius: 16px;
  padding: 20px;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 107, 139, 0.08);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 249, 250, 0.95) 100%);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    border-color: rgba(255, 107, 139, 0.15);
  }

  .stat-card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255, 107, 139, 0.1);

    .stat-icon {
      font-size: 20px;
      color: #FF6B8B;
    }

    h5 {
      margin: 0;
      font-size: 15px;
      font-weight: 600;
      color: #303133;
    }
  }

  .stat-card-content {
    .stat-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 0;
      border-bottom: 1px solid rgba(255, 107, 139, 0.05);

      &:last-child {
        border-bottom: none;
      }

      .stat-key {
        font-size: 13px;
        color: #606266;
        font-weight: 400;
      }

      .stat-val {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }
    }
  }
}

/* 右侧通知卡片 */
.notification-card {
  border-radius: 16px;
  margin-bottom: 20px;
  border: 1px solid rgba(255, 107, 139, 0.08);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 249, 250, 0.95) 100%);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  overflow: hidden;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    border-color: rgba(255, 107, 139, 0.15);
  }

  .notification-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 16px 20px;
    border-bottom: 1px solid rgba(255, 107, 139, 0.1);

    .notification-icon {
      font-size: 18px;
      color: #FF6B8B;
    }

    h5 {
      margin: 0;
      font-size: 15px;
      font-weight: 600;
      color: #303133;
      flex: 1;
    }

    .el-button {
      font-size: 12px;
      padding: 0;
    }
  }

  .notification-content {
    padding: 16px 20px;
  }
}

/* 紧急卡片特殊样式 */
.urgent-card {
  border-left: 4px solid #F56C6C;
}

.activity-card {
  border-left: 4px solid #409EFF;
}

/* 举报列表 */
.report-list {
  .report-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 16px 0;
    border-bottom: 1px solid rgba(255, 107, 139, 0.05);

    &:last-child {
      border-bottom: none;
    }

    .report-priority {
      width: 4px;
      border-radius: 2px;
      background-color: #E6A23C;
      flex-shrink: 0;

      &.urgent {
        background-color: #F56C6C;
      }
    }

    .report-body {
      flex: 1;

      h6 {
        margin: 0 0 8px 0;
        font-size: 14px;
        font-weight: 600;
        color: #303133;
      }

      p {
        margin: 0 0 10px 0;
        font-size: 13px;
        color: #606266;
        line-height: 1.4;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }

      .report-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;

        .report-time {
          font-size: 12px;
          color: #909399;
        }
      }
    }

    .report-actions {
      flex-shrink: 0;
    }
  }
}

/* 活动列表 */
.event-list {
  .event-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 16px 0;
    border-bottom: 1px solid rgba(255, 107, 139, 0.05);

    &:last-child {
      border-bottom: none;
    }

    .event-status {
      width: 4px;
      border-radius: 2px;
      background-color: #909399;
      flex-shrink: 0;

      &.active {
        background-color: #67C23A;
      }

      &.upcoming {
        background-color: #409EFF;
      }

      &.ended {
        background-color: #F56C6C;
      }
    }

    .event-body {
      flex: 1;

      h6 {
        margin: 0 0 8px 0;
        font-size: 14px;
        font-weight: 600;
        color: #303133;
      }

      p {
        margin: 0 0 10px 0;
        font-size: 13px;
        color: #606266;
        line-height: 1.4;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }

      .event-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;

        .event-time {
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #909399;

  i {
    font-size: 48px;
    margin-bottom: 16px;
    display: block;
    color: rgba(255, 107, 139, 0.2);
  }

  p {
    margin: 0;
    font-size: 14px;
    font-weight: 400;
  }
}

/* 刷新按钮区域 */
.refresh-section {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard {
    padding: 10px;
  }

  .metric-card {
    padding: 16px;

    .metric-value {
      font-size: 28px;
    }
  }

  .stat-card,
  .notification-card {
    padding: 12px;
  }
}
</style>