<template>
  <div class="flash-sale-management">
    <el-card shadow="never">
      <div slot="header" class="card-header">
        <span>闪购管理</span>
        <el-button type="primary" size="small" @click="handleAdd">
          <i class="el-icon-plus"></i> 添加闪购活动
        </el-button>
      </div>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="活动名称">
          <el-input v-model="searchForm.name" placeholder="请输入活动名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchFlashSales">
            <i class="el-icon-search"></i> 搜索
          </el-button>
          <el-button @click="resetForm">
            <i class="el-icon-refresh"></i> 重置
          </el-button>
        </el-form-item>
      </el-form>
      
      <el-table v-loading="loading" :data="flashSales" style="width: 100%">
        <el-table-column prop="id" label="活动ID" width="80" />
        <el-table-column prop="name" label="活动名称" />
        <el-table-column label="活动时间" width="300">
          <template slot-scope="scope">
            {{ scope.row.start_time }}<br/>
            至<br/>
            {{ scope.row.end_time }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'">
              {{ scope.row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="活动描述" />
        <el-table-column label="倒计时" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.need_countdown === 1 ? 'success' : 'info'">
              {{ scope.row.need_countdown === 1 ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="会员专享" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.is_vip_only === 1 ? 'success' : 'info'">
              {{ scope.row.is_vip_only === 1 ? '是' : '否' }}
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
        <el-form-item label="活动名称" required>
          <el-input v-model="form.name" placeholder="请输入活动名称" />
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
        <el-form-item label="活动描述">
          <el-input v-model="form.description" type="textarea" placeholder="请输入活动描述" rows="3" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.status" active-value="1" inactive-value="0" />
        </el-form-item>
        <el-form-item label="需要倒计时">
          <el-switch v-model="form.need_countdown" active-value="1" inactive-value="0" />
        </el-form-item>
        <el-form-item label="会员专享">
          <el-switch v-model="form.is_vip_only" active-value="1" inactive-value="0" />
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
import { getFlashSales, createFlashSale, updateFlashSale, deleteFlashSale } from '@/api/mall'

export default {
  name: 'FlashSaleList',
  data() {
    return {
      loading: false,
      flashSales: [],
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
        start_time: '',
        end_time: '',
        status: 1,
        description: '',
        need_countdown: 0,
        is_vip_only: 0
      }
    }
  },
  mounted() {
    this.fetchFlashSales()
  },
  methods: {
    fetchFlashSales() {
      this.loading = true
      const params = {
        page: this.pagination.current,
        page_size: this.pagination.size,
        search: this.searchForm.name
      }
      getFlashSales(params)
        .then(response => {
          // 后端直接返回数组格式，不是 { results: [...], count: number } 格式
          this.flashSales = response.data
          this.pagination.total = response.data.length
        })
        .catch(error => {
          this.$message.error('获取闪购活动列表失败: ' + error.message)
        })
        .finally(() => {
          this.loading = false
        })
    },
    handleAdd() {
      this.dialogTitle = '添加闪购活动'
      this.form = {
        id: '',
        name: '',
        start_time: '',
        end_time: '',
        status: 1,
        description: '',
        need_countdown: 0,
        is_vip_only: 0
      }
      this.dialogVisible = true
    },
    handleEdit(row) {
      this.dialogTitle = '编辑闪购活动'
      this.form = { ...row }
      this.dialogVisible = true
    },
    handleSubmit() {
      if (!this.form.name) {
        this.$message.error('请输入活动名称')
        return
      }
      if (!this.form.start_time || !this.form.end_time) {
        this.$message.error('请选择活动时间')
        return
      }
      if (new Date(this.form.start_time) >= new Date(this.form.end_time)) {
        this.$message.error('开始时间必须早于结束时间')
        return
      }
      
      const request = this.form.id ? updateFlashSale(this.form.id, this.form) : createFlashSale(this.form)
      request
        .then(response => {
          this.$message.success(this.form.id ? '更新闪购活动成功' : '添加闪购活动成功')
          this.dialogVisible = false
          this.fetchFlashSales()
        })
        .catch(error => {
          this.$message.error((this.form.id ? '更新闪购活动' : '添加闪购活动') + '失败: ' + error.message)
        })
    },
    handleDelete(id) {
      this.$confirm('确定要删除这个闪购活动吗？', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          deleteFlashSale(id)
            .then(response => {
              this.$message.success('删除闪购活动成功')
              this.fetchFlashSales()
            })
            .catch(error => {
              this.$message.error('删除闪购活动失败: ' + error.message)
            })
        })
        .catch(() => {})
    },
    resetForm() {
      this.searchForm = {
        name: ''
      }
      this.fetchFlashSales()
    },
    handleSizeChange(size) {
      this.pagination.size = size
      this.fetchFlashSales()
    },
    handleCurrentChange(current) {
      this.pagination.current = current
      this.fetchFlashSales()
    }
  }
}
</script>

<style scoped>
.flash-sale-management {
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