<template>
  <div class="address-management">

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="用户ID">
          <el-input v-model="searchForm.user_id" placeholder="请输入用户ID" clearable />
        </el-form-item>
        <el-form-item label="收货人">
          <el-input v-model="searchForm.recipient" placeholder="请输入收货人姓名" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchAddresses">
            <i class="el-icon-search"></i> 搜索
          </el-button>
          <el-button @click="resetForm">
            <i class="el-icon-refresh"></i> 重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 地址列表 -->
    <el-card class="list-card">
      <el-table v-loading="loading" :data="addresses" style="width: 100%">
        <el-table-column prop="id" label="地址ID" width="80" />
        <el-table-column prop="user_id" label="用户ID" width="80" />
        <el-table-column prop="recipient" label="收货人" width="100" />
        <el-table-column prop="phone" label="联系电话" width="120" />
        <el-table-column label="省份" width="100">
          <template slot-scope="scope">{{ scope.row.province || '-' }}</template>
        </el-table-column>
        <el-table-column label="城市" width="100">
          <template slot-scope="scope">{{ scope.row.city || '-' }}</template>
        </el-table-column>
        <el-table-column label="区县" width="100">
          <template slot-scope="scope">{{ scope.row.district || '-' }}</template>
        </el-table-column>
        <el-table-column prop="detail_address" label="详细地址">
          <template slot-scope="scope">
            <el-tooltip :content="scope.row.detail_address" placement="top">
              <div class="ellipsis">{{ scope.row.detail_address }}</div>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="是否默认" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.is_default === 1 ? 'success' : 'info'">
              {{ scope.row.is_default === 1 ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template slot-scope="scope">
            <div class="operation-buttons">
              <el-button type="primary" size="small" @click="handleView(scope.row)">
                <i class="el-icon-view"></i> 查看
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

    <!-- 地址详情对话框 -->
    <el-dialog title="地址详情" :visible.sync="detailVisible" width="600px" :modal="false">
      <div v-if="currentAddress" class="address-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="地址ID">{{ currentAddress.id }}</el-descriptions-item>
          <el-descriptions-item label="用户ID">{{ currentAddress.user_id }}</el-descriptions-item>
          <el-descriptions-item label="收货人">{{ currentAddress.recipient }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ currentAddress.phone }}</el-descriptions-item>
          <el-descriptions-item label="完整地址">
            {{ currentAddress.province }}{{ currentAddress.city }}{{ currentAddress.district }}{{
              currentAddress.detail_address }}
          </el-descriptions-item>
          <el-descriptions-item label="是否默认">{{ currentAddress.is_default === 1 ? '是' : '否' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentAddress.created_at }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ currentAddress.updated_at }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getAddresses, getAddressDetail, deleteAddress } from '@/api/mall'

export default {
  name: 'AddressList',
  data() {
    return {
      loading: false,
      addresses: [],
      searchForm: {
        user_id: '',
        recipient: ''
      },
      pagination: {
        current: 1,
        size: 10,
        total: 0
      },
      detailVisible: false,
      currentAddress: null
    }
  },
  mounted() {
    this.fetchAddresses()
  },
  methods: {
    fetchAddresses() {
      this.loading = true
      const params = {
        page: this.pagination.current,
        page_size: this.pagination.size,
        user_id: this.searchForm.user_id,
        recipient: this.searchForm.recipient
      }
      getAddresses(params)
        .then(response => {
          // 后端直接返回数组格式，不是 { results: [...], count: number } 格式
          this.addresses = response.data
          this.pagination.total = response.data.length
        })
        .catch(error => {
          this.$message.error('获取地址列表失败: ' + error.message)
        })
        .finally(() => {
          this.loading = false
        })
    },
    handleView(address) {
      this.loading = true
      getAddressDetail(address.id)
        .then(response => {
          this.currentAddress = response.data
          this.detailVisible = true
        })
        .catch(error => {
          // 当API返回404时，使用列表中已有的数据作为后备
          if (error.response && error.response.status === 404) {
            this.currentAddress = address
            this.detailVisible = true
            this.$message.warning('详情API不可用，显示列表数据')
          } else {
            this.$message.error('获取地址详情失败: ' + error.message)
          }
        })
        .finally(() => {
          this.loading = false
        })
    },
    handleDelete(id) {
      this.$confirm('确定要删除这个地址吗？', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          deleteAddress(id)
            .then(() => {
              this.$message.success('删除地址成功')
              this.fetchAddresses()
            })
            .catch(error => {
              this.$message.error('删除地址失败: ' + error.message)
            })
        })
        .catch(() => { })
    },
    resetForm() {
      this.searchForm = {
        user_id: '',
        recipient: ''
      }
      this.fetchAddresses()
    },
    handleSizeChange(size) {
      this.pagination.size = size
      this.fetchAddresses()
    },
    handleCurrentChange(current) {
      this.pagination.current = current
      this.fetchAddresses()
    }
  }
}
</script>

<style scoped>
.address-management {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
  color: #303133;
}

.filter-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.search-form {
  width: 100%;
}

.list-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.address-detail {
  max-height: 600px;
  overflow-y: auto;
}

/* 文本省略样式 */
.ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

/* 表格样式 */
.el-table {
  border-radius: 8px 8px 0 0;
  overflow: hidden;
  border: 1px solid #c0c4cc;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.el-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #303133;
  padding: 14px 0;
  border-bottom: 2px solid #409EFF;
  border-right: 1px solid #c0c4cc;
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
  .address-management {
    padding: 10px;
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