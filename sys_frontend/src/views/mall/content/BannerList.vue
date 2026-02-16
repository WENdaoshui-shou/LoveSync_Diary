<template>
  <div class="banner-management">
    <el-card shadow="never">
      <div slot="header" class="card-header">
        <span>Banner管理</span>
        <el-button type="primary" size="small" @click="handleAdd">
          <i class="el-icon-plus"></i> 添加Banner
        </el-button>
      </div>
      
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
        </el-form-item>
      </el-form>
      
      <el-table v-loading="loading" :data="banners" style="width: 100%">
        <el-table-column prop="id" label="Banner ID" width="80" />
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
        <el-table-column label="操作" width="150" fixed="right">
          <template slot-scope="scope">
            <el-button type="primary" size="small" @click="handleEdit(scope.row)">
              <i class="el-icon-edit"></i> 编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row.id)">
              <i class="el-icon-delete"></i> 删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          :current-page="pagination.current"
          :page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 添加/编辑对话框 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="Banner名称" required>
          <el-input v-model="form.title" placeholder="请输入Banner名称" />
        </el-form-item>
        <el-form-item label="链接地址" required>
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
          // 后端直接返回数组格式，不是 { results: [...], count: number } 格式
          // 映射后端字段到前端字段
          this.banners = response.data.map(item => ({
            ...item,
            link_url: item.link,  // 后端字段是link，前端使用link_url
            sort_order: item.sort  // 后端字段是sort，前端使用sort_order
          }))
          this.pagination.total = response.data.length
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
        sort_order: 0,
        is_active: true
      }
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.dialogTitle = '编辑Banner'
      this.form = { ...row }
      this.dialogVisible = true
    },
    handleSubmit() {
      if (!this.form.title) {
        this.$message.error('请输入Banner名称')
        return
      }
      if (!this.form.link_url) {
        this.$message.error('请输入链接地址')
        return
      }
      
      // 准备提交数据，将前端字段映射回后端字段
      const submitData = {
        title: this.form.title,
        link: this.form.link_url,  // 前端使用link_url，后端需要link
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
        .catch(() => {})
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
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}



.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
}
</style>