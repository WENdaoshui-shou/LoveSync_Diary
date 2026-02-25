<template>
  <div class="order-management">

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="订单号">
          <el-input v-model="searchForm.order_number" placeholder="请输入订单号" clearable />
        </el-form-item>
        <el-form-item label="用户ID">
          <el-input v-model="searchForm.user_id" placeholder="请输入用户ID" clearable />
        </el-form-item>
        <el-form-item label="订单状态">
          <el-select v-model="searchForm.status" placeholder="请选择订单状态" clearable>
            <el-option label="待付款" value="pending" />
            <el-option label="已付款" value="paid" />
            <el-option label="待发货" value="shipping" />
            <el-option label="待收货" value="delivering" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
            <el-option label="退款中" value="refunding" />
            <el-option label="已退款" value="refunded" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchOrders">
            <i class="el-icon-search"></i> 搜索
          </el-button>
          <el-button @click="resetForm">
            <i class="el-icon-refresh"></i> 重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 订单列表 -->
    <el-card class="list-card">
      <el-table v-loading="loading" :data="orders" style="width: 100%">
        <el-table-column prop="order_number" label="订单号" />
        <el-table-column prop="user_id" label="用户ID" width="100" />
        <el-table-column label="订单金额" width="120">
          <template slot-scope="scope">
            ¥{{ scope.row.total_amount.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column label="订单状态" width="120">
          <template slot-scope="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="220" fixed="right">
          <template slot-scope="scope">
            <div class="operation-buttons">
              <el-button type="primary" size="small" @click="handleView(scope.row)">
                <i class="el-icon-view"></i> 查看
              </el-button>
              <el-button type="success" size="small" @click="handleUpdateStatus(scope.row)"
                v-if="!['completed', 'cancelled', 'refunded'].includes(scope.row.status)">
                <i class="el-icon-edit"></i> 更新状态
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

    <!-- 订单详情对话框 -->
    <el-dialog title="订单详情" :visible.sync="detailVisible" width="800px" :modal="false">
      <div v-if="currentOrder" class="order-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="订单号">{{ currentOrder.order_number }}</el-descriptions-item>
          <el-descriptions-item label="用户ID">{{ currentOrder.user_id }}</el-descriptions-item>
          <el-descriptions-item label="订单金额">¥{{ currentOrder.total_amount.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="运费">¥{{ currentOrder.shipping_fee.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="订单状态">{{ getStatusText(currentOrder.status) }}</el-descriptions-item>
          <el-descriptions-item label="支付方式">{{ currentOrder.payment_method || '未支付' }}</el-descriptions-item>
          <el-descriptions-item label="支付时间">{{ currentOrder.paid_at || '未支付' }}</el-descriptions-item>
          <el-descriptions-item label="物流公司">{{ currentOrder.logistics_company || '未发货' }}</el-descriptions-item>
          <el-descriptions-item label="物流单号">{{ currentOrder.logistics_no || '未发货' }}</el-descriptions-item>
          <el-descriptions-item label="备注">{{ currentOrder.remark || '无' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentOrder.created_at }}</el-descriptions-item>
          <el-descriptions-item label="发货时间">{{ currentOrder.shipped_at || '未发货' }}</el-descriptions-item>
          <el-descriptions-item label="收货时间" :span="2">{{ currentOrder.delivered_at || '未收货' }}</el-descriptions-item>
        </el-descriptions>

        <h4 style="margin-top: 20px; margin-bottom: 10px;">订单商品</h4>
        <el-table :data="currentOrder.order_items || []" style="width: 100%">
          <el-table-column prop="product_id" label="商品ID" width="100" />
          <el-table-column prop="product_name" label="商品名称" />
          <el-table-column prop="quantity" label="数量" width="80" />
          <el-table-column label="单价" width="100">
            <template slot-scope="scope">
              ¥{{ scope.row.price.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column label="小计" width="120">
            <template slot-scope="scope">
              ¥{{ (scope.row.price * scope.row.quantity).toFixed(2) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 更新状态对话框 -->
    <el-dialog title="更新订单状态" :visible.sync="statusDialogVisible" width="400px" :modal="false">
      <el-form :model="statusForm" label-width="100px">
        <el-form-item label="当前状态">
          <el-input :value="getStatusText(statusForm.currentStatus)" disabled />
        </el-form-item>
        <el-form-item label="新状态" required>
          <el-select v-model="statusForm.newStatus" placeholder="请选择新状态">
            <el-option label="待付款" value="pending" />
            <el-option label="已付款" value="paid" />
            <el-option label="待发货" value="shipping" />
            <el-option label="待收货" value="delivering" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
            <el-option label="退款中" value="refunding" />
            <el-option label="已退款" value="refunded" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="statusDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitStatusUpdate">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { getOrders, getOrder, updateOrderStatus } from '@/api/mall'

export default {
  name: 'OrderList',
  data() {
    return {
      loading: false,
      orders: [],
      searchForm: {
        order_number: '',
        user_id: '',
        status: ''
      },
      pagination: {
        current: 1,
        size: 10,
        total: 0
      },
      detailVisible: false,
      currentOrder: null,
      statusDialogVisible: false,
      statusForm: {
        orderId: '',
        currentStatus: '',
        newStatus: ''
      }
    }
  },
  mounted() {
    this.fetchOrders()
  },
  methods: {
    fetchOrders() {
      this.loading = true
      const params = {
        page: this.pagination.current,
        page_size: this.pagination.size,
        order_number: this.searchForm.order_number,
        user_id: this.searchForm.user_id,
        status: this.searchForm.status
      }
      getOrders(params)
        .then(response => {
          // 后端返回 { results: [...], count: number } 格式
          this.orders = response.data.results
          this.pagination.total = response.data.count
        })
        .catch(error => {
          this.$message.error('获取订单列表失败: ' + error.message)
        })
        .finally(() => {
          this.loading = false
        })
    },
    handleView(order) {
      console.log('handleView called with order:', order)
      this.loading = true
      // 使用order_number作为参数从后端获取完整的订单详情
      getOrder(order.order_number)
        .then(response => {
          console.log('getOrder response:', response)
          this.currentOrder = response.data
          // 为订单项添加order_items属性，以便在模板中使用
          if (response.data.items) {
            this.currentOrder.order_items = response.data.items
          }
          console.log('Setting detailVisible to true')
          this.detailVisible = true
        })
        .catch(error => {
          console.error('Error in getOrder:', error)
          this.$message.error('获取订单详情失败: ' + error.message)
        })
        .finally(() => {
          this.loading = false
        })
    },
    handleUpdateStatus(order) {
      console.log('handleUpdateStatus called with order:', order)
      this.statusForm = {
        orderId: order.order_number, // 使用order_number作为唯一标识符
        currentStatus: order.status,
        newStatus: ''
      }
      console.log('Setting statusDialogVisible to true')
      this.statusDialogVisible = true
    },
    submitStatusUpdate() {
      if (!this.statusForm.newStatus) {
        this.$message.error('请选择新状态')
        return
      }

      updateOrderStatus(this.statusForm.orderId, { status: this.statusForm.newStatus })
        .then(() => {
          this.$message.success('订单状态更新成功')
          this.statusDialogVisible = false
          this.fetchOrders()
        })
        .catch(error => {
          this.$message.error('订单状态更新失败: ' + error.message)
        })
    },
    resetForm() {
      this.searchForm = {
        order_number: '',
        user_id: '',
        status: ''
      }
      this.fetchOrders()
    },
    handleSizeChange(size) {
      this.pagination.size = size
      this.fetchOrders()
    },
    handleCurrentChange(current) {
      this.pagination.current = current
      this.fetchOrders()
    },
    // 获取订单状态的标签类型
    getStatusType(status) {
      switch (status) {
        case 'pending':
        case 'refunding':
          return 'warning'
        case 'paid':
        case 'shipping':
        case 'delivering':
          return 'info'
        case 'completed':
          return 'success'
        case 'cancelled':
        case 'refunded':
          return 'danger'
        default:
          return 'default'
      }
    },
    // 获取订单状态的中文文本
    getStatusText(status) {
      const statusMap = {
        'pending': '待付款',
        'paid': '已付款',
        'shipping': '待发货',
        'delivering': '待收货',
        'completed': '已完成',
        'cancelled': '已取消',
        'refunding': '退款中',
        'refunded': '已退款'
      }
      return statusMap[status] || status
    }
  }
}
</script>

<style scoped>
.order-management {
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

/* 操作按钮容器 */
.operation-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
}

/* 按钮样式优化 */
.el-button--small {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 4px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.order-detail {
  max-height: 600px;
  overflow-y: auto;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
}
</style>