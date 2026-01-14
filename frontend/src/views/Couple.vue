<template>
  <div class="couple-container">
    <div class="couple-card">
      <div class="couple-header">
        <h2 class="couple-title">情侣关系管理</h2>
        <p class="couple-subtitle">管理您的情侣关系</p>
      </div>

      <div class="couple-content" v-if="!couple">
        <div class="no-couple">
          <el-icon class="no-couple-icon">
            <i class="el-icon-heart"></i>
          </el-icon>
          <h3>您还没有绑定伴侣</h3>
          <p>邀请您的伴侣加入 LoveSync，一起记录美好时光</p>
          <el-form ref="inviteForm" :model="inviteForm" :rules="rules" label-position="top" class="invite-form">
            <el-form-item label="邀请码" prop="coupleCode">
              <el-input v-model="inviteForm.coupleCode" placeholder="请输入伴侣的邀请码" prefix-icon="el-icon-key"
                clearable></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleInvite" :loading="loading">
                发送邀请
              </el-button>
            </el-form-item>
          </el-form>
        </div>
        <div class="your-code">
          <h3>您的邀请码</h3>
          <el-input v-model="myInviteCode" readonly prefix-icon="el-icon-document-copy" @click="copyCode"></el-input>
          <p>将此邀请码分享给您的伴侣</p>
        </div>
      </div>

      <div class="couple-content" v-else>
        <div class="couple-info">
          <h3>您的伴侣</h3>
          <div class="partner-info">
            <el-avatar :size="80" :src="couple.userAvatar">
              {{ couple.user.name.charAt(0) }}
            </el-avatar>
            <div class="partner-details">
              <p class="partner-name">{{ couple.user.name }}</p>
              <p class="partner-joined">
                绑定于 {{ formatTime(couple.couple_joined_at) }}
              </p>
            </div>
          </div>
          <el-button type="danger" @click="handleBreakup" :loading="loading">
            解除关系
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Couple',
  data() {
    return {
      couple: null,
      myInviteCode: '',
      inviteForm: {
        coupleCode: ''
      },
      rules: {
        coupleCode: [
          { required: true, message: '请输入邀请码', trigger: 'blur' },
          { min: 6, max: 6, message: '邀请码长度为 6 个字符', trigger: 'blur' }
        ]
      },
      loading: false
    }
  },
  created() {
    this.fetchCoupleInfo()
    this.fetchMyInviteCode()
  },
  methods: {
    async fetchCoupleInfo() {
      try {
        // 模拟API请求
        // const response = await this.$store.dispatch('fetchCoupleInfo')
        // this.couple = response.couple
      } catch (error) {
        console.error('获取情侣信息失败:', error)
      }
    },

    async fetchMyInviteCode() {
      try {
        // 模拟API请求
        // const response = await this.$store.dispatch('fetchMyInviteCode')
        // this.myInviteCode = response.coupleCode
        this.myInviteCode = '123456' // 模拟数据
      } catch (error) {
        console.error('获取邀请码失败:', error)
      }
    },

    async handleInvite() {
      this.$refs.inviteForm.validate(async (valid) => {
        if (valid) {
          this.loading = true
          try {
            // 模拟API请求
            // await this.$store.dispatch('sendCoupleRequest', this.inviteForm.coupleCode)
            this.$message.success('邀请发送成功')
            this.fetchCoupleInfo()
          } catch (error) {
            this.$message.error(error.message || '邀请发送失败')
          } finally {
            this.loading = false
          }
        }
      })
    },

    async handleBreakup() {
      this.$confirm('确定要解除情侣关系吗？', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        this.loading = true
        try {
          // 模拟API请求
          // await this.$store.dispatch('breakup')
          this.$message.success('情侣关系已解除')
          this.couple = null
        } catch (error) {
          this.$message.error(error.message || '解除关系失败')
        } finally {
          this.loading = false
        }
      }).catch(() => {
        this.$message.info('已取消解除关系')
      })
    },

    copyCode() {
      navigator.clipboard.writeText(this.myInviteCode)
        .then(() => {
          this.$message.success('邀请码已复制到剪贴板')
        })
        .catch(() => {
          this.$message.error('复制失败，请手动复制')
        })
    },

    formatTime(timeStr) {
      const date = new Date(timeStr)
      return date.toLocaleString()
    }
  }
}
</script>

<style scoped>
.couple-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.couple-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  padding: 30px;
  width: 100%;
  max-width: 600px;
}

.couple-header {
  text-align: center;
  margin-bottom: 30px;
}

.couple-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.couple-subtitle {
  font-size: 14px;
  color: #666;
}

.couple-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.no-couple {
  text-align: center;
  padding: 30px 0;
}

.no-couple-icon {
  font-size: 64px;
  color: #667eea;
  margin-bottom: 20px;
}

.no-couple h3 {
  font-size: 20px;
  color: #333;
  margin-bottom: 10px;
}

.no-couple p {
  color: #666;
  margin-bottom: 30px;
}

.invite-form {
  max-width: 400px;
  margin: 0 auto;
}

.your-code {
  background: #f0f5ff;
  border: 1px solid #d6e4ff;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.your-code h3 {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
}

.your-code .el-input {
  max-width: 300px;
  margin: 0 auto 10px;
}

.your-code p {
  color: #666;
  font-size: 14px;
}

.couple-info {
  text-align: center;
}

.couple-info h3 {
  font-size: 20px;
  color: #333;
  margin-bottom: 20px;
}

.partner-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 30px;
}

.partner-details {
  margin-top: 15px;
}

.partner-name {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.partner-joined {
  color: #666;
  font-size: 14px;
}
</style>
