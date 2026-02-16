<template>
  <div class="coupon-management">
    <el-card shadow="never">
      <div slot="header" class="card-header">
        <span>优惠券管理</span>
        <el-button type="primary" size="small" @click="handleAdd">
          <i class="el-icon-plus"></i> 添加优惠券
        </el-button>
      </div>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="优惠券名称">
          <el-input v-model="searchForm.name" placeholder="请输入优惠券名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchCoupons">
            <i class="el-icon-search"></i> 搜索
          </el-button>
          <el-button @click="resetForm">
            <i class="el-icon-refresh"></i> 重置
          </el-button>
        </el-form-item>
      </el-form>
      
      <el-table v-loading="loading" :data="coupons" style="width: 100%">
        <el-table-column prop="id" label="优惠券ID" width="80" />
        <el-table-column prop="name" label="优惠券名称" />
        <el-table-column prop="type" label="优惠券类型" width="120" />
        <el-table-column label="优惠金额" width="120">
          <template slot-scope="scope">
            ¥{{ scope.row.value.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column label="最低消费" width="120">
          <template slot-scope="scope">
            ¥{{ scope.row.min_spend.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column label="有效期" width="300">
          <template slot-scope="scope">
            {{ scope.row.start_time }}<br/>
            至<br/>
            {{ scope.row.end_time }}
          </template>
        </el-table-column>
        <el-table-column prop="total_quantity" label="总数量" width="100" />
        <el-table-column prop="remaining_quantity" label="剩余数量" width="100" />
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
        <el-form-item label="优惠券名称" required>
          <el-input v-model="form.name" placeholder="请输入优惠券名称" />
        </el-form-item>
        <el-form-item label="优惠券类型" required>
          <el-select v-model="form.type" placeholder="请选择优惠券类型">
            <el-option label="满减券" value="满减券" />
            <el-option label="折扣券" value="折扣券" />
            <el-option label="现金券" value="现金券" />
          </el-select>
        </el-form-item>
        <el-form-item label="优惠金额" required>
          <el-input-number v-model="form.value" :min="0.01" :max="9999" :step="0.01" />
        </el-form-item>
        <el-form-item label="最低消费" required>
          <el-input-number v-model="form.min_spend" :min="0" :max="9999" />
        </el-form-item>
        <el-form-item label="总数量" required>
          <el-input-number v-model="form.total_quantity" :min="1" :max="9999" />
        </el-form-item>
        <el-form-item label="开始时间" required>
          <el-date-picker
            v-model="form.start_time"
            type="datetime"
            placeholder="选择开始时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束时间" required>
          <el-date-picker
            v-model="form.end_time"
            type="datetime"
            placeholder="选择结束时间"
            style="width: 100%"
          />
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
import { getCoupons, createCoupon, updateCoupon, deleteCoupon } from '@/api/mall'

export default {
  name: 'CouponList',
  data() {
    return {
      loading: false,
      coupons: [],
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
        type: '满减券',
        value: 0,
        min_spend: 0,
        start_time: '',
        end_time: '',
        total_quantity: 100,
        is_active: 1
      }
    }
  },
  mounted() {
    this.fetchCoupons()
  },
  methods: {
    fetchCoupons() {
      this.loading = true
      const params = {
        page: this.pagination.current,
        page_size: this.pagination.size,
        search: this.searchForm.name
      }
      getCoupons(params)
        .then(response => {
          // 后端直接返回数组格式，不是 { results: [...], count: number } 格式
          this.coupons = response.data
          this.pagination.total = response.data.length
        })
        .catch(error => {
          this.$message.error('获取优惠券列表失败: ' + error.message)
        })
        .finally(() => {
          this.loading = false
        })
    },
    handleAdd() {
      this.dialogTitle = '添加优惠券'
      this.form = {
        id: '',
        name: '',
        type: '满减券',
        value: 0,
        min_spend: 0,
        start_time: '',
        end_time: '',
        total_quantity: 100,
        is_active: 1
      }
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.dialogTitle = '编辑优惠券'
      this.form = { ...row }
      this.dialogVisible = true
    },
    handleSubmit() {
      if (!this.form.name) {
        this.$message.error('请输入优惠券名称')
        return
      }
      if (!this.form.type) {
        this.$message.error('请选择优惠券类型')
        return
      }
      if (this.form.value <= 0) {
        this.$message.error('优惠金额必须大于0')
        return
      }
      if (this.form.total_quantity <= 0) {
        this.$message.error('总数量必须大于0')
        return
      }
      if (!this.form.start_time || !this.form.end_time) {
        this.$message.error('请选择有效期')
        return
      }
      if (new Date(this.form.start_time) >= new Date(this.form.end_time)) {
        this.$message.error('开始时间必须早于结束时间')
        return
      }
      
      const request = this.form.id ? updateCoupon(this.form.id, this.form) : createCoupon(this.form)
      request
        .then(response => {
          this.$message.success(this.form.id ? '更新优惠券成功' : '添加优惠券成功')
          this.dialogVisible = false
          this.fetchCoupons()
        })
        .catch(error => {
          this.$message.error((this.form.id ? '更新优惠券' : '添加优惠券') + '失败: ' + error.message)
        })
    },
    handleDelete(id) {
      this.$confirm('确定要删除这个优惠券吗？', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          deleteCoupon(id)
            .then(response => {
              this.$message.success('删除优惠券成功')
              this.fetchCoupons()
            })
            .catch(error => {
              this.$message.error('删除优惠券失败: ' + error.message)
            })
        })
        .catch(() => {})
    },
    resetForm() {
      this.searchForm = {
        name: ''
      }
      this.fetchCoupons()
    },
    handleSizeChange(size) {
      this.pagination.size = size
      this.fetchCoupons()
    },
    handleCurrentChange(current) {
      this.pagination.current = current
      this.fetchCoupons()
    }
  }
}
</script>

<style scoped>
.coupon-management {
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