<template>
  <div class="category-management">

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="分类名称">
          <el-input v-model="searchForm.name" placeholder="请输入分类名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchCategories">
            <i class="el-icon-search"></i> 搜索
          </el-button>
          <el-button @click="resetForm">
            <i class="el-icon-refresh"></i> 重置
          </el-button>
          <el-button type="primary" @click="handleAdd">
            <i class="el-icon-plus"></i> 添加分类
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 分类列表 -->
    <el-card class="list-card">
      <!-- 分类表格 -->
      <el-table v-loading="loading" :data="categories" style="width: 100%" border>
        <!-- 分类ID -->
        <el-table-column prop="id" label="分类ID" width="80" />

        <!-- 分类名称 -->
        <el-table-column prop="name" label="分类名称" />

        <!-- 父分类ID -->
        <el-table-column prop="parent_id" label="父分类ID" width="100" />

        <!-- 排序 -->
        <el-table-column prop="sort" label="排序" width="80" />

        <!-- 状态 -->
        <el-table-column label="状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'info'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- 创建时间（修复标签拼写错误） -->
        <el-table-column prop="created_at" label="创建时间" width="180" />

        <!-- 操作列（修复格式、标签闭合） -->
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

      <!-- 分页组件（优化格式） -->
      <div class="pagination-container">
        <el-pagination :current-page="pagination.current" :page-size="pagination.size" :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper" :total="pagination.total" @size-change="handleSizeChange"
          @current-change="handleCurrentChange" />
      </div>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="600px" :modal="false">
      <el-form :model="form" label-width="100px">
        <el-form-item label="分类名称" required>
          <el-input v-model="form.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="父分类ID">
          <el-input v-model="form.parent_id" placeholder="请输入父分类ID，顶级分类留空" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" :max="999" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" active-value="1" inactive-value="0" />
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
import { getCategories, createCategory, updateCategory, deleteCategory } from '@/api/mall'

export default {
  name: 'CategoryList',
  data() {
    return {
      loading: false,
      categories: [],
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
        parent_id: null,
        sort: 0,
        is_active: 1
      }
    }
  },
  mounted() {
    this.fetchCategories()
  },
  methods: {
    fetchCategories() {
      this.loading = true
      const params = {
        page: this.pagination.current,
        page_size: this.pagination.size,
        search: this.searchForm.name
      }
      getCategories(params)
        .then(response => {
          // 后端直接返回数组格式，不是 { results: [...], count: number } 格式
          this.categories = response.data
          this.pagination.total = response.data.length
        })
        .catch(error => {
          this.$message.error('获取分类列表失败: ' + error.message)
        })
        .finally(() => {
          this.loading = false
        })
    },
    handleAdd() {
      this.dialogTitle = '添加分类'
      // 获取当前最大排序值，新分类的排序值为最大排序值+1
      let maxSort = 0
      if (this.categories.length > 0) {
        maxSort = Math.max(...this.categories.map(cat => cat.sort || 0))
      }
      this.form = {
        id: '',
        name: '',
        parent_id: null,
        sort: maxSort + 1,
        is_active: 1
      }
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.dialogTitle = '编辑分类'
      // 确保is_active字段被正确转换为字符串类型，以匹配开关组件的active-value和inactive-value
      this.form = {
        ...row,
        is_active: row.is_active ? '1' : '0'
      }
      this.dialogVisible = true
    },
    handleSubmit() {
      if (!this.form.name) {
        this.$message.error('请输入分类名称')
        return
      }

      const request = this.form.id ? updateCategory(this.form.id, this.form) : createCategory(this.form)
      request
        .then(response => {
          console.log('分类操作成功:', response.data)
          this.$message.success(this.form.id ? '更新分类成功' : '添加分类成功')
          this.dialogVisible = false
          this.fetchCategories()
        })
        .catch(error => {
          this.$message.error((this.form.id ? '更新分类' : '添加分类') + '失败: ' + error.message)
        })
    },
    handleDelete(id) {
      this.$confirm('确定要删除这个分类吗？', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          deleteCategory(id)
            .then(response => {
              console.log('删除分类成功:', response.data)
              this.$message.success('删除分类成功')
              this.fetchCategories()
            })
            .catch(error => {
              this.$message.error('删除分类失败: ' + error.message)
            })
        })
        .catch(() => { })
    },
    resetForm() {
      this.searchForm = {
        name: ''
      }
      this.fetchCategories()
    },
    handleSizeChange(size) {
      this.pagination.size = size
      this.fetchCategories()
    },
    handleCurrentChange(current) {
      this.pagination.current = current
      this.fetchCategories()
    }
  }
}
</script>

<style scoped>
.category-management {
  padding: 20px;
  min-height: 100vh;
  background-color: #f5f7fa;
}

/* 页面标题 */
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

/* 筛选卡片 */
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

/* 列表卡片 */
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
  border-right: 1px solid #dcdfe6;
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

/* 增强表格边框可见度 */
.el-table {
  border: 1px solid #dcdfe6;
}

.el-table--border {
  border: 1px solid #dcdfe6;
}

.el-table--border th,
.el-table--border td {
  border-right: 1px solid #dcdfe6;
}

.el-table--border tr {
  border-bottom: 1px solid #dcdfe6;
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

/* 按钮样式 */
.el-button {
  border-radius: 4px;
  transition: all 0.3s ease;
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

/* 表单样式 */
.el-form-item {
  margin-bottom: 20px;
}

.el-form-item__label {
  font-weight: 500;
  color: #303133;
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
  .category-management {
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