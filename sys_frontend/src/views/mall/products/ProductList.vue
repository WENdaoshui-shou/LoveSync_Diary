<template>
  <div class="product-list">

    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="商品名称">
          <el-input v-model="filterForm.search" placeholder="搜索商品名称" clearable @clear="handleSearch"
            @keyup.enter="handleSearch" style="width: 200px"></el-input>
        </el-form-item>
        <el-form-item label="商品分类">
          <el-select v-model="filterForm.category" placeholder="选择分类" clearable>
            <el-option label="全部" value=""></el-option>
            <el-option v-for="category in categories" :key="category.id" :label="category.name"
              :value="category.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="上架状态">
          <el-select v-model="filterForm.is_active" placeholder="选择状态" clearable>
            <el-option label="全部" value=""></el-option>
            <el-option label="已上架" value="true"></el-option>
            <el-option label="未上架" value="false"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetFilter">重置</el-button>
          <el-button type="primary" @click="handleAddProduct">
            <i class="el-icon-plus"></i> 添加商品
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="list-card">
      <div class="header-info">
        <el-tag size="small">总计: {{ total }} 件商品</el-tag>
      </div>


      <el-table :data="products" v-loading="loading" border style="width: 100%; margin-bottom: 20px;">
        <el-table-column prop="id" label="ID" width="100" align="center">
          <template slot-scope="scope">
            <span>{{ scope.row.id.substring(0, 8) }}...</span>
          </template>
        </el-table-column>
        <el-table-column label="商品图片" width="120" align="center">
          <template slot-scope="scope">
            <img v-if="scope.row.main_image" :src="getImageUrl(scope.row.main_image)" class="product-image" />
            <div v-else class="no-image">无图片</div>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="商品名称" min-width="200"></el-table-column>
        <el-table-column prop="price" label="价格" width="100" align="center">
          <template slot-scope="scope">
            <span class="price">¥{{ scope.row.price }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="old_price" label="原价" width="100" align="center">
          <template slot-scope="scope">
            <span class="old-price">¥{{ scope.row.old_price }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="category_id" label="分类" width="120" align="center">
          <template slot-scope="scope">
            <span>{{ getCategoryName(scope.row.category_id) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="product_stock" label="库存" width="100" align="center">
          <template slot-scope="scope">
            <span :class="{ 'low-stock': scope.row.product_stock < 10 }">
              {{ scope.row.product_stock }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="monthly_sales" label="月销量" width="100" align="center">
          <template slot-scope="scope">
            <span class="sales">{{ scope.row.monthly_sales }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template slot-scope="scope">
            <el-tag type="success" effect="dark" v-if="scope.row.is_active">已上架</el-tag>
            <el-tag type="info" effect="plain" v-else>未上架</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180" align="center">
          <template slot-scope="scope">
            <span>{{ formatDateTime(scope.row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="center" fixed="right">
          <template slot-scope="scope">
            <el-button type="primary" size="mini" @click="editProduct(scope.row)"
              style="margin-right: 8px">编辑</el-button>
            <el-button type="danger" size="mini" @click="deleteProduct(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange" :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]" :page-size="pageSize" layout="total, sizes, prev, pager, next, jumper"
          :total="total"></el-pagination>
      </div>
    </el-card>

    <!-- 查看/编辑对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="600px" :modal="false">
      <el-form :model="form" label-width="100px">
        <el-form-item label="商品名称" required>
          <el-input v-model="form.name" placeholder="请输入商品名称"></el-input>
        </el-form-item>
        <el-form-item label="商品描述">
          <el-input type="textarea" v-model="form.description" placeholder="请输入商品描述" :rows="3"></el-input>
        </el-form-item>
        <el-form-item label="价格" required>
          <el-input type="number" v-model="form.price" placeholder="请输入价格" min="0"></el-input>
        </el-form-item>
        <el-form-item label="原价">
          <el-input type="number" v-model="form.old_price" placeholder="请输入原价" min="0"></el-input>
        </el-form-item>
        <el-form-item label="商品主图">
          <el-upload class="avatar-uploader" action="/admin-api/upload/image/" :show-file-list="false"
            :on-success="handleImageUpload" :before-upload="beforeUpload">
            <img v-if="form.main_image" :src="getImageUrl(form.main_image)" class="avatar">
            <i v-else class="el-icon-plus avatar-uploader-icon"></i>
          </el-upload>
        </el-form-item>
        <el-form-item label="详情图">
          <el-upload class="avatar-uploader" action="/admin-api/upload/image/" :show-file-list="false"
            :on-success="(response) => handleImageUpload(response, 'detail_image')" :before-upload="beforeUpload">
            <img v-if="form.detail_image" :src="getImageUrl(form.detail_image)" class="avatar">
            <i v-else class="el-icon-plus avatar-uploader-icon"></i>
          </el-upload>
        </el-form-item>
        <el-form-item label="SKU图">
          <el-upload class="avatar-uploader" action="/admin-api/upload/image/" :show-file-list="false"
            :on-success="(response) => handleImageUpload(response, 'sku_image')" :before-upload="beforeUpload">
            <img v-if="form.sku_image" :src="getImageUrl(form.sku_image)" class="avatar">
            <i v-else class="el-icon-plus avatar-uploader-icon"></i>
          </el-upload>
        </el-form-item>
        <el-form-item label="商品分类" required>
          <el-select v-model="form.category_id" placeholder="选择商品分类">
            <el-option v-for="category in categories" :key="category.id" :label="category.name"
              :value="category.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="库存" required>
          <el-input type="number" v-model="form.product_stock" placeholder="请输入库存" min="0"></el-input>
        </el-form-item>
        <el-form-item label="上架状态">
          <el-switch v-model="form.is_active"></el-switch>
        </el-form-item>
        <el-form-item label="情侣款">
          <el-switch v-model="form.is_couple_product"></el-switch>
        </el-form-item>
        <el-form-item label="新品">
          <el-switch v-model="form.is_new"></el-switch>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProduct">保存</el-button>
      </div>
    </el-dialog>

  </div>
</template>

<script>
import {
  getProducts,
  createProduct,
  updateProduct,
  deleteProduct,
  getCategories
} from '@/api/mall'

export default {
  name: 'ProductList',
  data() {
    return {
      loading: false,
      products: [],
      categories: [],
      total: 0,
      currentPage: 1,
      pageSize: 10,
      filterForm: {
        search: '',
        category: '',
        is_active: ''
      },
      dialogVisible: false,
      dialogTitle: '',
      form: {
        id: '',
        name: '',
        description: '',
        price: '',
        old_price: '',
        category_id: '',
        product_stock: '',
        is_active: true,
        is_couple_product: false,
        is_new: true,
        main_image: '',
        detail_image: '',
        sku_image: ''
      }
    }
  },
  created() {
    this.loadData()
    this.loadCategories()
  },
  methods: {
    async loadData() {
      this.loading = true
      try {
        const params = {
          search: this.filterForm.search,
          category: this.filterForm.category,
          is_active: this.filterForm.is_active
        }
        const response = await getProducts(params)
        this.products = response.data
        this.total = this.products.length
      } catch (error) {
        this.$message.error('加载失败')
      } finally {
        this.loading = false
      }
    },
    async loadCategories() {
      try {
        const response = await getCategories()
        this.categories = response.data
      } catch (error) {
        this.$message.error('加载分类失败')
      }
    },
    handleSearch() {
      this.currentPage = 1
      this.loadData()
    },
    resetFilter() {
      this.filterForm = {
        search: '',
        category: '',
        is_active: ''
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
    handleAddProduct() {
      this.dialogTitle = '添加商品'
      this.form = {
        id: null,
        name: '',
        description: '',
        price: '',
        old_price: '',
        category_id: '',
        product_stock: '',
        is_active: true,
        is_couple_product: false,
        is_new: true,
        main_image: '',
        detail_image: '',
        sku_image: ''
      }
      this.dialogVisible = true
    },
    handleImageUpload(response, field = 'main_image') {
      if (response.code === 200) {
        // 提取相对路径，去掉域名部分
        const imageUrl = response.data.url
        const relativePath = imageUrl.replace('https://static.lovesync-diary.top/', '')
        this.form[field] = relativePath
        this.$message.success('图片上传成功')
      } else {
        this.$message.error('图片上传失败')
      }
    },
    beforeUpload(file) {
      const isJPG = file.type === 'image/jpeg' || file.type === 'image/png' || file.type === 'image/gif'
      const isLt2M = file.size / 1024 / 1024 < 2

      if (!isJPG) {
        this.$message.error('只能上传JPG、PNG、GIF格式的图片!')
      }
      if (!isLt2M) {
        this.$message.error('图片大小不能超过2MB!')
      }
      return isJPG && isLt2M
    },

    editProduct(product) {
      this.dialogTitle = '编辑商品'
      this.form = { ...product }
      this.dialogVisible = true
    },
    async saveProduct() {
      try {
        if (this.form.id) {
          await updateProduct(this.form.id, this.form)
        } else {
          // 创建新商品时，不包含id字段
          const productData = { ...this.form }
          delete productData.id
          await createProduct(productData)
        }
        this.$message.success('保存成功')
        this.dialogVisible = false
        this.loadData()
      } catch (error) {
        this.$message.error('保存失败')
      }
    },
    async deleteProduct(product) {
      this.$confirm('确定要删除这个商品吗？', '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await deleteProduct(product.id)
          this.$message.success('删除成功')
          this.loadData()
        } catch (error) {
          this.$message.error('删除失败')
        }
      }).catch(() => { })
    },
    getCategoryName(categoryId) {
      const category = this.categories.find(c => c.id === categoryId)
      return category ? category.name : '未分类'
    },
    getImageUrl(path) {
      if (!path) return ''
      // 如果是完整URL，直接返回
      if (path.startsWith('http')) return path
      // 否则拼接完整URL
      return `https://static.lovesync-diary.top/${path}`
    },
    formatDateTime(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      const seconds = String(date.getSeconds()).padStart(2, '0')
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
    }
  }
}
</script>

<style scoped>
.product-list {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0;
  color: #303133;
}

.filter-card {
  margin-bottom: 20px;
}

.list-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-info {
  display: flex;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

/* 图片上传样式 */
.avatar-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-uploader:hover {
  border-color: #409EFF;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  text-align: center;
  line-height: 100px;
}

.avatar {
  width: 100px;
  height: 100px;
  display: block;
  object-fit: cover;
}

/* 商品列表图片样式 */
.product-image {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.product-image:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* 优化表格样式 */
.el-table {
  border-radius: 8px;
  overflow: hidden;
}

.el-table th {
  background-color: #f5f7fa;
  font-weight: 600;
  color: #303133;
}

.el-table tr:hover {
  background-color: #fafafa;
}

/* 优化表单样式 */
.el-form-item {
  margin-bottom: 20px;
}

.el-form-item__label {
  font-weight: 500;
  color: #303133;
}

/* 优化对话框样式 */
.el-dialog {
  border-radius: 8px;
  overflow: hidden;
}

.el-dialog__header {
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.el-dialog__title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 优化按钮样式 */
.el-button--primary {
  background-color: #409EFF;
  border-color: #409EFF;
}

.el-button--primary:hover {
  background-color: #66b1ff;
  border-color: #66b1ff;
}

/* 优化标签样式 */
.el-tag {
  border-radius: 4px;
  padding: 0 10px;
  height: 24px;
  line-height: 22px;
}

/* 优化输入框样式 */
.el-input__inner {
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  transition: all 0.3s ease;
}

.el-input__inner:focus {
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

/* 无图片占位样式 */
.no-image {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
  color: #909399;
  font-size: 12px;
}

/* 价格样式 */
.price {
  font-size: 14px;
  font-weight: 600;
  color: #F56C6C;
}

/* 旧价格样式 */
.old-price {
  font-size: 12px;
  color: #909399;
  text-decoration: line-through;
}

/* 低库存样式 */
.low-stock {
  color: #F56C6C;
  font-weight: 600;
}

/* 销量样式 */
.sales {
  font-size: 13px;
  color: #67C23A;
  font-weight: 500;
}

/* 优化表格行高 */
.el-table__row {
  height: 80px;
}

/* 优化表格单元格垂直居中 */
.el-table__cell {
  vertical-align: middle !important;
}

/* 优化卡片样式 */
.list-card {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.list-card:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.12);
}

/* 优化头部信息样式 */
.card-header {
  padding: 15px 20px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.card-header span {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 优化筛选卡片样式 */
.filter-card {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.filter-card:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.12);
}

/* 优化按钮样式 */
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
</style>
