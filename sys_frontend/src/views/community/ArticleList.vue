<template>
  <div class="article-list">

    <!-- 筛选和搜索 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filter" class="filter-form">
        <el-form-item label="专栏">
          <el-select v-model="filter.column_id" placeholder="选择专栏" clearable>
            <el-option v-for="column in columns" :key="column.id" :label="column.name" :value="column.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input v-model="filter.search" placeholder="搜索文章标题" clearable @keyup.enter.native="loadArticles"
            style="width: 250px">
            <el-button slot="append" icon="el-icon-search" @click="loadArticles"></el-button>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadArticles">
            <i class="el-icon-search"></i> 搜索
          </el-button>
          <el-button @click="resetFilter">
            <i class="el-icon-refresh"></i> 重置
          </el-button>
          <el-button type="primary" @click="handleCreate" class="create-button" :icon="'el-icon-plus'">
            新建文章
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 文章列表 -->
    <el-card class="list-card">

      <el-table :data="articles" v-loading="loading" style="width: 100%" border>
        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
        <el-table-column prop="title" label="标题">
          <template slot-scope="scope">
            <a href="javascript:void(0)" @click="handleView(scope.row)" class="article-title">{{ scope.row.title }}</a>
          </template>
        </el-table-column>
        <el-table-column prop="column_name" label="所属专栏" width="180" align="center"></el-table-column>
        <el-table-column prop="view_count" label="浏览量" width="100" align="center"></el-table-column>
        <el-table-column prop="like_count" label="点赞数" width="100" align="center"></el-table-column>
        <el-table-column prop="comment_count" label="评论数" width="100" align="center"></el-table-column>
        <el-table-column prop="published_at" label="发布时间" width="180" align="center">
          <template slot-scope="scope">
            {{ formatDate(scope.row.published_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template slot-scope="scope">
            <div class="action-buttons">
              <el-button type="primary" size="small" @click="handleEdit(scope.row)" class="action-btn edit-btn">
                <i class="el-icon-edit"></i> 编辑
              </el-button>
              <el-button type="danger" size="small" @click="handleDelete(scope.row)" class="action-btn delete-btn">
                <i class="el-icon-delete"></i> 删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange"
          :current-page="pagination.page" :page-sizes="[10, 20, 50, 100]" :page-size="pagination.page_size"
          layout="total, sizes, prev, pager, next, jumper" :total="pagination.total"></el-pagination>
      </div>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog :title="dialog.title" :visible.sync="dialog.visible" width="80%" :modal="false">
      <el-form :model="form" :rules="rules" ref="form" label-width="100px">
        <el-form-item label="所属专栏" prop="column_id">
          <el-select v-model="form.column_id" placeholder="请选择专栏">
            <el-option v-for="column in columns" :key="column.id" :label="column.name" :value="column.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="文章标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入文章标题" maxlength="200"></el-input>
        </el-form-item>
        <el-form-item label="文章封面图" prop="cover_image">
          <el-upload class="avatar-uploader" :action="uploadUrl" :show-file-list="false" :on-success="handleImageUpload"
            :before-upload="beforeAvatarUpload">
            <img v-if="form.cover_image"
              :src="form.cover_image.includes('http') ? form.cover_image : 'https://static.lovesync-diary.top/' + form.cover_image"
              class="avatar">
            <i v-else class="el-icon-plus avatar-uploader-icon"></i>
          </el-upload>
        </el-form-item>
        <el-form-item label="文章内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="10" placeholder="请输入文章内容"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'ArticleList',
  data() {
    return {
      loading: false,
      articles: [],
      columns: [],
      filter: {
        column_id: '',
        search: ''
      },
      pagination: {
        page: 1,
        page_size: 10,
        total: 0
      },
      dialog: {
        visible: false,
        title: '新建文章'
      },
      form: {
        id: '',
        column_id: '',
        title: '',
        content: '',
        cover_image: ''
      },
      rules: {
        column_id: [{ required: true, message: '请选择专栏', trigger: 'change' }],
        title: [{ required: true, message: '请输入文章标题', trigger: 'blur' }],
        content: [{ required: true, message: '请输入文章内容', trigger: 'blur' }]
      },
      uploadUrl: '/api/upload/' // 上传图片的接口
    }
  },
  created() {
    this.loadColumns()
    this.loadArticles()
  },
  methods: {
    async loadColumns() {
      try {
        const response = await this.$axios.get('/api/articles_manage/columns/')
        if (response.data.success) {
          this.columns = response.data.data
        }
      } catch (error) {
        this.$message.error('获取专栏列表失败')
        console.error('Error loading columns:', error)
      }
    },
    async loadArticles() {
      this.loading = true
      try {
        const params = {
          page: this.pagination.page,
          page_size: this.pagination.page_size,
          column_id: this.filter.column_id,
          search: this.filter.search
        }
        const response = await this.$axios.get('/api/articles_manage/articles/', { params })
        if (response.data.success) {
          // 处理文章数据，添加专栏名称
          this.articles = response.data.data.map(article => {
            const column = this.columns.find(c => c.id === article.column_id)
            return {
              ...article,
              column_name: column ? column.name : '未知专栏'
            }
          })
          this.pagination.total = response.data.total || this.articles.length
        }
      } catch (error) {
        this.$message.error('获取文章列表失败')
        console.error('Error loading articles:', error)
      } finally {
        this.loading = false
      }
    },
    handleCreate() {
      this.dialog.title = '新建文章'
      this.form = {
        id: '',
        column_id: '',
        title: '',
        content: '',
        cover_image: ''
      }
      this.dialog.visible = true
    },
    handleEdit(article) {
      this.dialog.title = '编辑文章'
      // 从完整URL中提取相对路径，移除域名部分
      let coverImage = article.cover_image
      if (coverImage && coverImage.includes('https://static.lovesync-diary.top/')) {
        coverImage = coverImage.replace('https://static.lovesync-diary.top/', '')
      }
      this.form = {
        id: article.id,
        column_id: article.column_id,
        title: article.title,
        content: article.content,
        cover_image: coverImage
      }
      this.dialog.visible = true
    },
    async handleSubmit() {
      try {
        this.$refs.form.validate(async (valid) => {
          if (valid) {
            let response
            if (this.form.id) {
              // 更新文章
              response = await this.$axios.put(`/api/articles_manage/articles/${this.form.id}/update/`, this.form)
            } else {
              // 创建文章
              response = await this.$axios.post('/api/articles_manage/articles/create/', this.form)
            }
            if (response.data.success) {
              this.$message.success(this.form.id ? '更新成功' : '创建成功')
              this.dialog.visible = false
              this.loadArticles()
            }
          }
        })
      } catch (error) {
        this.$message.error(this.form.id ? '更新失败' : '创建失败')
        console.error('Error submitting article:', error)
      }
    },
    handleDelete(article) {
      this.$confirm('确定要删除这篇文章吗？', '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          const response = await this.$axios.delete(`/api/articles_manage/articles/${article.id}/delete/`)
          if (response.data.success) {
            this.$message.success('删除成功')
            this.loadArticles()
          }
        } catch (error) {
          this.$message.error('删除失败')
          console.error('Error deleting article:', error)
        }
      }).catch(() => {
        // 用户取消删除
      })
    },
    handleView(article) {
      this.$router.push(`/articles/${article.id}`)
    },
    handleSizeChange(size) {
      this.pagination.page_size = size
      this.loadArticles()
    },
    handleCurrentChange(current) {
      this.pagination.page = current
      this.loadArticles()
    },
    resetFilter() {
      this.filter = {
        column_id: '',
        search: ''
      }
      this.pagination.page = 1
      this.loadArticles()
    },
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    },
    handleImageUpload(response) {
      if (response.success) {
        // 从完整URL中提取相对路径，移除域名部分
        let url = response.data.url;
        // 移除域名部分，只保留相对路径
        url = url.replace('https://static.lovesync-diary.top/', '');
        this.form.cover_image = url;
      }
    },
    beforeAvatarUpload(file) {
      const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
      const isLt2M = file.size / 1024 / 1024 < 2

      if (!isJPG) {
        this.$message.error('上传图片只能是 JPG/PNG 格式!')
      }
      if (!isLt2M) {
        this.$message.error('上传图片大小不能超过 2MB!')
      }
      return isJPG && isLt2M
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
$transition-base: all 0.3s ease;

// 基础样式
.article-list {
  padding: 20px;
  background-color: $bg-color;
  min-height: calc(100vh - 84px);
}

// 页面标题和操作区
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid $border-color;

  .header-left {
    h1 {
      font-size: 24px;
      font-weight: 600;
      color: $text-color;
      margin: 0 0 4px 0;
    }

    p {
      font-size: 14px;
      color: $info-color;
      margin: 0;
    }
  }

  .header-right {
    .create-button {
      display: flex;
      align-items: center;
      font-size: 14px;
      padding: 8px 16px;
      border-radius: 4px;
      transition: $transition-base;

      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      }
    }
  }
}

