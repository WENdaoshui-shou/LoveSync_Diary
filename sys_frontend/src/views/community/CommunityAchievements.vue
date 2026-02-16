<template>
  <div class="achievement-management">
    <h1>成就系统管理</h1>
    <p>管理用户成就、徽章和奖励系统</p>

    <!-- 成就统计 -->
    <div class="stats-container">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ statistics.totalAchievements || 0 }}</div>
              <div class="stat-label">总成就数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number text-success">{{ statistics.userAchievements || 0 }}</div>
              <div class="stat-label">用户获得</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number text-warning">{{ statistics.completionRate || '0%' }}</div>
              <div class="stat-label">完成率</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number text-info">{{ statistics.activeUsers || 0 }}</div>
              <div class="stat-label">活跃用户数</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 成就列表 -->
    <el-card>
      <div slot="header" class="card-header">
        <span>成就列表</span>
        <el-button type="primary" size="small" @click="createAchievement">
          <i class="el-icon-plus"></i> 创建成就
        </el-button>
      </div>

      <div class="achievement-list">
        <div v-if="achievements.length === 0" class="empty-state">
          <i class="el-icon-trophy"></i>
          <p>暂无成就数据</p>
        </div>

        <div v-else class="achievement-grid">
          <div v-for="achievement in achievements" :key="achievement.id" class="achievement-card">
            <div class="achievement-icon">
              <i :class="achievement.icon || 'el-icon-trophy'"></i>
            </div>
            <div class="achievement-info">
              <h4>{{ achievement.name }}</h4>
              <p>{{ achievement.description }}</p>
              <div class="achievement-meta">
                <el-tag :type="getDifficultyType(achievement.difficulty)" size="mini">
                  {{ getDifficultyText(achievement.difficulty) }}
                </el-tag>
                <span class="achievement-points">{{ achievement.points }} 积分</span>
              </div>
            </div>
            <div class="achievement-actions">
              <el-button type="text" size="mini" @click="editAchievement(achievement)">编辑</el-button>
              <el-button type="text" size="mini" @click="viewAchievementUsers(achievement)">查看用户</el-button>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'CommunityAchievements',
  data() {
    return {
      stats: {
        totalAchievements: 25,
        userAchievements: 156,
        completionRate: '12%',
        activeUsers: 89
      },
      achievements: [
        {
          id: 1,
          name: '初次分享',
          description: '分享您的第一个动态',
          icon: 'el-icon-share',
          difficulty: 1,
          points: 10
        },
        {
          id: 2,
          name: '社交达人',
          description: '获得100个点赞',
          icon: 'el-icon-thumb',
          difficulty: 2,
          points: 50
        },
        {
          id: 3,
          name: '社区贡献者',
          description: '参与10次社区活动',
          icon: 'el-icon-star',
          difficulty: 3,
          points: 100
        }
      ]
    }
  },
  methods: {
    createAchievement() {
      this.$message.info('创建成就功能开发中...')
    },

    editAchievement(achievement) {
      this.$message.info(`编辑成就: ${achievement.name}`)
    },

    viewAchievementUsers(achievement) {
      this.$message.info(`查看获得成就的用户: ${achievement.name}`)
    },

    getDifficultyType(difficulty) {
      const types = {
        1: 'success',
        2: 'warning',
        3: 'danger'
      }
      return types[difficulty] || 'info'
    },

    getDifficultyText(difficulty) {
      const texts = {
        1: '简单',
        2: '中等',
        3: '困难'
      }
      return texts[difficulty] || '未知'
    }
  }
}
</script>

<style lang="scss" scoped>
.community-achievements {
  padding: 20px;

  h1 {
    color: #303133;
    margin-bottom: 10px;
  }

  p {
    color: #909399;
    margin-bottom: 30px;
  }
}

.stats-container {
  margin-bottom: 30px;
}

.stat-card {
  text-align: center;

  .stat-content {
    padding: 20px 0;

    .stat-number {
      font-size: 32px;
      font-weight: bold;
      color: #303133;
      margin-bottom: 10px;

      &.text-success {
        color: #67C23A;
      }

      &.text-warning {
        color: #E6A23C;
      }

      &.text-info {
        color: #409EFF;
      }
    }

    .stat-label {
      font-size: 14px;
      color: #909399;
    }
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;

  i {
    font-size: 64px;
    margin-bottom: 20px;
    display: block;
  }

  p {
    margin: 0;
    font-size: 16px;
  }
}

.achievement-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.achievement-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  }

  .achievement-icon {
    font-size: 48px;
    color: #409EFF;
    width: 60px;
    text-align: center;
  }

  .achievement-info {
    flex: 1;

    h4 {
      margin: 0 0 8px 0;
      color: #303133;
      font-size: 16px;
    }

    p {
      margin: 0 0 10px 0;
      color: #606266;
      font-size: 14px;
      line-height: 1.5;
    }

    .achievement-meta {
      display: flex;
      align-items: center;
      gap: 10px;

      .achievement-points {
        font-size: 12px;
        color: #909399;
        font-weight: bold;
      }
    }
  }

  .achievement-actions {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }
}
</style>