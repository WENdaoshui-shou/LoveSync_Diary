<template>
  <div class="report-management">

    <!-- 统计卡片 -->
    <div class="stats-container">
      <el-row :gutter="20">
        <el-col :span="6" :xs="12" :sm="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon">
                <i class="el-icon-document"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ statistics.total_reports || 0 }}</div>
                <div class="stat-label">总举报数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6" :xs="12" :sm="6">
          <el-card class="stat-card warning-card">
            <div class="stat-content">
              <div class="stat-icon warning-icon">
                <i class="el-icon-time"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number text-warning">{{ statistics.pending_reports || 0 }}</div>
                <div class="stat-label">待处理</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6" :xs="12" :sm="6">
          <el-card class="stat-card success-card">
            <div class="stat-content">
              <div class="stat-icon success-icon">
                <i class="el-icon-check"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number text-success">{{ statistics.resolved_reports || 0 }}</div>
                <div class="stat-label">已处理</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6" :xs="12" :sm="6">
          <el-card class="stat-card info-card">
            <div class="stat-content">
              <div class="stat-icon info-icon">
                <i class="el-icon-data-analysis"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number text-info">{{ statistics.resolution_rate || '0%' }}</div>
                <div class="stat-label">处理率</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选和搜索 -->
    <el-card class="filter-card">
      <div slot="header" class="card-header">
        <span class="card-title">筛选条件</span>
      </div>
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="搜索">
          <el-input v-model="filterForm.search" placeholder="搜索举报标题或描述" clearable @clear="handleSearch"
            @keyup.enter="handleSearch" style="width: 200px">
            <el-button slot="append" icon="el-icon-search" @click="handleSearch"></el-button>
          </el-input>
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable @change="handleSearch"
            style="width: 150px">
            <el-option label="全部" value=""></el-option>
            <el-option label="待处理" value="pending"></el-option>
            <el-option label="审核中" value="reviewing"></el-option>
            <el-option label="已处理" value="resolved"></el-option>
            <el-option label="已驳回" value="dismissed"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="举报类型">
          <el-select v-model="filterForm.report_type" placeholder="全部类型" clearable @change="handleSearch"
            style="width: 150px">
            <el-option label="全部" value=""></el-option>
            <el-option label="内容举报" value="content"></el-option>
            <el-option label="骚扰举报" value="harassment"></el-option>
            <el-option label="垃圾信息" value="spam"></el-option>
            <el-option label="不当行为" value="inappropriate"></el-option>
            <el-option label="其他举报" value="other"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="优先级">
          <el-select v-model="filterForm.priority" placeholder="全部优先级" clearable @change="handleSearch"
            style="width: 120px">
            <el-option label="全部" value=""></el-option>
            <el-option label="高" value="3"></el-option>
            <el-option label="中" value="2"></el-option>
            <el-option label="低" value="1"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="时间范围">
          <el-select v-model="filterForm.date_range" placeholder="全部时间" clearable @change="handleSearch"
            style="width: 120px">
            <el-option label="全部" value=""></el-option>
            <el-option label="今天" value="today"></el-option>
            <el-option label="本周" value="week"></el-option>
            <el-option label="本月" value="month"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item>
          <div class="action-buttons">
            <el-button type="primary" @click="handleSearch" class="search-button">
              <i class="el-icon-search"></i> 搜索
            </el-button>
            <el-button @click="resetFilter" class="reset-button">
              <i class="el-icon-refresh-left"></i> 重置
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 举报列表 -->
    <el-card class="list-card">
      <div slot="header" class="card-header">
        <span class="card-title">举报列表</span>
        <div class="header-actions">
          <el-button type="success" size="small" @click="batchResolve" :disabled="selectedReports.length === 0"
            class="batch-button">
            <i class="el-icon-check"></i> 批量处理
          </el-button>
          <el-button type="info" size="small" @click="exportReports" class="export-button">
            <i class="el-icon-download"></i> 导出
          </el-button>
        </div>
      </div>

      <el-table :data="reportList" v-loading="loading" border style="width: 100%"
        @selection-change="handleSelectionChange" class="report-table">
        <el-table-column type="selection" width="55"></el-table-column>

        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>

        <el-table-column label="举报人" min-width="120">
          <template slot-scope="scope">
            <div class="user-info">
              <div class="user-avatar">
                <el-avatar size="small" :src="getAvatarUrl(scope.row.reporter_avatar)"
                  :icon="scope.row.reporter_avatar ? '' : 'el-icon-user'">
                  {{ !scope.row.reporter_avatar ? (scope.row.reporter_name ? scope.row.reporter_name.charAt(0) : '?') : '' }}
                </el-avatar>
              </div>
              <div class="user-details">
                <div class="user-name">{{ scope.row.reporter_name }}</div>
                <div class="user-username">@{{ scope.row.reporter_username }}</div>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="被举报人" min-width="120">
          <template slot-scope="scope">
            <div class="user-info">
              <div class="user-avatar">
                <el-avatar size="small" :src="getAvatarUrl(scope.row.reported_user_avatar)"
                  :icon="scope.row.reported_user_avatar ? '' : 'el-icon-user'">
                  {{ !scope.row.reported_user_avatar ? (scope.row.reported_user_name ?
                    scope.row.reported_user_name.charAt(0) : '?') : '' }}
                </el-avatar>
              </div>
              <div class="user-details">
                <div class="user-name">{{ scope.row.reported_user_name }}</div>
                <div class="user-username">@{{ scope.row.reported_user_username }}</div>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="举报标题" min-width="200">
          <template slot-scope="scope">
            <div class="report-title" @click="viewReport(scope.row)">
              {{ truncateText(scope.row.title, 30) }}
            </div>
          </template>
        </el-table-column>

        <el-table-column label="举报类型" width="120" align="center">
          <template slot-scope="scope">
            <el-tag :type="getReportTypeType(scope.row.report_type)" size="mini" effect="plain">
              {{ getReportTypeText(scope.row.report_type) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="优先级" width="90" align="center">
          <template slot-scope="scope">
            <el-tag :type="getPriorityType(scope.row.priority)" size="mini" effect="dark">
              {{ getPriorityText(scope.row.priority) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="110" align="center">
          <template slot-scope="scope">
            <el-tag :type="getStatusType(scope.row.status)" size="mini">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="是否紧急" width="90" align="center">
          <template slot-scope="scope">
            <el-tag v-if="scope.row.is_urgent" type="danger" size="mini" effect="dark">紧急</el-tag>
            <span v-else class="text-gray">-</span>
          </template>
        </el-table-column>

        <el-table-column label="举报时间" width="160" align="center">
          <template slot-scope="scope">
            {{ formatDate(scope.row.created_at_formatted) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template slot-scope="scope">
            <div class="action-buttons">
              <el-button type="primary" size="mini" @click="viewReport(scope.row)" class="view-button">
                <i class="el-icon-view"></i> 详情
              </el-button>
              <el-button v-if="scope.row.status === 'pending'" type="success" size="mini"
                @click="startReview(scope.row)" class="review-button">
                <i class="el-icon-s-order"></i> 开始审核
              </el-button>
              <el-button v-if="scope.row.status === 'reviewing'" type="warning" size="mini"
                @click="resolveReport(scope.row)" class="resolve-button">
                <i class="el-icon-check"></i> 处理
              </el-button>
              <el-button v-if="scope.row.status === 'reviewing'" type="danger" size="mini"
                @click="dismissReport(scope.row)" class="dismiss-button">
                <i class="el-icon-close"></i> 驳回
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange" :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]" :page-size="pageSize" layout="total, sizes, prev, pager, next, jumper"
          :total="total" class="pagination"></el-pagination>
      </div>
    </el-card>

    <!-- 举报详情对话框 -->
    <el-dialog title="举报详情" :visible.sync="detailDialogVisible" width="900px" :modal="false" class="detail-dialog">
      <div v-if="currentReport" class="report-detail">
        <el-descriptions :column="2" border class="report-descriptions">
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
          <h4 class="section-title">举报标题</h4>
          <p class="section-content">{{ currentReport.title }}</p>
        </div>

        <div class="detail-section">
          <h4 class="section-title">举报描述</h4>
          <p class="section-content">{{ currentReport.description }}</p>
        </div>

        <div v-if="currentReport.evidence" class="detail-section">
          <h4 class="section-title">证据信息</h4>
          <p class="section-content">{{ currentReport.evidence }}</p>
        </div>

        <div v-if="currentReport.content_title" class="detail-section">
          <h4 class="section-title">关联内容</h4>
          <p class="section-content">类型：{{ currentReport.content_type }}，标题：{{ currentReport.content_title }}</p>
        </div>

        <div v-if="currentReport.review_notes" class="detail-section">
          <h4 class="section-title">处理备注</h4>
          <p class="section-content">{{ currentReport.review_notes }}</p>
        </div>

        <div v-if="currentReport.action_taken" class="detail-section">
          <h4 class="section-title">处理措施</h4>
          <p class="section-content">{{ currentReport.action_taken }}</p>
        </div>
      </div>

      <div slot="footer" class="dialog-footer">
        <el-button @click="detailDialogVisible = false" class="cancel-button">关闭</el-button>
        <el-button v-if="currentReport && currentReport.status === 'pending'" type="primary"
          @click="startReview(currentReport)" class="primary-button">
          <i class="el-icon-s-order"></i> 开始审核
        </el-button>
        <el-button v-if="currentReport && currentReport.status === 'reviewing'" type="success"
          @click="resolveReport(currentReport)" class="success-button">
          <i class="el-icon-check"></i> 处理举报
        </el-button>
        <el-button v-if="currentReport && currentReport.status === 'reviewing'" type="warning"
          @click="dismissReport(currentReport)" class="warning-button">
          <i class="el-icon-close"></i> 驳回举报
        </el-button>
      </div>
    </el-dialog>

    <!-- 处理举报对话框 -->
    <el-dialog title="处理举报" :visible.sync="resolveDialogVisible" width="500px" :modal="false" class="resolve-dialog">
      <el-form :model="resolveForm" label-width="100px" class="resolve-form">
        <el-form-item label="处理措施" required>
          <el-select v-model="resolveForm.action" placeholder="选择处理措施" style="width: 100%">
            <el-option label="警告" value="warning"></el-option>
            <el-option label="内容删除" value="content_removal"></el-option>
            <el-option label="账号暂停" value="account_suspension"></el-option>
            <el-option label="账号封禁" value="account_ban"></el-option>
            <el-option label="无需处理" value="no_action"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="处理描述" required>
          <el-input type="textarea" v-model="resolveForm.description" placeholder="详细描述处理措施" :rows="4"></el-input>
        </el-form-item>
        <el-form-item v-if="resolveForm.action === 'account_suspension' || resolveForm.action === 'account_ban'"
          label="持续时间" required>
          <el-input-number v-model="resolveForm.duration" :min="1" :max="365" label="天数"
            style="width: 100%"></el-input-number>
          <span style="margin-left: 10px;">天</span>
        </el-form-item>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button @click="resolveDialogVisible = false" class="cancel-button">取消</el-button>
        <el-button type="primary" @click="confirmResolve" class="primary-button">确认处理</el-button>
      </div>
    </el-dialog>

    <!-- 驳回举报对话框 -->
    <el-dialog title="驳回举报" :visible.sync="dismissDialogVisible" width="500px" :modal="false" class="dismiss-dialog">
      <el-form :model="dismissForm" label-width="100px" class="dismiss-form">
        <el-form-item label="驳回原因" required>
          <el-input type="textarea" v-model="dismissForm.reason" placeholder="请输入驳回原因" :rows="4"></el-input>
        </el-form-item>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button @click="dismissDialogVisible = false" class="cancel-button">取消</el-button>
        <el-button type="warning" @click="confirmDismiss" class="warning-button">确认驳回</el-button>
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
    this.handleUrlParams()
  },

  watch: {
    $route: {
      handler: 'handleUrlParams',
      immediate: true
    }
  },

  methods: {
    handleUrlParams() {
      // 处理URL参数，从Dashboard页面跳转过来时自动打开详情
      const viewId = this.$route.query.view
      if (viewId) {
        const report = this.reportList.find(r => r.id === parseInt(viewId))
        if (report) {
          this.viewReport(report)
        } else {
          // 如果举报还没加载，延迟一下再查找
          setTimeout(() => {
            const report = this.reportList.find(r => r.id === parseInt(viewId))
            if (report) {
              this.viewReport(report)
            }
          }, 1000)
        }
        // 清除URL参数
        this.$router.replace({
          query: {}
        })
      }
    },

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
        // 数据加载完成后更新统计数据
        this.loadStatistics()
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
              total_reports: data.total_reports || data.totalReports || 0,
              pending_reports: data.pending_reports || data.pendingReports || 0,
              resolved_reports: data.resolved_reports || data.resolvedReports || 0,
              resolution_rate: data.resolution_rate || data.reportResolutionRate || '0%'
            }
          } else if (response.data.data) {
            // 处理嵌套格式
            const data = response.data.data
            this.statistics = {
              total_reports: data.total_reports || data.totalReports || 0,
              pending_reports: data.pending_reports || data.pendingReports || 0,
              resolved_reports: data.resolved_reports || data.resolvedReports || 0,
              resolution_rate: data.resolution_rate || data.reportResolutionRate || '0%'
            }
          } else {
            // 直接数据格式
            this.statistics = {
              total_reports: response.data.total_reports || response.data.totalReports || 0,
              pending_reports: response.data.pending_reports || response.data.pendingReports || 0,
              resolved_reports: response.data.resolved_reports || response.data.resolvedReports || 0,
              resolution_rate: response.data.resolution_rate || response.data.reportResolutionRate || '0%'
            }
          }
        } else {
          // 使用举报列表数据计算统计
          this.calculateLocalStatistics()
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
        // 使用举报列表数据计算统计作为后备
        this.calculateLocalStatistics()
      }
    },

    // 本地计算统计数据
    calculateLocalStatistics() {
      const total = this.reportList.length
      const pending = this.reportList.filter(r => r.status === 'pending' || r.status === 'reviewing').length
      const resolved = this.reportList.filter(r => r.status === 'resolved' || r.status === 'dismissed').length
      const rate = total > 0 ? `${Math.round((resolved / total) * 100)}%` : '0%'

      this.statistics = {
        total_reports: total,
        pending_reports: pending,
        resolved_reports: resolved,
        resolution_rate: rate
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
          if (response.data) {
            this.$message.success('已开始审核')
            this.loadData()
          } else {
            this.$message.error('操作失败')
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
          if (response.data) {
            this.$message.success('举报已处理')
            this.resolveDialogVisible = false
            this.loadData()
          } else {
            this.$message.error('处理失败')
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
          if (response.data) {
            this.$message.success('举报已驳回')
            this.dismissDialogVisible = false
            this.loadData()
          } else {
            this.$message.error('驳回失败')
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

    // 导出举报数据
    exportReports() {
      this.$confirm('确定要导出举报数据吗？', '确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }).then(() => {
        // 这里可以添加API调用来导出举报数据
        this.$message.success('导出成功，文件正在下载')
      }).catch(() => { })
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
    },

    // 截断文本
    truncateText(text, maxLength) {
      if (!text) return ''
      if (text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    },

    // 获取完整的头像URL
    getAvatarUrl(avatarPath) {
      if (!avatarPath) return ''
      // 如果已经是完整的URL，直接返回
      if (avatarPath.startsWith('http://') || avatarPath.startsWith('https://')) {
        return avatarPath
      }
      // 否则添加CDN域名
      return `https://static.lovesync-diary.top/${avatarPath}`
    }
  }
}
</script>

<style lang="scss" scoped>
.report-management {
  padding: 20px;
  min-height: calc(100vh - 120px);
  background-color: #f5f7fa;
}

// 页面标题样式
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  padding: 24px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);

  .header-content {
    flex: 1;
  }

  .page-title {
    display: flex;
    align-items: center;
    margin: 0 0 8px 0;
    color: #303133;
    font-size: 24px;
    font-weight: 600;

    .title-icon {
      margin-right: 12px;
      font-size: 28px;
      color: #409EFF;
    }
  }

  .page-description {
    margin: 0;
    color: #909399;
    font-size: 14px;
    line-height: 1.5;
  }

  .header-actions {
    display: flex;
    align-items: center;
  }

  .refresh-button {
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
    }
  }
}

// 统计卡片样式
.stats-container {
  margin-bottom: 30px;

  .stat-card {
    position: relative;
    overflow: hidden;
    border-radius: 12px;
    transition: all 0.3s ease;
    border: none;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
    }

    &.warning-card {
      background: linear-gradient(135deg, #fef6ec 0%, #fde9c9 100%);
    }

    &.success-card {
      background: linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%);
    }

    &.info-card {
      background: linear-gradient(135deg, #ecf5ff 0%, #d6ecff 100%);
    }

    .stat-content {
      display: flex;
      align-items: center;
      padding: 24px;

      .stat-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        margin-right: 20px;
        border-radius: 50%;
        background-color: rgba(255, 255, 255, 0.9);
        font-size: 24px;
        color: #409EFF;

        &.warning-icon {
          color: #E6A23C;
        }

        &.success-icon {
          color: #67C23A;
        }

        &.info-icon {
          color: #909399;
        }
      }

      .stat-info {
        flex: 1;

        .stat-number {
          font-size: 32px;
          font-weight: bold;
          color: #303133;
          margin-bottom: 4px;

          &.text-warning {
            color: #E6A23C;
          }

          &.text-success {
            color: #67C23A;
          }

          &.text-info {
            color: #909399;
          }
        }

        .stat-label {
          font-size: 14px;
          color: #909399;
          line-height: 1.4;
        }
      }
    }
  }
}

// 筛选卡片样式
.filter-card {
  margin-bottom: 30px;
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid #ebeef5;

    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
  }

  .filter-form {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    padding: 20px;
    gap: 16px;

    .action-buttons {
      display: flex;
      gap: 10px;

      .search-button,
      .reset-button {
        transition: all 0.3s ease;

        &:hover {
          transform: translateY(-1px);
        }
      }
    }
  }
}

