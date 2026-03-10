<template>
  <div class="community-events">

    <!-- 活动统计 -->
    <div class="stats-container">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon">
                <i class="el-icon-calendar"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ statistics.totalEvents || 0 }}</div>
                <div class="stat-label">总活动数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon success">
                <i class="el-icon-video-camera"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number text-success">{{ statistics.activeEvents || 0 }}</div>
                <div class="stat-label">进行中</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon info">
                <i class="el-icon-date"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number text-info">{{ statistics.upcomingEvents || 0 }}</div>
                <div class="stat-label">即将开始</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon warning">
                <i class="el-icon-user"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number text-warning">{{ statistics.totalParticipants || 0 }}</div>
                <div class="stat-label">总参与人数</div>
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

        <!-- 操作按钮 -->
        <el-form-item>
          <div class="action-buttons">
            <el-button type="primary" @click="createEvent">
              <i class="el-icon-plus"></i> 创建活动
            </el-button>
            <el-button @click="refreshData">
              <i class="el-icon-refresh"></i> 刷新
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 活动列表 -->
    <el-card class="list-card">

      <el-table :data="eventList" v-loading="loading" border style="width: 100%" :row-class-name="tableRowClassName"
        :default-expand-all="false">
        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>

        <el-table-column label="活动信息" min-width="300">
          <template slot-scope="scope">
            <div class="event-info">
              <div class="event-title">
                <span class="title-text">{{ truncateText(scope.row.title, 30) }}</span>
                <el-tag v-if="scope.row.is_pinned" type="warning" size="mini" class="pin-tag">置顶</el-tag>
              </div>
              <div class="event-description">{{ truncateText(scope.row.description, 60) }}</div>
              <div class="event-meta">
                <el-tag :type="getStatusType(scope.row.status)" size="mini" class="status-tag">
                  {{ getStatusText(scope.row.status) }}
                </el-tag>
                <span class="event-location" v-if="scope.row.location">
                  <i class="el-icon-location"></i> {{ truncateText(scope.row.location, 20) }}
                </span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="时间" width="180" align="center">
          <template slot-scope="scope">
            <div class="event-time">
              <div v-if="scope.row.start_date" class="time-item">
                <i class="el-icon-time"></i> {{ formatDate(scope.row.start_date) }}
              </div>
              <div v-if="scope.row.end_date" class="time-item">
                <i class="el-icon-finished"></i> {{ formatDate(scope.row.end_date) }}
              </div>
              <div v-if="!scope.row.start_date && !scope.row.end_date" class="time-item">
                <i class="el-icon-information"></i> 无时间限制
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="参与人数" width="100" align="center">
          <template slot-scope="scope">
            <div class="participant-count">
              <div class="count-circle">
                <span class="count">{{ scope.row.participant_count || 0 }}</span>
              </div>
              <span class="unit">人参与</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="奖品信息" width="120" align="center">
          <template slot-scope="scope">
            <div class="prize-info" v-if="scope.row.prize_info">
              <el-tooltip :content="scope.row.prize_info" placement="top">
                <span class="prize-text">{{ truncateText(scope.row.prize_info, 15) }}</span>
              </el-tooltip>
            </div>
            <div v-else class="no-prize">
              <i class="el-icon-gift"></i> 无奖品
            </div>
          </template>
        </el-table-column>

        <el-table-column label="创建时间" width="140" align="center">
          <template slot-scope="scope">
            <div class="create-time">
              <i class="el-icon-clock"></i> {{ formatDate(scope.row.created_at) }}
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="320" align="center" fixed="right">
          <template slot-scope="scope">
            <div class="action-buttons">
              <el-button type="primary" size="mini" plain @click="viewEvent(scope.row)" class="action-btn">
                <i class="el-icon-view"></i> 详情
              </el-button>
              <el-button type="success" size="mini" plain @click="editEvent(scope.row)" class="action-btn">
                <i class="el-icon-edit"></i> 编辑
              </el-button>
              <el-button :type="scope.row.is_pinned ? 'warning' : 'info'" size="mini" plain
                @click="togglePin(scope.row)" class="action-btn">
                <i :class="scope.row.is_pinned ? 'el-icon-top' : 'el-icon-bottom'"></i> {{ scope.row.is_pinned ? '取消置顶'
                  : '置顶' }}
              </el-button>
              <el-button :type="getStatusButtonType(scope.row.status)" size="mini" @click="toggleStatus(scope.row)"
                class="action-btn">
                <i class="el-icon-refresh"></i> {{ getStatusActionText(scope.row.status) }}
              </el-button>
              <el-button type="danger" size="mini" plain @click="deleteEvent(scope.row)" class="action-btn">
                <i class="el-icon-delete"></i> 删除
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

    <!-- 活动详情对话框 -->
    <el-dialog title="活动详情" :visible.sync="detailDialogVisible" width="800px" :modal="false" class="detail-dialog">
      <div v-if="currentEvent" class="event-detail">
        <el-descriptions :column="2" border class="detail-descriptions">
          <el-descriptions-item label="活动ID">{{ currentEvent.id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentEvent.status)" size="small" effect="dark">
              {{ getStatusText(currentEvent.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="置顶">
            <el-tag v-if="currentEvent.is_pinned" type="warning" size="small" effect="dark">置顶</el-tag>
            <span v-else class="text-muted">否</span>
          </el-descriptions-item>
          <el-descriptions-item label="参与人数">{{ currentEvent.participant_count || 0 }} 人</el-descriptions-item>
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
          <h4 class="section-title">活动标题</h4>
          <p class="section-content">{{ currentEvent.title }}</p>
        </div>

        <div class="detail-section">
          <h4 class="section-title">活动描述</h4>
          <p class="section-content">{{ currentEvent.description }}</p>
        </div>

        <div class="detail-section" v-if="currentEvent.prize_info">
          <h4 class="section-title">奖品信息</h4>
          <p class="section-content">{{ currentEvent.prize_info }}</p>
        </div>

        <div class="detail-section" v-if="currentEvent.image">
          <h4 class="section-title">活动图片</h4>
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

    <!-- 创建活动对话框 -->
    <el-dialog title="创建活动" :visible.sync="createDialogVisible" width="700px" :modal="false" class="create-dialog">
      <el-form :model="createForm" label-width="100px" class="create-form">
        <el-form-item label="活动标题" required>
          <el-input v-model="createForm.title" placeholder="请输入活动标题" maxlength="50" show-word-limit></el-input>
        </el-form-item>

        <el-form-item label="活动描述">
          <el-input type="textarea" v-model="createForm.description" placeholder="请输入活动描述" rows="4"></el-input>
        </el-form-item>

        <el-form-item label="活动地点">
          <el-input v-model="createForm.location" placeholder="请输入活动地点" maxlength="100" show-word-limit></el-input>
        </el-form-item>

        <el-form-item label="开始时间">
          <el-date-picker v-model="createForm.start_date" type="datetime" placeholder="选择开始时间"
            style="width: 100%"></el-date-picker>
        </el-form-item>

        <el-form-item label="结束时间">
          <el-date-picker v-model="createForm.end_date" type="datetime" placeholder="选择结束时间"
            style="width: 100%"></el-date-picker>
        </el-form-item>

        <el-form-item label="奖品信息">
          <el-input type="textarea" v-model="createForm.prize_info" placeholder="请输入奖品信息" rows="3"></el-input>
        </el-form-item>

        <el-form-item label="活动状态">
          <el-select v-model="createForm.status" placeholder="选择活动状态" style="width: 100%">
            <el-option label="即将开始" value="upcoming"></el-option>
            <el-option label="进行中" value="active"></el-option>
            <el-option label="已结束" value="ended"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="置顶">
          <el-switch v-model="createForm.is_pinned" active-text="是" inactive-text="否"></el-switch>
        </el-form-item>

        <el-form-item label="活动图片">
          <el-upload class="upload-demo" action="/admin-api/common/upload/image/" :on-success="handleImageUploadSuccess"
            :on-error="handleImageUploadError" :before-upload="beforeImageUpload" :disabled="uploadLoading"
            :headers="getUploadHeaders()">
            <el-button size="small" type="primary">点击上传</el-button>
            <div slot="tip" class="el-upload__tip">只能上传jpg/png文件，且不超过2MB</div>
          </el-upload>
          <div v-if="imageUrl" class="image-preview">
            <img :src="imageUrl" alt="预览" class="preview-image">
            <el-button type="text" size="small" @click="imageUrl = ''">删除</el-button>
          </div>
        </el-form-item>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button @click="createDialogVisible = false; resetCreateForm()">取消</el-button>
        <el-button type="primary" @click="submitCreateForm">创建活动</el-button>
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
      currentEvent: null,
      // 创建活动相关
      createDialogVisible: false,
      createForm: {
        title: '',
        description: '',
        location: '',
        start_date: '',
        end_date: '',
        prize_info: '',
        is_pinned: false,
        status: 'upcoming'
      },
      imageUrl: '',
      uploadLoading: false
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
      const editId = this.$route.query.edit
      if (editId) {
        const event = this.eventList.find(e => e.id === parseInt(editId))
        if (event) {
          this.viewEvent(event)
        } else {
          // 如果事件还没加载，延迟一下再查找
          setTimeout(() => {
            const event = this.eventList.find(e => e.id === parseInt(editId))
            if (event) {
              this.viewEvent(event)
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
        const response = await axios.get('/admin-api/community/events/statistics/')

        if (response.data) {
          // 处理可能的认证错误或数据格式
          if (response.data.code === 200) {
            const data = response.data.data || {}
            this.statistics = {
              totalEvents: data.totalEvents || data.total_events || 0,
              activeEvents: data.activeEvents || data.active_events || 0,
              upcomingEvents: data.upcomingEvents || data.upcoming_events || 0,
              totalParticipants: data.totalParticipants || data.total_participants || 0
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
            const data = response.data
            this.statistics = {
              totalEvents: data.totalEvents || data.total_events || 0,
              activeEvents: data.activeEvents || data.active_events || 0,
              upcomingEvents: data.upcomingEvents || data.upcoming_events || 0,
              totalParticipants: data.totalParticipants || data.total_participants || 0
            }
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
      this.createDialogVisible = true
      this.resetCreateForm()
    },

    resetCreateForm() {
      this.createForm = {
        title: '',
        description: '',
        location: '',
        start_date: '',
        end_date: '',
        prize_info: '',
        is_pinned: false,
        status: 'upcoming'
      }
      this.imageUrl = ''
      this.uploadLoading = false
    },

    handleImageUploadSuccess(response) {
      if (response.data && response.data.url) {
        this.imageUrl = response.data.url
        this.$message.success('图片上传成功')
      } else {
        this.$message.error('图片上传失败')
      }
      this.uploadLoading = false
    },

    handleImageUploadError(error) {
      this.$message.error('图片上传失败')
      this.uploadLoading = false
    },

    beforeImageUpload(file) {
      this.uploadLoading = true
      const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
      const isLt2M = file.size / 1024 / 1024 < 2

      if (!isJPG) {
        this.$message.error('只能上传JPG/PNG图片!')
        this.uploadLoading = false
        return false
      }
      if (!isLt2M) {
        this.$message.error('图片大小不能超过2MB!')
        this.uploadLoading = false
        return false
      }
      return true
    },

    async submitCreateForm() {
      if (!this.createForm.title) {
        this.$message.error('请输入活动标题')
        return
      }

      try {
        const formData = {
          ...this.createForm,
          image: this.imageUrl
        }

        const response = await axios.post('/admin-api/community/events/', formData)
        // 检查响应格式
        if (response.data) {
          // 如果返回的是活动对象（包含id字段），说明创建成功
          if (response.data.id) {
            this.$message.success('活动创建成功')
            this.createDialogVisible = false
            this.loadData()
            this.loadStatistics()
          } else if (response.data.code === 200) {
            // 兼容其他可能的响应格式
            this.$message.success('活动创建成功')
            this.createDialogVisible = false
            this.loadData()
            this.loadStatistics()
          } else {
            this.$message.error('创建失败: ' + (response.data.message || '未知错误'))
          }
        } else {
          this.$message.error('创建失败，请稍后重试')
        }
      } catch (error) {
        console.error('创建活动失败:', error)
        this.$message.error('创建失败，请稍后重试')
      }
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
        if (response.data) {
          // 如果返回的是活动对象（包含id字段），说明操作成功
          if (response.data.id) {
            // 更新本地状态
            event.status = response.data.status
            this.$message.success(`${action}成功`)
            this.loadStatistics()
          } else if (response.data.code === 200) {
            // 兼容其他可能的响应格式
            const statusTransitions = {
              'active': 'ended',
              'upcoming': 'active',
              'ended': 'upcoming'
            }
            event.status = statusTransitions[event.status] || 'upcoming'
            this.$message.success(`${action}成功`)
            this.loadStatistics()
          } else {
            this.$message.error('操作失败: ' + (response.data.message || '未知错误'))
          }
        } else {
          this.$message.error('操作失败，请稍后重试')
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
        // 204 No Content 表示删除成功
        if (response.status === 204) {
          this.$message.success('活动删除成功')
          this.loadData()
          this.loadStatistics()
        } else if (response.data && response.data.code === 200) {
          this.$message.success('活动删除成功')
          this.loadData()
          this.loadStatistics()
        } else {
          this.$message.error('删除失败: ' + (response.data.message || '未知错误'))
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

    exportEvents() {
      this.$confirm('确定要导出活动数据吗？', '导出数据', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }).then(async () => {
        try {
          const response = await axios.get('/admin-api/community/events/export/')
          if (response.data.code === 200) {
            this.$message.success('数据导出成功，请在下载中心查看')
          } else {
            this.$message.error('导出失败: ' + response.data.message)
          }
        } catch (error) {
          console.error('导出数据失败:', error)
          this.$message.error('导出失败，请稍后重试')
        }
      }).catch(() => {
        // 取消导出
      })
    },

    tableRowClassName({ row }) {
      // 根据活动状态设置不同的行样式
      if (row.is_pinned) {
        return 'pinned-row'
      }
      if (row.status === 'active') {
        return 'active-row'
      }
      if (row.status === 'ended') {
        return 'ended-row'
      }
      return ''
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
    },

    getUploadHeaders() {
      return {
        'Authorization': 'Bearer ' + (localStorage.getItem('token') || '')
      }
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

.community-events {
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

      &.info {
        background-color: rgba($info-color, 0.1);
        color: $info-color;
      }

      &.warning {
        background-color: rgba($warning-color, 0.1);
        color: $warning-color;
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

        &.text-info {
          color: $info-color;
        }

        &.text-warning {
          color: $warning-color;
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
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
  justify-content: center;
  padding: 4px 0;

  .el-button {
    transition: all 0.3s ease;
    min-width: 60px;
    padding: 4px 8px;

    &:hover {
      transform: translateY(-1px);
    }
  }

  .action-btn {
    margin-bottom: 4px;
  }

  @media (max-width: 1400px) {
    gap: 6px;

    .el-button {
      min-width: 55px;
      font-size: 12px;

      i {
        font-size: 12px;
      }
    }
  }
}

// 活动列表
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

// 表格样式
.el-table {
  border-radius: 0;

  th {
    background-color: #fafafa;
    font-weight: 600;
  }

  td {
    padding: 16px;
  }
}

// 表格行样式
.pinned-row {
  background-color: rgba($warning-color, 0.05) !important;
}

.active-row {
  background-color: rgba($success-color, 0.05) !important;
}

.ended-row {
  background-color: rgba($info-color, 0.05) !important;
}

// 活动信息
.event-info {
  .event-title {
    font-weight: bold;
    color: $text-color;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 10px;

    .title-text {
      flex: 1;
    }

    .pin-tag {
      margin-left: auto;
    }
  }

  .event-description {
    color: $text-color-secondary;
    margin-bottom: 12px;
    line-height: 1.5;
    font-size: 14px;
  }

  .event-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;

    .event-location {
      color: $info-color;
      font-size: 12px;
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .status-tag {
      margin-right: 8px;
    }
  }
}

// 时间信息
.event-time {
  font-size: 12px;
  color: $text-color-secondary;
  line-height: 1.8;

  .time-item {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 4px;

    &:last-child {
      margin-bottom: 0;
    }
  }
}

// 参与人数
.participant-count {
  text-align: center;

  .count-circle {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background-color: rgba($primary-color, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 8px;

    .count {
      font-size: 16px;
      font-weight: bold;
      color: $primary-color;
    }
  }

  .unit {
    font-size: 12px;
    color: $info-color;
  }
}

// 奖品信息
.prize-info {
  text-align: center;

  .prize-text {
    color: $text-color-secondary;
    font-size: 12px;
  }
}

.no-prize {
  color: $info-color;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

// 分页
.pagination-container {
  margin-top: 20px;
  text-align: right;
  padding: 20px;
  background-color: $card-bg;
  border-top: 1px solid $border-color;

  .pagination {
    display: inline-flex;
    align-items: center;
  }
}

// 详情对话框
.detail-dialog {
  .el-dialog__header {
    border-bottom: 1px solid $border-color;
    padding: 20px;
  }

  .el-dialog__body {
    padding: 24px;
    max-height: 70vh;
    overflow-y: auto;
  }

  .el-dialog__footer {
    border-top: 1px solid $border-color;
    padding: 16px 24px;
  }
}

// 创建活动对话框
.create-dialog {
  .el-dialog__header {
    border-bottom: 1px solid $border-color;
    padding: 20px;
  }

  .el-dialog__body {
    padding: 24px;
    max-height: 70vh;
    overflow-y: auto;
  }

  .el-dialog__footer {
    border-top: 1px solid $border-color;
    padding: 16px 24px;
  }

  .create-form {
    .el-form-item {
      margin-bottom: 20px;
    }
  }

  .image-preview {
    margin-top: 16px;
    display: flex;
    align-items: center;
    gap: 12px;

    .preview-image {
      width: 100px;
      height: 100px;
      object-fit: cover;
      border-radius: $border-radius;
      box-shadow: $shadow-base;
    }
  }
}

.event-detail {
  .detail-descriptions {
    margin-bottom: 24px;

    .el-descriptions__label {
      font-weight: 600;
    }
  }

  .detail-section {
    margin: 24px 0;

    .section-title {
      margin-bottom: 12px;
      color: $text-color;
      font-size: 16px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 8px;

      &::before {
        content: '';
        width: 4px;
        height: 16px;
        background-color: $primary-color;
        border-radius: 2px;
      }
    }

    .section-content {
      color: $text-color-secondary;
      line-height: 1.6;
      margin: 0;
      padding-left: 20px;
    }
  }

  .event-image {
    max-width: 100%;
    max-height: 400px;
    border-radius: $border-radius;
    box-shadow: $shadow-hover;
    margin-top: 12px;
  }
}

// 文本工具类
.text-muted {
  color: $info-color;
}

// 响应式设计
@media (max-width: 1200px) {
  .stats-container {
    .el-col {
      &:nth-child(4n+1) {
        margin-left: 0;
      }

      &:nth-child(4n) {
        margin-right: 0;
      }
    }
  }
}

@media (max-width: 768px) {
  .community-events {
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

  .action-buttons {
    flex-wrap: wrap;
  }

  .el-table {
    font-size: 12px;

    td {
      padding: 12px;
    }
  }
}
</style>