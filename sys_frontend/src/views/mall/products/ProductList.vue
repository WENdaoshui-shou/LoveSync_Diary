<template>
  <div class="product-list">
    <div class="page-header">
      <h1>商品列表</h1>
      <el-button type="primary" @click="handleAddProduct">
        <i class="el-icon-plus"></i> 添加商品
      </el-button>
    </div>

    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="商品名称">
          <el-input v-model="filterForm.search" placeholder="搜索商品名称" clearable @clear="handleSearch" @keyup.enter="handleSearch" style="width: 200px"></el-input>
        </el-form-item>
        <el-form-item label="商品分类">
          <el-select v-model="filterForm.category" placeholder="选择分类" clearable>
            <el-option label="全部" value=""></el-option>
            <el-option v-for="category in categories" :key="category.id" :label="category.name" :value="category.id"></el-option>
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
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="list-card">
      <div slot="header" class="card-header">
        <span>商品列表</span>
        <div class="header-info">
          <el-tag size="small">总计: {{ total }} 件商品</el-tag>
        </div>
      </div>

      <el-table :data="products" v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
        <el-table-column prop="name" label="商品名称" min-width="180"></el-table-column>
        <el-table-column prop="price" label="价格" width="100" align="center">
          <template slot-scope="scope">
            <span>¥{{ scope.row.price }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="old_price" label="原价" width="100" align="center">
          <template slot-scope="scope">
            <span style="text-decoration: line-through; color: #999">¥{{ scope.row.old_price }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="category_id" label="分类" width="120" align="center">
          <template slot-scope="scope">
            <span>{{ getCategoryName(scope.row.category_id) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="product_stock" label="库存" width="100" align="center"></el-table-column>
        <el-table-column prop="monthly_sales" label="月销量" width="100" align="center"></el-table-column>
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template slot-scope="scope">
            <el-tag type="success" v-if="scope.row.is_active">已上架</el-tag>
            <el-tag type="info" v-else>未上架</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180"></el-table-column>
        <el-table-column label="操作" width="150" align="center">
          <template slot-scope="scope">
            <el-button type="text" size="mini" @click="viewProduct(scope.row)">查看</el-button>
            <el-button type="text" size="mini" @click="editProduct(scope.row)">编辑</el-button>
            <el-button type="text" size="mini" @click="deleteProduct(scope.row)" style="color: #F56C6C">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange" :current-page="currentPage" :page-sizes="[10, 20, 50, 100]" :page-size="pageSize" layout="total, sizes, prev, pager, next, jumper" :total="total"></el-pagination>
      </div>
    </el-card>

    <!-- 查看/编辑对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="600px">
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
        <el-form-item label="商品分类" required>
          <el-select v-model="form.category_id" placeholder="选择商品分类">
            <el-option v-for="category in categories" :key="category.id" :label="category.name" :value="category.id"></el-option>
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
        is_new: true
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
        id: '',
        name: '',
        description: '',
        price: '',
        old_price: '',
        category_id: '',
        product_stock: '',
        is_active: true,
        is_couple_product: false,
        is_new: true
      }
      this.dialogVisible = true
    },
    viewProduct(product) {
      this.dialogTitle = '查看商品'
      this.form = { ...product }
      this.dialogVisible = true
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
          await createProduct(this.form)
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
      }).catch(() => {})
    },
    getCategoryName(categoryId) {
      const category = this.categories.find(c => c.id === categoryId)
      return category ? category.name : '未分类'
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
</style>