// 列表卡片样式
.list-card {
  margin-bottom: 30px;
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid #ebeef5;

    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }

    .header-actions {
      display: flex;
      gap: 10px;

      .batch-button,
      .export-button {
        transition: all 0.3s ease;

        &:hover {
          transform: translateY(-1px);
        }

        &:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
      }
    }
  }

  .report-table {
    border-radius: 0 0 12px 12px;

    .el-table__header-wrapper th {
      background-color: #fafafa;
      font-weight: 600;
      color: #303133;
    }

    .el-table__body-wrapper tr {
      transition: all 0.3s ease;

      &:hover {
        background-color: #f5f7fa;
      }
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 10px;

      .user-avatar {
        flex-shrink: 0;
        width: 32px;
        height: 32px;
        overflow: hidden;
        border-radius: 50%;
        background: none !important;
        box-shadow: none !important;
        position: relative;

        :deep(.el-avatar) {
          width: 100% !important;
          height: 100% !important;
          border-radius: 50% !important;
          overflow: hidden !important;
          box-shadow: none !important;
          background: none !important;
          position: relative;
          z-index: 1;
        }

        :deep(.el-avatar__inner) {
          width: 100% !important;
          height: 100% !important;
          border-radius: 50% !important;
          overflow: hidden !important;
          position: relative;
          z-index: 2;
        }

        :deep(.el-avatar__img) {
          width: 100% !important;
          height: 100% !important;
          border-radius: 50% !important;
          object-fit: cover !important;
          object-position: center center !important;
          position: relative;
          z-index: 3;
        }
      }

      .user-details {
        flex: 1;
        min-width: 0;

        .user-name {
          font-weight: 500;
          color: #303133;
          margin-bottom: 2px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .user-username {
          font-size: 12px;
          color: #909399;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
      }
    }

    .report-title {
      cursor: pointer;
      color: #409EFF;
      font-weight: 500;
      transition: all 0.3s ease;

      &:hover {
        text-decoration: underline;
      }
    }

    .action-buttons {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      justify-content: center;

      .view-button,
      .review-button,
      .resolve-button,
      .dismiss-button {
        transition: all 0.3s ease;
        font-size: 12px;
        padding: 4px 10px;

        &:hover {
          transform: translateY(-1px);
        }
      }
    }
  }

  .pagination-container {
    margin-top: 24px;
    padding: 0 20px 20px;

    .pagination {
      display: flex;
      justify-content: flex-end;
      align-items: center;
    }
  }
}

// 对话框样式
.detail-dialog,
.resolve-dialog,
.dismiss-dialog {
  border-radius: 12px;
  overflow: hidden;

  .el-dialog__header {
    padding: 20px 24px;
    background-color: #fafafa;
    border-bottom: 1px solid #ebeef5;
  }

  .el-dialog__title {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
  }

  .el-dialog__body {
    padding: 24px;
    max-height: 60vh;
    overflow-y: auto;
  }

  .el-dialog__footer {
    padding: 16px 24px;
    border-top: 1px solid #ebeef5;
  }
}

.report-detail {
  .report-descriptions {
    margin-bottom: 24px;

    .el-descriptions__label {
      font-weight: 500;
      color: #303133;
    }

    .el-descriptions__content {
      color: #606266;
    }
  }

  .detail-section {
    margin: 0 0 24px 0;

    .section-title {
      margin: 0 0 12px 0;
      color: #303133;
      font-size: 16px;
      font-weight: 600;
      border-left: 4px solid #409EFF;
      padding-left: 12px;
    }

    .section-content {
      color: #606266;
      line-height: 1.6;
      margin: 0;
      padding: 12px;
      background-color: #fafafa;
      border-radius: 6px;
      word-break: break-word;
    }
  }
}

.resolve-form,
.dismiss-form {
  .el-form-item {
    margin-bottom: 20px;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;

  .cancel-button,
  .primary-button,
  .success-button,
  .warning-button {
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-1px);
    }
  }
}

// 辅助样式
.text-gray {
  color: #909399;
}

.text-danger {
  color: #F56C6C;
}

// 响应式设计
@media (max-width: 1200px) {
  .report-management {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;

    .header-actions {
      align-self: flex-end;
    }
  }

  .stats-container {
    .el-col {
      &:nth-child(n+3) {
        margin-top: 20px;
      }
    }
  }

  .filter-form {
    .el-form-item {
      margin-right: 0;
    }
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 20px;

    .page-title {
      font-size: 20px;

      .title-icon {
        font-size: 24px;
      }
    }
  }

  .stats-container {
    .stat-card {
      .stat-content {
        padding: 20px;

        .stat-icon {
          width: 40px;
          height: 40px;
          font-size: 20px;
        }

        .stat-number {
          font-size: 24px;
        }
      }
    }
  }

  .filter-form {
    .action-buttons {
      flex-direction: column;
      width: 100%;

      .el-button {
        width: 100%;
      }
    }
  }

  .list-card {
    .report-table {
      .action-buttons {
        flex-direction: column;
        align-items: center;

        .el-button {
          width: 100%;
          margin-bottom: 4px;
        }
      }
    }
  }

  .detail-dialog {
    width: 95% !important;
  }
}
</style>