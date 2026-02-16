<template>
  <div class="address-management">
    <el-card shadow="never">
      <div slot="header" class="card-header">
        <span>用户地址管理</span>
      </div>

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

      <el-table v-loading="loading" :data="addresses" style="width: 100%">
        <el-table-column prop="id" label="地址ID" width="80" />
        <el-table-column prop="user_id" label="用户ID" width="100" />
        <el-table-column prop="recipient" label="收货人" width="100" />
        <el-table-column prop="phone" label="联系电话" width="120" />
        <el-table-column prop="province" label="省份" width="100" />
        <el-table-column prop="city" label="城市" width="100" />
        <el-table-column prop="district" label="区县" width="100" />
        <el-table-column prop="detail_address" label="详细地址" />
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
            <el-button type="primary" size="small" @click="handleView(scope.row)">
              <i class="el-icon-view"></i> 查看
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row.id)">
              <i class="el-icon-delete"></i> 删除
            </el-button>
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
    <el-dialog title="地址详情" v-model="detailVisible" width="600px">
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

.address-detail {
  max-height: 600px;
  overflow-y: auto;
}
</style>