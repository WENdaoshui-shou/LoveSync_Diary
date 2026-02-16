<template>
  <div class="recommended-couples">
    <div class="page-header">
      <h1>推荐情侣管理</h1>
      <el-button type="primary" @click="refreshData">
        <i class="el-icon-refresh"></i> 刷新数据
      </el-button>
    </div>

    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="搜索">
          <el-input v-model="filterForm.search" placeholder="搜索用户名" clearable @clear="handleSearch"
            @keyup.enter="handleSearch" style="width: 200px"></el-input>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="选择状态" clearable>
            <el-option label="全部" value=""></el-option>
            <el-option label="已绑定" value="coupled"></el-option>
            <el-option label="未绑定" value="single"></el-option>
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
        <span>绑定情侣关系的用户列表</span>
        <div class="header-info">
          <el-tag size="small">总计: {{ total }} 对情侣</el-tag>
        </div>
      </div>

      <el-table :data="couples" v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
        <el-table-column label="情侣信息" min-width="300">
          <template slot-scope="scope">
            <div class="couple-info">
              <div class="user-pair">
                <span class="user-name">{{ scope.row.user1_name }}</span>
                <span class="couple-symbol">💖</span>
                <span class="user-name">{{ scope.row.user2_name }}</span>
              </div>
              <div class="user-ids">
                <span>用户ID: {{ scope.row.user1_id }}</span>
                <span>和</span>
                <span>用户ID: {{ scope.row.user2_id }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="relationship_start_date" label="相恋日期" width="120" align="center"></el-table-column>
        <el-table-column prop="couple_name" label="情侣名" width="150"></el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template>
            <el-tag type="success" size="small">已绑定</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center">
          <template slot-scope="scope">
            <el-button type="text" size="mini" @click="viewCouple(scope.row)">查看详情</el-button>
            <el-button type="text" size="mini" @click="editCouple(scope.row)">编辑</el-button>
            <el-button type="text" size="mini" @click="deleteCouple(scope.row)" style="color: #F56C6C">解除关系</el-button>
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
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="600px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="用户1 ID" required>
          <el-input v-model="form.user1_id" type="number" placeholder="请输入用户1 ID"></el-input>
        </el-form-item>
        <el-form-item label="用户2 ID" required>
          <el-input v-model="form.user2_id" type="number" placeholder="请输入用户2 ID"></el-input>
        </el-form-item>
        <el-form-item label="情侣名">
          <el-input v-model="form.couple_name" placeholder="请输入情侣名"></el-input>
        </el-form-item>
        <el-form-item label="相恋日期">
          <el-date-picker v-model="form.relationship_start_date" type="date" placeholder="选择日期"
            style="width: 100%"></el-date-picker>
        </el-form-item>
        <el-form-item label="爱情誓言">
          <el-input type="textarea" v-model="form.love_vow" placeholder="请输入爱情誓言" :rows="3"></el-input>
        </el-form-item>
        <el-form-item label="爱情故事">
          <el-input type="textarea" v-model="form.love_story" placeholder="请输入爱情故事" :rows="3"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCouple">保存</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {
  getRecommendedCouples,
  createRecommendedCouple,
  updateRecommendedCouple,
  deleteRecommendedCouple
} from '@/api/couple'

export default {
  name: 'RecommendedCouples',
  data() {
    return {
      loading: false,
      couples: [],
      total: 0,
      currentPage: 1,
      pageSize: 10,
      filterForm: {
        search: '',
        status: ''
      },
      dialogVisible: false,
      dialogTitle: '',
      form: {
        id: '',
        user1_id: '',
        user2_id: '',
        user1_name: '',
        user2_name: '',
        couple_name: '',
        relationship_start_date: '',
        love_vow: '',
        love_story: ''
      }
    }
  },
  created() {
    this.loadData()
  },
  methods: {
    async loadData() {
      this.loading = true
      try {
        const params = {
          search: this.filterForm.search,
          status: this.filterForm.status
        }
        const response = await getRecommendedCouples(params)
        this.couples = response.data
        this.total = this.couples.length
      } catch (error) {
        this.$message.error('加载失败')
      } finally {
        this.loading = false
      }
    },
    handleSearch() {
      this.currentPage = 1
      this.loadData()
    },
    resetFilter() {
      this.filterForm = {
        search: '',
        status: ''
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
    refreshData() {
      this.loadData()
      this.$message.success('数据已刷新')
    },
    viewCouple(couple) {
      this.dialogTitle = '查看情侣详情'
      this.form = { ...couple }
      this.dialogVisible = true
    },
    editCouple(couple) {
      this.dialogTitle = '编辑情侣信息'
      this.form = { ...couple }
      this.dialogVisible = true
    },
    async saveCouple() {
      try {
        if (this.form.id) {
          await updateRecommendedCouple(this.form.id, this.form)
        } else {
          await createRecommendedCouple(this.form)
        }
        this.$message.success('保存成功')
        this.dialogVisible = false
        this.loadData()
      } catch (error) {
        this.$message.error('保存失败')
      }
    },
    async deleteCouple(couple) {
      this.$confirm('确定要解除这对情侣的关系吗？', '确认解除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await deleteRecommendedCouple(couple.id)
          this.$message.success('解除关系成功')
          this.loadData()
        } catch (error) {
          this.$message.error('解除关系失败')
        }
      }).catch(() => { })
    }
  }
}
</script>

<style scoped>
.recommended-couples {
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

.couple-info {
  line-height: 1.5;
}

.user-pair {
  font-weight: bold;
  color: #303133;
}

.couple-symbol {
  margin: 0 8px;
  font-size: 16px;
}

.user-ids {
  font-size: 12px;
  color: #909399;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style>