// 筛选和搜索区
.filter-card {
  margin-bottom: 24px;
  border-radius: $border-radius;
  box-shadow: $shadow-base;
  transition: box-shadow $transition-base;
  overflow: hidden;

  &:hover {
    box-shadow: $shadow-hover;
  }

  .filter-form {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 4px 0;
  }
}

// 文章列表
.list-card {
  margin-bottom: 24px;
  border-radius: $border-radius;
  box-shadow: $shadow-base;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background-color: #fafafa;
  border-bottom: 1px solid $border-color;

  span {
    font-size: 16px;
    font-weight: 500;
    color: $text-color;
  }

  .header-info {
    font-size: 14px;
    color: $info-color;
  }
}

// 表格样式
.el-table {
  border-radius: 0;

  .el-table__header-wrapper th {
    background-color: #fafafa;
    font-weight: 500;
    color: $text-color;
  }

  .el-table__body-wrapper tr {
    transition: background-color 0.2s ease;

    &:hover {
      background-color: $hover-bg !important;
    }
  }
}

// 文章标题链接
.article-title {
  color: $primary-color;
  text-decoration: none;
  transition: color 0.2s ease;

  &:hover {
    color: #66b1ff;
    text-decoration: underline;
  }
}

// 分页
.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
}

// 头像上传
.avatar-uploader {
  display: flex;
  align-items: center;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 8px;
  object-fit: cover;
  transition: all 0.3s ease;

  &:hover {
    transform: scale(1.02);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #c0c4cc;
  width: 120px;
  height: 120px;
  line-height: 120px;
  text-align: center;
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    border-color: $primary-color;
    color: $primary-color;
  }
}

// 对话框
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

// 操作按钮
.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
}

.action-btn {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 4px;
  transition: $transition-base;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
}

.edit-btn {
  background-color: #409EFF;
  border-color: #409EFF;

  &:hover {
    background-color: #66b1ff;
    border-color: #66b1ff;
  }
}

.delete-btn {
  background-color: #F56C6C;
  border-color: #F56C6C;

  &:hover {
    background-color: #f78989;
    border-color: #f78989;
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .article-list {
    padding: 16px;
  }

  .filter-form {
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .article-list {
    padding: 12px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding-bottom: 12px;

    .header-right {
      width: 100%;
      display: flex;
      justify-content: flex-start;
    }
  }

  .filter-card .filter-form {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .filter-card .el-form-item {
    margin-bottom: 0;
  }

  .list-card .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    padding: 12px 16px;
  }

  .el-table {
    .el-table__body-wrapper {
      .el-button {
        margin-right: 4px;
        padding: 3px 8px;
        font-size: 11px;
      }
    }
  }
}
</style>
