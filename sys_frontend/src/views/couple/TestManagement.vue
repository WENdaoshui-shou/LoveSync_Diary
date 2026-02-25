<template>
  <div class="test-management">

    <!-- 统计面板 -->
    <div class="stats-container">
      <el-row :gutter="12">
        <el-col :span="4" v-for="(count, category) in categoryStats" :key="category">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon">
                <i class="el-icon-document"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ count }}</div>
                <div class="stat-label">{{ category }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="搜索">
          <el-input v-model="filterForm.search" placeholder="搜索测试标题" clearable @clear="handleSearch"
            @keyup.enter="handleSearch" style="width: 200px"></el-input>
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="filterForm.category" placeholder="选择分类" clearable>
            <el-option label="全部" value=""></el-option>
            <el-option label="沟通交流" value="1"></el-option>
            <el-option label="亲密关系" value="2"></el-option>
            <el-option label="信任关系" value="3"></el-option>
            <el-option label="未来规划" value="4"></el-option>
            <el-option label="冲突解决" value="5"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetFilter">重置</el-button>
          <el-button type="primary" @click="addTest">
            <i class="el-icon-plus"></i> 添加测试
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="list-card">

      <el-table :data="tests" v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
        <el-table-column prop="question" label="测试问题" min-width="200"></el-table-column>
        <el-table-column label="分类" width="100" align="center">
          <template slot-scope="scope">
            {{ getCategoryName(scope.row.category_id) }}
          </template>
        </el-table-column>

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
        <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange" :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]" :page-size="pageSize" layout="total, sizes, prev, pager, next, jumper"
          :total="total"></el-pagination>
      </div>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="600px" :modal="false">
      <el-form :model="form" label-width="100px">
        <el-form-item label="测试问题" required>
          <el-input type="textarea" v-model="form.question" placeholder="请输入测试问题" rows="3"></el-input>
        </el-form-item>
        <el-form-item label="正确答案" required>
          <el-input v-model="form.correct_answer" placeholder="请输入正确答案"></el-input>
        </el-form-item>
        <el-form-item label="选项列表" required>
          <div v-for="(value, key) in form.optionsObj" :key="key" class="option-item">
            <el-input :value="key" @input="updateOptionKey(key, $event)" placeholder="选项标识（如A、B、C）"
              style="width: 80px; margin-right: 10px"></el-input>
            <el-input :value="value" @input="updateOptionValue(key, $event)" placeholder="选项内容"
              style="flex: 1"></el-input>
            <el-button type="danger" size="small" @click="removeOption(key)" style="margin-left: 10px">删除</el-button>
          </div>
          <el-button type="primary" size="small" @click="addOption" style="margin-top: 10px">添加选项</el-button>
        </el-form-item>

        <el-form-item label="分类" required>
          <el-select v-model="form.category_id" placeholder="选择分类">
            <el-option label="沟通交流" value="1"></el-option>
            <el-option label="亲密关系" value="2"></el-option>
            <el-option label="信任关系" value="3"></el-option>
            <el-option label="未来规划" value="4"></el-option>
            <el-option label="冲突解决" value="5"></el-option>
          </el-select>
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
        optionsObj: {},
        category_id: ''
      },
      fileList: [],
      categoryStats: {}
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

        // 计算分类统计数据
        this.calculateCategoryStats()
      } catch (error) {
        this.$message.error('加载失败')
      } finally {
        this.loading = false
      }
    },
    calculateCategoryStats() {
      // 初始化分类统计对象
      const stats = {
        '沟通交流': 0,
        '亲密关系': 0,
        '信任关系': 0,
        '未来规划': 0,
        '冲突解决': 0
      }

      // 遍历测试数据，统计每个分类的数量
      this.tests.forEach(test => {
        const categoryName = this.getCategoryName(test.category_id)
        if (Object.prototype.hasOwnProperty.call(stats, categoryName)) {
          stats[categoryName]++
        }
      })

      this.categoryStats = stats
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
        optionsObj: { 'A': '', 'B': '', 'C': '', 'D': '' },
        category_id: ''
      }
      this.fileList = []
      this.dialogVisible = true
    },
    editTest(test) {
      this.dialogTitle = '编辑测试'
      // 处理options格式
      let optionsObj = {}
      if (typeof test.options === 'string') {
        // 尝试解析JSON字符串
        try {
          optionsObj = JSON.parse(test.options)
        } catch (e) {
          // 如果不是JSON，则按逗号分隔处理
          const optionsArray = test.options.split(',').map(opt => opt.trim())
          optionsArray.forEach((opt, index) => {
            const key = String.fromCharCode(65 + index) // A, B, C, D...
            optionsObj[key] = opt
          })
        }
      } else if (Array.isArray(test.options)) {
        // 如果是数组，转换为对象
        test.options.forEach((opt, index) => {
          const key = String.fromCharCode(65 + index) // A, B, C, D...
          optionsObj[key] = opt
        })
      } else if (typeof test.options === 'object' && test.options !== null) {
        // 如果已经是对象，直接使用
        optionsObj = test.options
      }

      this.form = {
        ...test,
        options: '',
        optionsObj: optionsObj,
        category_id: test.category_id ? test.category_id.toString() : ''
      }
      this.fileList = []
      this.dialogVisible = true
    },
    addOption() {
      // 生成下一个选项键（A, B, C, D...）
      const keys = Object.keys(this.form.optionsObj)
      const lastKey = keys.length > 0 ? keys[keys.length - 1] : 'Z'
      const nextKey = String.fromCharCode(lastKey.charCodeAt(0) + 1)
      this.$set(this.form.optionsObj, nextKey, '')
    },
    removeOption(key) {
      this.$delete(this.form.optionsObj, key)
    },
    updateOptionKey(oldKey, newKey) {
      if (oldKey !== newKey && newKey) {
        const value = this.form.optionsObj[oldKey]
        this.$delete(this.form.optionsObj, oldKey)
        this.$set(this.form.optionsObj, newKey, value)
      }
    },
    updateOptionValue(key, value) {
      this.$set(this.form.optionsObj, key, value)
    },
    viewTest(test) {
      // 查看详情
      console.log('查看测试详情:', test)
      this.$message.info('查看详情功能开发中')
    },
    async saveTest() {
      try {
        // 转换optionsObj为JSON字符串格式
        const formData = {
          ...this.form,
          options: JSON.stringify(this.form.optionsObj)
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
      }).catch(() => { })
    },
    handlePreview(file) {
      console.log('预览文件:', file)
    },
    handleRemove(file, fileList) {
      console.log('删除文件:', file, fileList)
    },
    getCategoryName(categoryId) {
      const categories = {
        '1': '沟通交流',
        '2': '亲密关系',
        '3': '信任关系',
        '4': '未来规划',
        '5': '冲突解决'
      }
      return categories[categoryId] || '未知分类'
    }
  }
}
</script>

<style scoped>
.test-management {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

/* 统计卡片 */
.stats-container {
  margin-bottom: 20px;
}

.stat-card {
  text-align: left;
  border-radius: 6px;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
}

.stat-card:hover {
  box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.06);
  transform: translateY(-1px);
  border-color: #e6f7ff;
}

.stat-content {
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-content .stat-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: rgba(64, 158, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #409EFF;
  flex-shrink: 0;
}

.stat-content .stat-info {
  flex: 1;
  min-width: 0;
}

.stat-content .stat-info .stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 2px;
  line-height: 1;
}

.stat-content .stat-info .stat-label {
  font-size: 12px;
  color: #909399;
  line-height: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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

.option-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.option-item .el-input {
  margin-right: 10px;
}
</style>