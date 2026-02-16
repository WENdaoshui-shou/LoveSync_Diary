<template>
  <div class="place-management">
    <div class="page-header">
      <h1>地点管理</h1>
      <el-button type="primary" @click="addPlace">
        <i class="el-icon-plus"></i> 添加地点
      </el-button>
    </div>

    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="搜索">
          <el-input v-model="filterForm.search" placeholder="搜索地点名称" clearable @clear="handleSearch" @keyup.enter="handleSearch" style="width: 200px"></el-input>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="filterForm.type" placeholder="选择类型" clearable>
            <el-option label="全部" value=""></el-option>
            <el-option label="浪漫约会" value="romantic"></el-option>
            <el-option label="户外探险" value="outdoor"></el-option>
            <el-option label="文化体验" value="cultural"></el-option>
            <el-option label="美食餐厅" value="dining"></el-option>
            <el-option label="休闲娱乐" value="entertainment"></el-option>
            <el-option label="免费景点" value="free"></el-option>
            <el-option label="其他" value="other"></el-option>
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
        <span>地点列表</span>
      </div>

      <el-table :data="places" v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
        <el-table-column label="地点信息" min-width="300">
          <template slot-scope="scope">
            <div class="place-info">
              <div class="place-name">{{ scope.row.name }}</div>
              <div class="place-address">{{ scope.row.address }}</div>
              <div class="place-type">{{ getPlaceTypeText(scope.row.place_type) }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="评分" width="80" align="center">
          <template slot-scope="scope">
            <div class="rating">
              <el-rate v-model="scope.row.rating" disabled show-score :score-template="scope.row.rating"></el-rate>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="review_count" label="评价数" width="100" align="center"></el-table-column>
        <el-table-column prop="price_range" label="价格范围" width="120"></el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template slot-scope="scope">
            <el-button type="text" size="mini" @click="viewPlace(scope.row)">详情</el-button>
            <el-button type="text" size="mini" @click="editPlace(scope.row)">编辑</el-button>
            <el-button type="text" size="mini" @click="deletePlace(scope.row)" style="color: #F56C6C">删除</el-button>
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
        <el-form-item label="地点名称" required>
          <el-input v-model="form.name" placeholder="请输入地点名称"></el-input>
        </el-form-item>
        <el-form-item label="地址" required>
          <el-input v-model="form.address" placeholder="请输入地址"></el-input>
        </el-form-item>
        <el-form-item label="类型" required>
          <el-select v-model="form.place_type" placeholder="选择类型">
            <el-option label="浪漫约会" value="romantic"></el-option>
            <el-option label="户外探险" value="outdoor"></el-option>
            <el-option label="文化体验" value="cultural"></el-option>
            <el-option label="美食餐厅" value="dining"></el-option>
            <el-option label="休闲娱乐" value="entertainment"></el-option>
            <el-option label="免费景点" value="free"></el-option>
            <el-option label="其他" value="other"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input type="textarea" v-model="form.description" placeholder="请输入地点描述" :rows="3"></el-input>
        </el-form-item>
        <el-form-item label="坐标">
          <el-row :gutter="10">
            <el-col :span="12">
              <el-form-item label="纬度" required>
                <el-input v-model="form.latitude" type="number" placeholder="请输入纬度"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="经度" required>
                <el-input v-model="form.longitude" type="number" placeholder="请输入经度"></el-input>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form-item>
        <el-form-item label="评分">
          <el-rate v-model="form.rating" :max="5" :step="0.1"></el-rate>
        </el-form-item>
        <el-form-item label="评价数">
          <el-input-number v-model="form.review_count" :min="0" label="数量"></el-input-number>
        </el-form-item>
        <el-form-item label="价格范围">
          <el-input v-model="form.price_range" placeholder="请输入价格范围"></el-input>
        </el-form-item>
        <el-form-item label="图片">
          <el-upload class="upload-demo" action="#" :on-preview="handlePreview" :on-remove="handleRemove" :file-list="fileList" :auto-upload="false">
            <el-button size="small" type="primary">点击上传</el-button>
            <div slot="tip" class="el-upload__tip">只能上传jpg/png文件，且不超过500kb</div>
          </el-upload>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePlace">保存</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {
  getPlaces,
  createPlace,
  updatePlace,
  deletePlace
} from '@/api/couple'

export default {
  name: 'PlaceManagement',
  data() {
    return {
      loading: false,
      places: [],
      total: 0,
      currentPage: 1,
      pageSize: 10,
      filterForm: {
        search: '',
        type: ''
      },
      dialogVisible: false,
      dialogTitle: '',
      form: {
        id: '',
        name: '',
        address: '',
        place_type: 'romantic',
        description: '',
        latitude: '',
        longitude: '',
        rating: 0,
        review_count: 0,
        price_range: '',
        image: ''
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
          type: this.filterForm.type
        }
        const response = await getPlaces(params)
        this.places = response.data
        this.total = this.places.length
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
        type: ''
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
    addPlace() {
      this.dialogTitle = '添加地点'
      this.form = {
        id: '',
        name: '',
        address: '',
        place_type: 'romantic',
        description: '',
        latitude: '',
        longitude: '',
        rating: 0,
        review_count: 0,
        price_range: '',
        image: ''
      }
      this.fileList = []
      this.dialogVisible = true
    },
    editPlace(place) {
      this.dialogTitle = '编辑地点'
      this.form = { ...place }
      this.fileList = []
      this.dialogVisible = true
    },
    viewPlace(place) {
      // 查看详情
      this.$message.info('查看详情功能开发中')
    },
    async savePlace() {
      try {
        if (this.form.id) {
          await updatePlace(this.form.id, this.form)
        } else {
          await createPlace(this.form)
        }
        this.$message.success('保存成功')
        this.dialogVisible = false
        this.loadData()
      } catch (error) {
        this.$message.error('保存失败')
      }
    },
    async deletePlace(place) {
      this.$confirm('确定要删除这个地点吗？', '确认删除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await deletePlace(place.id)
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
    },
    getPlaceTypeText(type) {
      const types = {
        'romantic': '浪漫约会',
        'outdoor': '户外探险',
        'cultural': '文化体验',
        'dining': '美食餐厅',
        'entertainment': '休闲娱乐',
        'free': '免费景点',
        'other': '其他'
      }
      return types[type] || type
    }
  }
}
</script>

<style scoped>
.place-management {
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

.place-info {
  line-height: 1.5;
}

.place-name {
  font-weight: bold;
  color: #303133;
}

.place-address {
  font-size: 12px;
  color: #606266;
}

.place-type {
  font-size: 12px;
  color: #909399;
}

.rating {
  display: flex;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style>