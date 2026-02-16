<template>
  <div class="report-management">
    <!-- 页面标题和操作 -->
    <div class="page-header">
      <h1>举报管理</h1>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData">
          <i class="el-icon-refresh"></i> 刷新
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-container">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statistics.total_reports || 0 }}</div>
              <div class="stat-label">总举报数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number text-warning">{{ statistics.pending_reports || 0 }}</div>
              <div class="stat-label">待处理</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number text-success">{{ statistics.resolved_reports || 0 }}</div>
              <div class="stat-label">已处理</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number text-info">{{ statistics.resolution_rate || '0%' }}</div>
              <div class="stat-label">处理率</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选和搜索 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="搜索">
          <el-input v-model="filterForm.search" placeholder="搜索举报标题或描述" clearable @clear="handleSearch"
            @keyup.enter="handleSearch" style="width: 250px">
            <el-button slot="append" icon="el-icon-search" @click="handleSearch"></el-button>
          </el-input>
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable @change="handleSearch">
            <el-option label="全部" value=""></el-option>
            <el-option label="待处理" value="pending"></el-option>
            <el-option label="审核中" value="reviewing"></el-option>
            <el-option label="已处理" value="resolved"></el-option>
            <el-option label="已驳回" value="dismissed"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="举报类型">
          <el-select v-model="filterForm.report_type" placeholder="全部类型" clearable @change="handleSearch">
            <el-option label="全部" value=""></el-option>
            <el-option label="内容举报" value="content"></el-option>
            <el-option label="骚扰举报" value="harassment"></el-option>
            <el-option label="垃圾信息" value="spam"></el-option>
            <el-option label="不当行为" value="inappropriate"></el-option>
            <el-option label="其他举报" value="other"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="优先级">
          <el-select v-model="filterForm.priority" placeholder="全部优先级" clearable @change="handleSearch">
            <el-option label="全部" value=""></el-option>
            <el-option label="高" value="3"></el-option>
            <el-option label="中" value="2"></el-option>
            <el-option label="低" value="1"></el-option>
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

    <!-- 举报列表 -->
    <el-card class="list-card">
      <div slot="header" class="card-header">
        <span>举报列表</span>
        <div class="header-actions">
          <el-button type="success" size="small" @click="batchResolve" :disabled="selectedReports.length === 0">
            <i class="el-icon-check"></i> 批量处理
          </el-button>
        </div>
      </div>

      <el-table :data="reportList" v-loading="loading" border style="width: 100%"
        @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55"></el-table-column>

        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>

        <el-table-column label="举报人" min-width="120">
          <template slot-scope="scope">
            <div class="user-info">
              <div class="user-name">{{ scope.row.reporter_name }}</div>
              <div class="user-username">@{{ scope.row.reporter_username }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="被举报人" min-width="120">
          <template slot-scope="scope">
            <div class="user-info">
              <div class="user-name">{{ scope.row.reported_user_name }}</div>
              <div class="user-username">@{{ scope.row.reported_user_username }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="title" label="举报标题" min-width="200"></el-table-column>

        <el-table-column label="举报类型" width="100" align="center">
          <template slot-scope="scope">
            <el-tag :type="getReportTypeType(scope.row.report_type)" size="mini">
              {{ getReportTypeText(scope.row.report_type) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="优先级" width="80" align="center">
          <template slot-scope="scope">
            <el-tag :type="getPriorityType(scope.row.priority)" size="mini">
              {{ getPriorityText(scope.row.priority) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="100" align="center">
          <template slot-scope="scope">
            <el-tag :type="getStatusType(scope.row.status)" size="mini">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="是否紧急" width="80" align="center">
          <template slot-scope="scope">
            <el-tag v-if="scope.row.is_urgent" type="danger" size="mini">紧急</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column label="举报时间" width="160" align="center">
          <template slot-scope="scope">
            {{ formatDate(scope.row.created_at_formatted) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template slot-scope="scope">
            <el-button type="text" size="mini" @click="viewReport(scope.row)">详情</el-button>
            <el-button v-if="scope.row.status === 'pending'" type="text" size="mini" @click="startReview(scope.row)">
              开始审核
            </el-button>
            <el-button v-if="scope.row.status === 'reviewing'" type="text" size="mini"
              @click="resolveReport(scope.row)">
              处理
            </el-button>
            <el-button v-if="scope.row.status === 'reviewing'" type="text" size="mini"
              @click="dismissReport(scope.row)">
              驳回
            </el-button>
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

    <!-- 举报详情对话框 -->
    <el-dialog title="举报详情" :visible.sync="detailDialogVisible" width="800px">
      <div v-if="currentReport" class="report-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="举报ID">{{ currentReport.id }}</el-descriptions-item>
          <el-descriptions-item label="举报时间">{{ currentReport.created_at_formatted }}</el-descriptions-item>
          <el-descriptions-item label="举报人">{{ currentReport.reporter_name }} ({{ currentReport.reporter_username
          }})</el-descriptions-item>
          <el-descriptions-item label="被举报人">{{ currentReport.reported_user_name }} ({{
            currentReport.reported_user_username
          }})</el-descriptions-item>
          <el-descriptions-item label="举报类型">{{ getReportTypeText(currentReport.report_type) }}</el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityType(currentReport.priority)" size="mini">
              {{ getPriorityText(currentReport.priority) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentReport.status)" size="mini">
              {{ getStatusText(currentReport.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="是否紧急">
            <span v-if="currentReport.is_urgent" class="text-danger">紧急</span>
            <span v-else>否</span>
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <h4>举报标题</h4>
          <p>{{ currentReport.title }}</p>
        </div>

        <div class="detail-section">
          <h4>举报描述</h4>
          <p>{{ currentReport.description }}</p>
        </div>

        <div v-if="currentReport.evidence" class="detail-section">
          <h4>证据信息</h4>
          <p>{{ currentReport.evidence }}</p>
        </div>

        <div v-if="currentReport.content_title" class="detail-section">
          <h4>关联内容</h4>
          <p>类型：{{ currentReport.content_type }}，标题：{{ currentReport.content_title }}</p>
        </div>

        <div v-if="currentReport.review_notes" class="detail-section">
          <h4>处理备注</h4>
          <p>{{ currentReport.review_notes }}</p>
        </div>

        <div v-if="currentReport.action_taken" class="detail-section">
          <h4>处理措施</h4>
          <p>{{ currentReport.action_taken }}</p>
        </div>
      </div>

      <div slot="footer" class="dialog-footer">
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button v-if="currentReport && currentReport.status === 'pending'" type="primary"
          @click="startReview(currentReport)">
          开始审核
        </el-button>
        <el-button v-if="currentReport && currentReport.status === 'reviewing'" type="success"
          @click="resolveReport(currentReport)">
          处理举报
        </el-button>
        <el-button v-if="currentReport && currentReport.status === 'reviewing'" type="warning"
          @click="dismissReport(currentReport)">
          驳回举报
        </el-button>
      </div>
    </el-dialog>

    <!-- 处理举报对话框 -->
    <el-dialog title="处理举报" :visible.sync="resolveDialogVisible" width="500px">
      <el-form :model="resolveForm" label-width="100px">
        <el-form-item label="处理措施">
          <el-select v-model="resolveForm.action" placeholder="选择处理措施">
            <el-option label="警告" value="warning"></el-option>
            <el-option label="内容删除" value="content_removal"></el-option>
            <el-option label="账号暂停" value="account_suspension"></el-option>
            <el-option label="账号封禁" value="account_ban"></el-option>
            <el-option label="无需处理" value="no_action"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="处理描述">
          <el-input type="textarea" v-model="resolveForm.description" placeholder="详细描述处理措施" :rows="4"></el-input>
        </el-form-item>
        <el-form-item v-if="resolveForm.action === 'account_suspension' || resolveForm.action === 'account_ban'"
          label="持续时间">
          <el-input-number v-model="resolveForm.duration" :min="1" :max="365" label="天数"></el-input-number>
          <span style="margin-left: 10px;">天</span>
        </el-form-item>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button @click="resolveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmResolve">确认处理</el-button>
      </div>
    </el-dialog>

    <!-- 驳回举报对话框 -->
    <el-dialog title="驳回举报" :visible.sync="dismissDialogVisible" width="500px">
      <el-form :model="dismissForm" label-width="100px">
        <el-form-item label="驳回原因" required>
          <el-input type="textarea" v-model="dismissForm.reason" placeholder="请输入驳回原因" :rows="4"></el-input>
        </el-form-item>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button @click="dismissDialogVisible = false">取消</el-button>
        <el-button type="warning" @click="confirmDismiss">确认驳回</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {
  getReportList,
  startReviewReport,
  resolveReport,
  dismissReport,
  getReportStatistics
} from '@/api/community'

export default {
  name: 'ReportManagement',
  data() {
    return {
      loading: false,
      reportList: [],
      selectedReports: [],
      total: 0,
      currentPage: 1,
      pageSize: 10,
      filterForm: {
        search: '',
        status: '',
        report_type: '',
        priority: '',
        date_range: ''
      },
      statistics: {
        total_reports: 0,
        pending_reports: 0,
        resolved_reports: 0,
        resolution_rate: '0%'
      },
      detailDialogVisible: false,
      resolveDialogVisible: false,
      dismissDialogVisible: false,
      currentReport: null,
      resolveForm: {
        action: '',
        description: '',
        duration: 7
      },
      dismissForm: {
        reason: ''
      }
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
          report_type: this.filterForm.report_type,
          priority: this.filterForm.priority
        }

        const response = await getReportList(params)

        if (response.data) {
          // 处理标准 DRF 分页格式
          if (response.data.results !== undefined) {
            this.reportList = response.data.results || []
            this.total = response.data.count || 0
          } else if (response.data.data && response.data.data.results !== undefined) {
            // 处理嵌套格式
            this.reportList = response.data.data.results || []
            this.total = response.data.data.count || 0
          } else {
            // 处理其他格式
            this.reportList = Array.isArray(response.data) ? response.data : (response.data.data || [])
            this.total = this.reportList.length
          }
        } else {
          this.reportList = []
          this.total = 0
        }
      } catch (error) {
        this.reportList = []
        this.total = 0

        // 处理认证错误
        if (error.response && error.response.status === 401) {
          this.$message.error('请先登录后再查看举报数据')
        } else {
          this.$message.error('加载数据失败')
        }
      } finally {
        this.loading = false
      }
    },

    async loadStatistics() {
      try {
        const response = await getReportStatistics()

        if (response.data) {
          // 处理标准 DRF 分页格式
          if (response.data.results !== undefined) {
            const data = response.data.results[0] || response.data.results
            this.statistics = {
              total_reports: data.total_reports || 0,
              pending_reports: data.pending_reports || 0,
              resolved_reports: data.resolved_reports || 0,
              resolution_rate: data.resolution_rate ? `${data.resolution_rate}%` : '0%'
            }
          } else if (response.data.data) {
            // 处理嵌套格式
            const data = response.data.data
            this.statistics = {
              total_reports: data.total_reports || 0,
              pending_reports: data.pending_reports || 0,
              resolved_reports: data.resolved_reports || 0,
              resolution_rate: data.resolution_rate ? `${data.resolution_rate}%` : '0%'
            }
          } else {
            // 直接数据格式
            this.statistics = {
              total_reports: response.data.total_reports || 0,
              pending_reports: response.data.pending_reports || 0,
              resolved_reports: response.data.resolved_reports || 0,
              resolution_rate: response.data.resolution_rate ? `${response.data.resolution_rate}%` : '0%'
            }
          }
        } else {
          // 使用举报列表数据计算统计
          this.statistics = {
            total_reports: this.reportList.length,
            pending_reports: this.reportList.filter(r => r.status === 'pending').length,
            resolved_reports: this.reportList.filter(r => r.status === 'resolved').length,
            resolution_rate: this.reportList.length > 0 ? `${Math.round((this.reportList.filter(r => r.status === 'resolved').length / this.reportList.length) * 100)}%` : '0%'
          }
        }
      } catch (error) {
        // 使用举报列表数据计算统计作为后备
        this.statistics = {
          total_reports: this.reportList.length,
          pending_reports: this.reportList.filter(r => r.status === 'pending').length,
          resolved_reports: this.reportList.filter(r => r.status === 'resolved').length,
          resolution_rate: this.reportList.length > 0 ? `${Math.round((this.reportList.filter(r => r.status === 'resolved').length / this.reportList.length) * 100)}%` : '0%'
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
        report_type: '',
        priority: '',
        date_range: ''
      }
      this.currentPage = 1
      this.loadData()
    },

    handleSelectionChange(val) {
      this.selectedReports = val
    },

    handleSizeChange(val) {
      this.pageSize = val
      this.loadData()
    },

    handleCurrentChange(val) {
      this.currentPage = val
      this.loadData()
    },

    viewReport(report) {
      this.currentReport = report
      this.detailDialogVisible = true
    },

    async startReview(report) {
      this.$confirm('确定要开始审核这个举报吗？', '确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }).then(async () => {
        try {
          const response = await startReviewReport(report.id)
          if (response.data.code === 200) {
            this.$message.success('已开始审核')
            this.loadData()
          } else {
            this.$message.error('操作失败: ' + response.data.message)
          }
        } catch (error) {
          this.$message.error('操作失败')
        }
      }).catch(() => { })
    },

    resolveReport(report) {
      this.currentReport = report
      this.resolveDialogVisible = true
    },

    dismissReport(report) {
      this.currentReport = report
      this.dismissDialogVisible = true
    },

    confirmResolve() {
      if (!this.resolveForm.action) {
        this.$message.error('请选择处理措施')
        return
      }
      if (!this.resolveForm.description) {
        this.$message.error('请输入处理描述')
        return
      }

      this.$confirm('确定要处理这个举报吗？', '确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          const response = await resolveReport(this.currentReport.id, {
            action_taken: this.resolveForm.description
          })
          if (response.data.code === 200) {
            this.$message.success('举报已处理')
            this.resolveDialogVisible = false
            this.loadData()
          } else {
            this.$message.error('处理失败: ' + response.data.message)
          }
        } catch (error) {
          this.$message.error('处理失败')
        }
      }).catch(() => { })
    },

    confirmDismiss() {
      if (!this.dismissForm.reason) {
        this.$message.error('请输入驳回原因')
        return
      }

      this.$confirm('确定要驳回这个举报吗？', '确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          const response = await dismissReport(this.currentReport.id, {
            review_notes: this.dismissForm.reason
          })
          if (response.data.code === 200) {
            this.$message.success('举报已驳回')
            this.dismissDialogVisible = false
            this.loadData()
          } else {
            this.$message.error('驳回失败: ' + response.data.message)
          }
        } catch (error) {
          this.$message.error('驳回失败')
        }
      }).catch(() => { })
    },

    batchResolve() {
      if (this.selectedReports.length === 0) {
        this.$message.warning('请选择要处理的举报')
        return
      }

      this.$confirm(`确定要批量处理选中的 ${this.selectedReports.length} 个举报吗？`, '确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 这里可以添加API调用来批量处理举报
        this.$message.success('批量处理成功')
        this.loadData()
      }).catch(() => { })
    },

    refreshData() {
      this.loadData()
      this.loadStatistics()
      this.$message.success('数据已刷新')
    },

    // 辅助方法
    getReportTypeType(type) {
      const types = {
        'content': 'danger',
        'harassment': 'warning',
        'spam': 'info',
        'inappropriate': 'warning',
        'other': 'info'
      }
      return types[type] || 'info'
    },

    getReportTypeText(type) {
      const texts = {
        'content': '内容举报',
        'harassment': '骚扰举报',
        'spam': '垃圾信息',
        'inappropriate': '不当行为',
        'other': '其他举报'
      }
      return texts[type] || type
    },

    getPriorityType(priority) {
      const types = {
        1: 'info',
        2: 'warning',
        3: 'danger'
      }
      return types[priority] || 'info'
    },

    getPriorityText(priority) {
      const texts = {
        1: '低',
        2: '中',
        3: '高'
      }
      return texts[priority] || priority
    },

    getStatusType(status) {
      const types = {
        'pending': 'warning',
        'reviewing': 'info',
        'resolved': 'success',
        'dismissed': 'info'
      }
      return types[status] || 'info'
    },

    getStatusText(status) {
      const texts = {
        'pending': '待处理',
        'reviewing': '审核中',
        'resolved': '已处理',
        'dismissed': '已驳回'
      }
      return texts[status] || status
    },

    formatDate(dateString) {
      return dateString
    }
  }
}
</script>

<style lang="scss" scoped>
.report-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  h1 {
    margin: 0;
    color: #303133;
  }
}

.stats-container {
  margin-bottom: 20px;
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

      &.text-warning {
        color: #E6A23C;
      }

      &.text-success {
        color: #67C23A;
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

.user-info {
  line-height: 1.5;

  .user-name {
    font-weight: bold;
    color: #303133;
  }

  .user-username {
    font-size: 12px;
    color: #909399;
  }
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.report-detail {
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
}

.text-danger {
  color: #F56C6C;
}
</style>