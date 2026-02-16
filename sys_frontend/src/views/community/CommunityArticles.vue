<template>
  <div class="community-articles">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>文章专栏管理</h1>
      <el-button type="primary" @click="handleCreate" icon="el-icon-plus">
        创建专栏
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="statistics-row">
      <el-col :span="6">
        <el-card class="statistics-card">
          <div class="statistics-item">
            <div class="statistics-label">总专栏数</div>
            <div class="statistics-value">{{ statistics.total_columns || 0 }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="statistics-card">
          <div class="statistics-item">
            <div class="statistics-label">启用专栏</div>
            <div class="statistics-value">{{ statistics.active_columns || 0 }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="statistics-card">
          <div class="statistics-item">
            <div class="statistics-label">总订阅数</div>
            <div class="statistics-value">{{ statistics.total_subscribers || 0 }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="statistics-card">
          <div class="statistics-item">
            <div class="statistics-label">总浏览量</div>
            <div class="statistics-value">{{ statistics.total_views || 0 }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选条件 -->
    <el-form :inline="true" :model="filterForm" class="filter-form">
      <el-form-item label="搜索">
        <el-input v-model="filterForm.search" placeholder="专栏名称/描述" clearable />
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="filterForm.is_active" placeholder="状态" clearable>
          <el-option label="启用" value="true" />
          <el-option label="禁用" value="false" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch" icon="el-icon-search">
          查询
        </el-button>
        <el-button @click="resetFilter" icon="el-icon-refresh">
          重置
        </el-button>
      </el-form-item>
    </el-form>

    <!-- 专栏列表 -->
    <el-table :data="columnList" v-loading="loading" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" align="center" />
      <el-table-column label="专栏信息" min-width="300">
        <template slot-scope="scope">
          <div class="column-info" v-if="scope.row">
            <div class="column-name">{{ scope.row.name }}</div>
            <div class="column-slug">{{ scope.row.slug }}</div>
            <div class="column-description">{{ scope.row.description || '无描述' }}</div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="分类" width="120" align="center">
        <template slot-scope="scope">
          <el-tag v-if="scope.row" type="info" size="small">
            {{ scope.row.category_display }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="数据统计" width="180" align="center">
        <template slot-scope="scope">
          <div class="column-stats" v-if="scope.row">
            <div>订阅: {{ scope.row.subscriber_count || 0 }}</div>
            <div>浏览: {{ scope.row.view_count || 0 }}</div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80" align="center">
        <template slot-scope="scope">
          <el-tag v-if="scope.row" :type="scope.row.is_active ? 'success' : 'info'" size="small">
            {{ scope.row.status_display }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="更新时间" width="160" align="center">
        <template slot-scope="scope">
          <span v-if="scope.row">{{ scope.row.updated_at }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" align="center">
        <template slot-scope="scope">
          <el-button v-if="scope.row" size="mini" @click="handleEdit(scope.row)" icon="el-icon-edit">
            编辑
          </el-button>
          <el-button v-if="scope.row" size="mini" type="danger" @click="handleDelete(scope.row.id)"
            icon="el-icon-delete">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination :current-page="currentPage" :page-size="pageSize" :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="handleSizeChange"
        @current-change="handleCurrentChange" />
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="form" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="专栏名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入专栏名称" />
        </el-form-item>
        <el-form-item label="专栏标识" prop="slug">
          <el-input v-model="form.slug" placeholder="请输入专栏标识（英文）" />
        </el-form-item>
        <el-form-item label="专栏描述">
          <el-input v-model="form.description" type="textarea" rows="3" placeholder="请输入专栏描述" />
        </el-form-item>
        <el-form-item label="专栏分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择专栏分类">
            <el-option label="恋爱成长手册" value="love_growth" />
            <el-option label="日记灵感库" value="diary_inspiration" />
            <el-option label="节日特辑" value="festival_special" />
            <el-option label="平台活动通知" value="platform_activity" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="专栏封面">
          <el-upload class="avatar-uploader" action="#" :auto-upload="false" :on-change="handleImageChange"
            :show-file-list="false">
            <img v-if="form.cover_image" :src="form.cover_image" class="avatar" />
            <i v-else class="el-icon-plus avatar-uploader-icon"></i>
          </el-upload>
          <div class="upload-tip">点击上传专栏封面图片</div>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" />
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
import { getColumnList, getColumnDetail, createColumn, updateColumn, deleteColumn, getColumnStatistics } from '@/api/community'

export default {
  name: 'CommunityArticles',
  data() {
    return {
      loading: false,
      columnList: [],
      total: 0,
      currentPage: 1,
      pageSize: 10,
      filterForm: {
        search: '',
        is_active: ''
      },
      statistics: {
        total_columns: 0,
        active_columns: 0,
        total_subscribers: 0,
        total_views: 0
      },
      dialogVisible: false,
      dialogTitle: '',
      form: {
        name: '',
        slug: '',
        description: '',
        cover_image: '',
        category: 'other',
        is_active: true
      },
      rules: {
        name: [{ required: true, message: '请输入专栏名称', trigger: 'blur' }],
        slug: [{ required: true, message: '请输入专栏标识', trigger: 'blur' }],
        category: [{ required: true, message: '请选择专栏分类', trigger: 'change' }]
      }
    }
  },
  created() {
    this.loadData()
    this.loadStatistics()
  },
  methods: {
    // 加载数据
    async loadData() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          page_size: this.pageSize,
          ...this.filterForm
        }
        const response = await getColumnList(params)
        if (response.data) {
          this.columnList = response.data.results || []
          this.total = response.data.count || 0
        }
      } catch (error) {
        this.$message.error('加载专栏列表失败')
        console.error('加载专栏列表失败:', error)
      } finally {
        this.loading = false
      }
    },

    // 加载统计数据
    async loadStatistics() {
      try {
        const response = await getColumnStatistics()
        if (response.data) {
          this.statistics = response.data
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    },

    // 搜索
    handleSearch() {
      this.currentPage = 1
      this.loadData()
    },

    // 重置
    resetFilter() {
      this.filterForm = {
        search: '',
        is_active: ''
      }
      this.currentPage = 1
      this.loadData()
    },

    // 分页处理
    handleSizeChange(size) {
      this.pageSize = size
      this.loadData()
    },

    handleCurrentChange(current) {
      this.currentPage = current
      this.loadData()
    },

    // 创建专栏
    handleCreate() {
      this.dialogTitle = '创建专栏'
      this.form = {
        name: '',
        slug: '',
        description: '',
        cover_image: '',
        category: 'other',
        is_active: true
      }
      this.dialogVisible = true
    },

    // 编辑专栏
    handleEdit(column) {
      this.dialogTitle = '编辑专栏'
      this.form = {
        ...column
      }
      this.dialogVisible = true
    },

    // 删除专栏
    handleDelete(id) {
      this.$confirm('确定要删除这个专栏吗？', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await deleteColumn(id)
          this.$message.success('删除成功')
          this.loadData()
          this.loadStatistics()
        } catch (error) {
          this.$message.error('删除失败')
          console.error('删除专栏失败:', error)
        }
      }).catch(() => {
        // 取消删除
      })
    },

    // 提交表单
    async handleSubmit() {
      this.$refs.form.validate(async (valid) => {
        if (valid) {
          try {
            if (this.form.id) {
              // 更新专栏
              await updateColumn(this.form.id, this.form)
              this.$message.success('更新成功')
            } else {
              // 创建专栏
              await createColumn(this.form)
              this.$message.success('创建成功')
            }
            this.dialogVisible = false
            this.loadData()
            this.loadStatistics()
          } catch (error) {
            this.$message.error('操作失败')
            console.error('提交表单失败:', error)
          }
        }
      })
    },

    // 图片上传处理
    handleImageChange(file) {
      // 这里可以添加图片上传逻辑
      // 暂时直接设置为文件路径
      this.form.cover_image = URL.createObjectURL(file.raw)
    }
  }
}
</script>

<style scoped>
.community-articles {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
}

.statistics-row {
  margin-bottom: 20px;
}

.statistics-card {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.statistics-item {
  text-align: center;
  padding: 10px;
}

.statistics-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.statistics-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.filter-form {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.column-info {
  line-height: 1.5;
}

.column-name {
  font-weight: bold;
  margin-bottom: 4px;
}

.column-slug {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.column-description {
  font-size: 12px;
  color: #666;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.column-stats {
  font-size: 12px;
  line-height: 1.5;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
  width: 150px;
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-uploader .el-upload:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 150px;
  height: 150px;
  line-height: 150px;
  text-align: center;
}

.avatar {
  width: 150px;
  height: 150px;
  display: block;
}

.upload-tip {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.dialog-footer {
  text-align: right;
}
</style>