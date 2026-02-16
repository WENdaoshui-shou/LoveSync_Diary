<template>
  <div class="game-management">
    <el-card shadow="hover">
      <template slot="header">
        <div class="card-header">
          <span>情侣游戏管理</span>
          <el-button type="primary" @click="handleAddGame" icon="el-icon-plus">添加游戏</el-button>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <div class="filter-section">
        <el-form :inline="true" :model="filterForm" class="filter-form">
          <el-form-item label="游戏名称">
            <el-input v-model="filterForm.name" placeholder="请输入游戏名称" clearable />
          </el-form-item>
          <el-form-item label="游戏类型">
            <el-select v-model="filterForm.type" placeholder="请选择游戏类型" clearable>
              <el-option label="任务" value="task" />
              <el-option label="挑战" value="challenge" />
              <el-option label="冒险" value="adventure" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="filterForm.status" placeholder="请选择状态" clearable>
              <el-option label="启用" value="active" />
              <el-option label="禁用" value="inactive" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="getGames">搜索</el-button>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 游戏列表 -->
      <el-table :data="gamesList" style="width: 100%" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="游戏名称" min-width="150" />
        <el-table-column prop="description" label="游戏描述" min-width="200">
          <template slot-scope="scope">
            <span>{{ scope.row.description }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="游戏类型" width="120">
          <template slot-scope="scope">
            <el-tag :type="getTypeTagType(scope.row.type)">{{ getTypeText(scope.row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="difficulty" label="难度" width="100">
          <template slot-scope="scope">
            <el-tag size="small">{{ getDifficultyText(scope.row.difficulty) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="预计时长" width="120">
          <template slot-scope="scope">
            <span>{{ scope.row.duration }}分钟</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'">
              {{ scope.row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template slot-scope="scope">
            <el-button type="primary" size="small" @click="handleEditGame(scope.row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDeleteGame(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-section">
        <el-pagination @size-change="handleSizeChange" @current-change="handleCurrentChange"
          :current-page="pagination.currentPage" :page-sizes="[10, 20, 50, 100]" :page-size="pagination.pageSize"
          layout="total, sizes, prev, pager, next, jumper" :total="pagination.total" />
      </div>
    </el-card>

    <!-- 添加/编辑游戏弹窗 -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="500px" :close-on-click-modal="false">
      <el-form :model="gameForm" :rules="rules" ref="gameForm" label-width="120px">
        <el-form-item label="游戏名称" prop="name">
          <el-input v-model="gameForm.name" placeholder="请输入游戏名称" />
        </el-form-item>
        <el-form-item label="游戏描述" prop="description">
          <el-input type="textarea" v-model="gameForm.description" placeholder="请输入游戏描述" rows="3" />
        </el-form-item>
        <el-form-item label="游戏类型" prop="type">
          <el-select v-model="gameForm.type" placeholder="请选择游戏类型">
            <el-option label="任务" value="task" />
            <el-option label="挑战" value="challenge" />
            <el-option label="冒险" value="adventure" />
          </el-select>
        </el-form-item>
        <el-form-item label="难度" prop="difficulty">
          <el-select v-model="gameForm.difficulty" placeholder="请选择难度">
            <el-option label="简单" value="easy" />
            <el-option label="中等" value="medium" />
            <el-option label="困难" value="hard" />
          </el-select>
        </el-form-item>
        <el-form-item label="预计时长" prop="duration">
          <el-input-number v-model="gameForm.duration" :min="1" :max="300" label="分钟" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch v-model="gameForm.status" active-value="active" inactive-value="inactive" />
        </el-form-item>
        <el-form-item label="游戏规则">
          <el-input type="textarea" v-model="gameForm.rules" placeholder="请输入游戏规则" rows="4" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {
  getCoupleGames,
  createCoupleGame,
  updateCoupleGame,
  deleteCoupleGame
} from '@/api/couple'

export default {
  name: 'GameManagement',
  data() {
    return {
      // 游戏列表
      gamesList: [],
      // 搜索筛选
      filterForm: {
        name: '',
        type: '',
        status: ''
      },
      // 分页信息
      pagination: {
        currentPage: 1,
        pageSize: 10,
        total: 0
      },
      // 弹窗状态
      dialogVisible: false,
      dialogTitle: '添加游戏',
      // 游戏表单
      gameForm: {
        id: '',
        name: '',
        description: '',
        type: '',
        difficulty: '',
        duration: 30,
        status: 'active',
        rules: ''
      },
      // 表单验证规则
      rules: {
        name: [
          { required: true, message: '请输入游戏名称', trigger: 'blur' },
          { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
        ],
        description: [
          { required: true, message: '请输入游戏描述', trigger: 'blur' }
        ],
        type: [
          { required: true, message: '请选择游戏类型', trigger: 'change' }
        ],
        difficulty: [
          { required: true, message: '请选择难度', trigger: 'change' }
        ],
        duration: [
          { required: true, message: '请输入预计时长', trigger: 'blur' }
        ]
      }
    }
  },
  mounted() {
    this.getGames()
  },
  methods: {
    // 获取游戏列表
    async getGames() {
      try {
        const params = {
          search: this.filterForm.name,
          type: this.filterForm.type,
          status: this.filterForm.status
        }
        const response = await getCoupleGames(params)
        this.gamesList = response.data
        this.pagination.total = this.gamesList.length
      } catch (error) {
        this.$message.error('加载失败')
      }
    },

    // 重置筛选
    resetFilter() {
      this.filterForm = {
        name: '',
        type: '',
        status: ''
      }
      this.getGames()
    },

    // 分页处理
    handleSizeChange(size) {
      this.pagination.pageSize = size
      this.getGames()
    },
    handleCurrentChange(current) {
      this.pagination.currentPage = current
      this.getGames()
    },

    // 添加游戏
    handleAddGame() {
      this.dialogTitle = '添加游戏'
      this.gameForm = {
        id: '',
        name: '',
        description: '',
        type: '',
        difficulty: '',
        duration: 30,
        status: 'active',
        rules: ''
      }
      this.dialogVisible = true
    },

    // 编辑游戏
    handleEditGame(game) {
      this.dialogTitle = '编辑游戏'
      this.gameForm = { ...game }
      this.dialogVisible = true
    },

    // 删除游戏
    async handleDeleteGame(id) {
      this.$confirm('确定要删除这个游戏吗？', '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await deleteCoupleGame(id)
          this.$message.success('删除成功')
          this.getGames()
        } catch (error) {
          this.$message.error('删除失败')
        }
      }).catch(() => {
        // 用户取消
      })
    },

    // 提交表单
    async submitForm() {
      this.$refs.gameForm.validate(async (valid) => {
        if (valid) {
          try {
            if (this.gameForm.id) {
              await updateCoupleGame(this.gameForm.id, this.gameForm)
            } else {
              await createCoupleGame(this.gameForm)
            }
            this.$message.success(this.gameForm.id ? '更新成功' : '添加成功')
            this.dialogVisible = false
            this.getGames()
          } catch (error) {
            this.$message.error('保存失败')
          }
        } else {
          return false
        }
      })
    },

    // 获取类型标签类型
    getTypeTagType(type) {
      const typeMap = {
        task: 'info',
        challenge: 'warning',
        adventure: 'success'
      }
      return typeMap[type] || 'default'
    },

    // 获取类型文本
    getTypeText(type) {
      const typeMap = {
        task: '任务',
        challenge: '挑战',
        adventure: '冒险'
      }
      return typeMap[type] || type
    },

    // 获取难度文本
    getDifficultyText(difficulty) {
      const diffMap = {
        easy: '简单',
        medium: '中等',
        hard: '困难'
      }
      return diffMap[difficulty] || difficulty
    }
  }
}
</script>

<style scoped>
.game-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-section {
  margin-bottom: 20px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.pagination-section {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.el-table {
  margin-top: 20px;
}

.dialog-footer {
  text-align: right;
}
</style>