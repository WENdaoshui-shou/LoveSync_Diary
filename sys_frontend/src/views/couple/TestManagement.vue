<template>
  <div class="test-management">
    <div class="page-header">
      <h1>爱情测试管理</h1>
      <el-button type="primary" @click="addTest">
        <i class="el-icon-plus"></i> 添加测试
      </el-button>
    </div>

    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="搜索">
          <el-input v-model="filterForm.search" placeholder="搜索测试标题" clearable @clear="handleSearch" @keyup.enter="handleSearch" style="width: 200px"></el-input>
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="filterForm.category" placeholder="选择分类" clearable>
            <el-option label="全部" value=""></el-option>
            <el-option label="情侣默契" value="默契测试"></el-option>
            <el-option label="爱情观" value="爱情观测试"></el-option>
            <el-option label="性格匹配" value="性格测试"></el-option>
            <el-option label="其他" value="其他测试"></el-option>
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
        <span>测试列表</span>
      </div>

      <el-table :data="tests" v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
        <el-table-column prop="question" label="测试问题" min-width="200"></el-table-column>
        <el-table-column prop="user_name" label="创建用户" width="120"></el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="150" align="center"></el-table-column>
        <el-table-column label="操作" width="150" align="center">
          <template slot-scope="scope">
            <el-button type="text" size="mini" @click="viewTest(scope.row)">详情</el-button>
            <el-button type="text" size="mini" @click="editTest(scope.row)">编辑</el-button>
            <el-button type="text" size="mini" @click="deleteTest(scope.row)" style="color: #F56C6C">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange" :current-page="currentPage" :page-sizes="[10, 20, 50, 100]" :page-size="pageSize" layout="total, sizes, prev, pager, next, jumper" :total="total"></el-pagination>
      </div>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="测试问题" required>
          <el-input type="textarea" v-model="form.question" placeholder="请输入测试问题" rows="3"></el-input>
        </el-form-item>
        <el-form-item label="正确答案" required>
          <el-input v-model="form.correct_answer" placeholder="请输入正确答案"></el-input>
        </el-form-item>
        <el-form-item label="选项列表" required>
          <el-input type="textarea" v-model="form.options" placeholder="请输入选项列表，以逗号分隔" rows="3"></el-input>
        </el-form-item>
        <el-form-item label="用户ID" required>
          <el-input v-model="form.user_id" type="number" placeholder="请输入用户ID"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTest">保存</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {
  getLoveTests,
  createLoveTest,
  updateLoveTest,
  deleteLoveTest
} from '@/api/couple'

export default {
  name: 'TestManagement',
  data() {
    return {
      loading: false,
      tests: [],
      total: 0,
      currentPage: 1,
      pageSize: 10,
      filterForm: {
        search: '',
        category: ''
      },
      dialogVisible: false,
      dialogTitle: '',
      form: {
        id: '',
        question: '',
        correct_answer: '',
        options: '',
        user_id: ''
      },
      fileList: []
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
          category: this.filterForm.category
        }
        const response = await getLoveTests(params)
        this.tests = response.data
        this.total = this.tests.length
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
        category: ''
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
    addTest() {
      this.dialogTitle = '添加测试'
      this.form = {
        id: '',
        question: '',
        correct_answer: '',
        options: '',
        user_id: ''
      }
      this.fileList = []
      this.dialogVisible = true
    },
    editTest(test) {
      this.dialogTitle = '编辑测试'
      // 将数组形式的options转换为逗号分隔的字符串
      const optionsStr = Array.isArray(test.options) ? test.options.join(',') : test.options
      this.form = {
        ...test,
        options: optionsStr
      }
      this.fileList = []
      this.dialogVisible = true
    },
    viewTest(test) {
      // 查看详情
      this.$message.info('查看详情功能开发中')
    },
    async saveTest() {
      try {
        // 转换options为数组格式
        const formData = {
          ...this.form,
          options: this.form.options.split(',').map(opt => opt.trim())
        }
        
        if (this.form.id) {
          await updateLoveTest(this.form.id, formData)
        } else {
          await createLoveTest(formData)
        }
        this.$message.success('保存成功')
        this.dialogVisible = false
        this.loadData()
      } catch (error) {
        this.$message.error('保存失败')
      }
    },
    async deleteTest(test) {
      this.$confirm('确定要删除这个测试吗？', '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await deleteLoveTest(test.id)
          this.$message.success('删除成功')
          this.loadData()
        } catch (error) {
          this.$message.error('删除失败')
        }
      }).catch(() => {})
    },
    handlePreview(file) {
      console.log('预览文件:', file)
    },
    handleRemove(file, fileList) {
      console.log('删除文件:', file, fileList)
    }
  }
}
</script>

<style scoped>
.test-management {
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

.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style>