<template>
  <div class="banner-management">

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="Banner名称">
          <el-input v-model="searchForm.title" placeholder="请输入Banner名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchBanners">
            <i class="el-icon-search"></i> 搜索
          </el-button>
          <el-button @click="resetForm">
            <i class="el-icon-refresh"></i> 重置
          </el-button>
          <el-button type="primary" @click="handleAdd">
            <i class="el-icon-plus"></i> 添加Banner
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Banner列表 -->
    <el-card class="list-card">
      <el-table v-loading="loading" :data="banners" style="width: 100%">
        <el-table-column prop="id" label="Banner ID" width="100" />
        <el-table-column prop="title" label="Banner名称" />
        <el-table-column prop="link_url" label="链接地址" />
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column label="状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.is_active === 1 ? 'success' : 'danger'">
              {{ scope.row.is_active === 1 ? '启用' : '禁用' }}
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
        <el-form-item label="Banner名称" required>
          <el-input v-model="form.title" placeholder="请输入Banner名称" />
        </el-form-item>
        <el-form-item label="链接地址">
          <el-input v-model="form.link_url" placeholder="请输入链接地址" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" :max="999" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template slot="footer">
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { getBanners, createBanner, updateBanner, deleteBanner } from '@/api/mall'

export default {
  name: 'BannerList',
  data() {
    return {
      loading: false,
      banners: [],
      searchForm: {
        title: ''
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
        title: '',
        link_url: '',
        image: '',
        sort_order: 0,
        is_active: true
      }
    }
  },
  mounted() {
    this.fetchBanners()
  },
  methods: {
    fetchBanners() {
      this.loading = true
      const params = {
        page: this.pagination.current,
        page_size: this.pagination.size,
        search: this.searchForm.title
      }
      getBanners(params)
        .then(response => {
          // 检查后端返回格式
          let bannerData = []
          if (response.data.results && response.data.count) {
            // 后端返回 { results: [...], count: number } 格式
            bannerData = response.data.results
            this.pagination.total = response.data.count
          } else {
            // 后端直接返回数组格式
            bannerData = response.data
            this.pagination.total = response.data.length
          }

          // 映射后端字段到前端字段
          this.banners = bannerData.map(item => ({
            ...item,
            link_url: item.link,  // 后端字段是link，前端使用link_url
            sort_order: item.sort,  // 后端字段是sort，前端使用sort_order
            image: item.image  // 后端字段是image，前端使用image
          }))
        })
        .catch(error => {
          this.$message.error('获取Banner列表失败: ' + error.message)
        })
        .finally(() => {
          this.loading = false
        })
    },
    handleAdd() {
      this.dialogTitle = '添加Banner'
      this.form = {
        id: '',
        title: '',
        link_url: '',
        image: '',
        sort_order: 0,
        is_active: true
      }
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.dialogTitle = '编辑Banner'
      this.form = { ...row }
      // 确保状态字段被正确处理
      this.form.is_active = !!this.form.is_active
      this.dialogVisible = true
    },
    handleSubmit() {
      if (!this.form.title) {
        this.$message.error('请输入Banner名称')
        return
      }

      // 准备提交数据，将前端字段映射回后端字段
      const submitData = {
        title: this.form.title,
        link: this.form.link_url || '',  // 前端使用link_url，后端需要link，允许为空
        image: this.form.image || '',  // 前端使用image，后端需要image，允许为空
        sort: this.form.sort_order,  // 前端使用sort_order，后端需要sort
        is_active: this.form.is_active ? 1 : 0  // 前端使用布尔值，后端需要数字
      }

      const request = this.form.id ? updateBanner(this.form.id, submitData) : createBanner(submitData)
      request
        .then(() => {
          this.$message.success(this.form.id ? '更新Banner成功' : '添加Banner成功')
          this.dialogVisible = false
          this.fetchBanners()
        })
        .catch(error => {
          this.$message.error((this.form.id ? '更新Banner' : '添加Banner') + '失败: ' + error.message)
        })
    },
    handleDelete(id) {
      this.$confirm('确定要删除这个Banner吗？', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          deleteBanner(id)
            .then(() => {
              this.$message.success('删除Banner成功')
              this.fetchBanners()
            })
            .catch(error => {
              this.$message.error('删除Banner失败: ' + error.message)
            })
        })
        .catch(() => { })
    },
    resetForm() {
      this.searchForm = {
        title: ''
      }
      this.fetchBanners()
    },
    handleSizeChange(size) {
      this.pagination.size = size
      this.fetchBanners()
    },
    handleCurrentChange(current) {
      this.pagination.current = current
      this.fetchBanners()
    }
  }
}
</script>

<style scoped>
.banner-management {
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
  border-right: 1px solid #c0c4cc;
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

/* 加载动画 */
.el-loading {
  background-color: rgba(255, 255, 255, 0.8);
}

.el-loading-spinner .path {
  stroke: #409EFF;
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
  .banner-management {
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