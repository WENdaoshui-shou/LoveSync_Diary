<template>
  <div class="flash-sale-management">

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="活动名称">
          <el-input v-model="searchForm.name" placeholder="请输入活动名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchFlashSales">
            <i class="el-icon-search"></i> 搜索
          </el-button>
          <el-button @click="resetForm">
            <i class="el-icon-refresh"></i> 重置
          </el-button>
          <el-button type="primary" @click="handleAdd">
            <i class="el-icon-plus"></i> 添加闪购活动
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 闪购活动列表 -->
    <el-card class="list-card">
      <el-table v-loading="loading" :data="flashSales" style="width: 100%">
        <el-table-column prop="id" label="活动ID" width="80" />
        <el-table-column prop="name" label="活动名称" />
        <el-table-column label="活动时间" width="300">
          <template slot-scope="scope">
            <div class="activity-time">
              <div class="time-item">{{ scope.row.start_time }}</div>
              <div class="time-separator">→</div>
              <div class="time-item">{{ scope.row.end_time }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'">
              {{ scope.row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="活动描述" min-width="200">
          <template slot-scope="scope">
            <div class="activity-description" :title="scope.row.description">
              {{ scope.row.description || '无' }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="倒计时" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.need_countdown === 1 ? 'success' : 'info'">
              {{ scope.row.need_countdown === 1 ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="会员专享" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.is_vip_only === 1 ? 'success' : 'info'">
              {{ scope.row.is_vip_only === 1 ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template slot-scope="scope">
            <div class="operation-buttons">
              <el-button type="primary" size="small" @click="handleEdit(scope.row)">
                <i class="el-icon-edit"></i> 编辑
              </el-button>
              <el-button type="danger" size="small" @click="handleDelete(scope.row.id)">
                <i class="el-icon-delete"></i> 删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination :current-page="pagination.current" :page-size="pagination.size" :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper" :total="pagination.total" @size-change="handleSizeChange"
          @current-change="handleCurrentChange" />
      </div>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="600px" :modal="false">
      <el-form :model="form" label-width="100px">
        <el-form-item label="活动名称" required>
          <el-input v-model="form.name" placeholder="请输入活动名称" />
        </el-form-item>
        <el-form-item label="开始时间" required>
          <el-date-picker v-model="form.start_time" type="datetime" placeholder="选择开始时间" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束时间" required>
          <el-date-picker v-model="form.end_time" type="datetime" placeholder="选择结束时间" style="width: 100%" />
        </el-form-item>
        <el-form-item label="活动描述">
          <el-input v-model="form.description" type="textarea" placeholder="请输入活动描述" rows="3" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.status" active-value="1" inactive-value="0" />
        </el-form-item>
        <el-form-item label="需要倒计时">
          <el-switch v-model="form.need_countdown" active-value="1" inactive-value="0" />
        </el-form-item>
        <el-form-item label="会员专享">
          <el-switch v-model="form.is_vip_only" active-value="1" inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { getFlashSales, createFlashSale, updateFlashSale, deleteFlashSale } from '@/api/mall'

export default {
  name: 'FlashSaleList',
  data() {
    return {
      loading: false,
      flashSales: [],
      searchForm: {
        name: ''
      },
      pagination: {
        current: 1,
        size: 10,
        total: 0
      },
      dialogVisible: false,
      dialogTitle: '',
      form: {
        id: '',
        name: '',
        start_time: '',
        end_time: '',
        status: 1,
        description: '',
        need_countdown: 0,
        is_vip_only: 0
      }
    }
  },
  mounted() {
    this.fetchFlashSales()
  },
  methods: {
    fetchFlashSales() {
      this.loading = true
      const params = {
        page: this.pagination.current,
        page_size: this.pagination.size,
        search: this.searchForm.name
      }
      getFlashSales(params)
        .then(response => {
          // 检查后端返回格式
          if (response.data.results && response.data.count) {
            // 后端返回 { results: [...], count: number } 格式
            this.flashSales = response.data.results
            this.pagination.total = response.data.count
          } else {
            // 后端直接返回数组格式
            this.flashSales = response.data
            this.pagination.total = response.data.length
          }
        })
        .catch(error => {
          this.$message.error('获取闪购活动列表失败: ' + error.message)
        })
        .finally(() => {
          this.loading = false
        })
    },
    handleAdd() {
      this.dialogTitle = '添加闪购活动'
      this.form = {
        id: '',
        name: '',
        start_time: '',
        end_time: '',
        status: 1,
        description: '',
        need_countdown: 0,
        is_vip_only: 0
      }
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.dialogTitle = '编辑闪购活动'
      // 确保状态字段被正确转换为字符串类型，以匹配开关组件的 active-value 和 inactive-value
      this.form = {
        ...row,
        status: row.status.toString(),
        need_countdown: row.need_countdown.toString(),
        is_vip_only: row.is_vip_only.toString()
      }
      this.dialogVisible = true
    },
    handleSubmit() {
      if (!this.form.name) {
        this.$message.error('请输入活动名称')
        return
      }
      if (!this.form.start_time || !this.form.end_time) {
        this.$message.error('请选择活动时间')
        return
      }
      if (new Date(this.form.start_time) >= new Date(this.form.end_time)) {
        this.$message.error('开始时间必须早于结束时间')
        return
      }

      const request = this.form.id ? updateFlashSale(this.form.id, this.form) : createFlashSale(this.form)
      request
        .then(() => {
          this.$message.success(this.form.id ? '更新闪购活动成功' : '添加闪购活动成功')
          this.dialogVisible = false
          this.fetchFlashSales()
        })
        .catch(error => {
          this.$message.error((this.form.id ? '更新闪购活动' : '添加闪购活动') + '失败: ' + error.message)
        })
    },
    handleDelete(id) {
      this.$confirm('确定要删除这个闪购活动吗？', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          deleteFlashSale(id)
            .then(() => {
              this.$message.success('删除闪购活动成功')
              this.fetchFlashSales()
            })
            .catch(error => {
              this.$message.error('删除闪购活动失败: ' + error.message)
            })
        })
        .catch(() => { })
    },
    resetForm() {
      this.searchForm = {
        name: ''
      }
      this.fetchFlashSales()
    },
    handleSizeChange(size) {
      this.pagination.size = size
      this.fetchFlashSales()
    },
    handleCurrentChange(current) {
      this.pagination.current = current
      this.fetchFlashSales()
    }
  }
}
</script>

<style scoped>
.flash-sale-management {
  padding: 20px;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.filter-card {
  margin-bottom: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  overflow: hidden;
}

.filter-card:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.15);
}

.search-form {
  width: 100%;
  padding: 20px;
}

.list-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  overflow: hidden;
}

.list-card:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.15);
}

/* 表格样式 */
.el-table {
  border-radius: 8px 8px 0 0;
  overflow: hidden;
  border: 1px solid #dcdfe6;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.el-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #303133;
  padding: 14px 0;
  border-bottom: 2px solid #409EFF;
  border-right: 1px solid #e4e7ed;
  font-size: 14px;
}

.el-table th:last-child {
  border-right: none;
}

.el-table tr {
  border-bottom: 1px solid #dcdfe6;
  transition: all 0.2s ease;
}

.el-table tr:hover {
  background-color: #ecf5ff;
}

.el-table__row {
  height: 65px;
}

.el-table__cell {
  vertical-align: middle !important;
  border-right: 1px solid #dcdfe6;
  padding: 12px 0;
  font-size: 14px;
  color: #606266;
}

.el-table__cell:last-child {
  border-right: none;
}

.el-table::before {
  height: 0;
}

/* 操作按钮容器 */
.operation-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
}

/* 按钮样式优化 */
.el-button {
  border-radius: 4px;
  transition: all 0.3s ease;
}

.el-button--small {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 4px;
}

.el-button--primary {
  background-color: #409EFF;
  border-color: #409EFF;
}

.el-button--primary:hover {
  background-color: #66b1ff;
  border-color: #66b1ff;
}

.el-button--danger {
  background-color: #F56C6C;
  border-color: #F56C6C;
}

.el-button--danger:hover {
  background-color: #f78989;
  border-color: #f78989;
}

/* 标签样式 */
.el-tag {
  border-radius: 4px;
  padding: 0 10px;
  height: 24px;
  line-height: 22px;
  font-size: 12px;
}

/* 活动时间样式 */
.activity-time {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.time-item {
  font-size: 12px;
  color: #606266;
  white-space: nowrap;
}

.time-separator {
  color: #909399;
  font-size: 12px;
  font-weight: 500;
}

/* 活动描述样式 */
.activity-description {
  font-size: 12px;
  color: #606266;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  cursor: help;
  transition: all 0.3s ease;
}

.activity-description:hover {
  color: #409EFF;
}

/* 分页样式 */
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  padding: 20px;
  background-color: #ffffff;
  border-top: 1px solid #e4e7ed;
}

/* 对话框样式 */
.el-dialog {
  border-radius: 8px;
  overflow: hidden;
}

.el-dialog__header {
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  padding: 20px;
}

.el-dialog__title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.el-dialog__body {
  padding: 24px;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  padding: 16px 24px;
  border-top: 1px solid #e4e7ed;
  background-color: #fafafa;
}

/* 输入框样式 */
.el-input__inner {
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  transition: all 0.3s ease;
}

.el-input__inner:focus {
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

/* 日期选择器样式 */
.el-date-editor {
  width: 100%;
}

/* 加载动画 */
.el-loading {
  background-color: rgba(255, 255, 255, 0.8);
}

.el-loading-spinner .path {
  stroke: #409EFF;
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
  .flash-sale-management {
    padding: 10px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .search-form {
    padding: 15px;
  }

  .el-table {
    font-size: 12px;
  }

  .el-table-column {
    width: auto !important;
    min-width: 80px;
  }
}
</style>