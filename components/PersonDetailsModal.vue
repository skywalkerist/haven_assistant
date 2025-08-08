<template>
  <view class="modal-overlay" v-if="visible" @click="closeModal">
    <view class="modal-content" @click.stop>
      <view class="modal-header">
        <text class="modal-title">{{ person.name }}的详细信息</text>
        <view class="close-btn" @click="closeModal">✕</view>
      </view>
      
      <view class="person-info">
        <view class="basic-info">
          <view class="info-row">
            <text class="label">年龄：</text>
            <text class="value">{{ person.age }}岁</text>
          </view>
          <view class="info-row">
            <text class="label">性别：</text>
            <text class="value">{{ person.gender }}</text>
          </view>
          <view class="info-row">
            <text class="label">状态：</text>
            <text class="value" :class="person.isAlive ? 'alive' : 'dead'">
              {{ person.isAlive ? '健在' : '已故' }}
            </text>
          </view>
          <view class="info-row">
            <text class="label">职业：</text>
            <text class="value">{{ person.occupation || '无' }}</text>
          </view>
          <view class="info-row">
            <text class="label">教育：</text>
            <text class="value">{{ person.education }}</text>
          </view>
          <view class="info-row" v-if="person.schoolLevel">
            <text class="label">学历档次：</text>
            <text class="value">{{ person.schoolLevel }}</text>
          </view>
          <view class="info-row" v-if="person.major">
            <text class="label">专业：</text>
            <text class="value">{{ person.major }}</text>
          </view>
          <view class="info-row" v-if="person.workYears > 0">
            <text class="label">工作年限：</text>
            <text class="value">{{ person.workYears }}年</text>
          </view>
          <view class="info-row" v-if="person.isRetired">
            <text class="label">状态：</text>
            <text class="value retired">已退休</text>
          </view>
          <view class="info-row" v-if="person.jobSeeking">
            <text class="label">状态：</text>
            <text class="value job-seeking">正在找工作</text>
          </view>
        </view>
        
        <!-- 三大属性 -->
        <view class="attributes">
          <text class="section-title">核心属性</text>
          <view class="attribute-item">
            <view class="attribute-header">
              <text class="attribute-name">健康</text>
              <text class="attribute-value">{{ person.health }}/100</text>
            </view>
            <view class="progress-bar">
              <view class="progress-fill health" :style="{ width: person.health + '%' }"></view>
            </view>
          </view>
          
          <view class="attribute-item">
            <view class="attribute-header">
              <text class="attribute-name">魅力</text>
              <text class="attribute-value">{{ person.charm }}/100</text>
            </view>
            <view class="progress-bar">
              <view class="progress-fill charm" :style="{ width: person.charm + '%' }"></view>
            </view>
          </view>
          
          <view class="attribute-item">
            <view class="attribute-header">
              <text class="attribute-name">智力</text>
              <text class="attribute-value">{{ person.intelligence }}/100</text>
            </view>
            <view class="progress-bar">
              <view class="progress-fill intelligence" :style="{ width: person.intelligence + '%' }"></view>
            </view>
          </view>
        </view>
        
        <!-- 经济信息 -->
        <view class="economic-info">
          <text class="section-title">经济状况</text>
          <view class="info-row">
            <text class="label">年收入：</text>
            <text class="value positive">{{ person.income ? person.income.toLocaleString() : '0' }}元</text>
          </view>
          <view class="info-row">
            <text class="label">年支出：</text>
            <text class="value negative">{{ calculateExpense() }}元</text>
          </view>
          <view class="info-row">
            <text class="label">年收支：</text>
            <text class="value" :class="person.economicContribution >= 0 ? 'positive' : 'negative'">
              {{ person.economicContribution >= 0 ? '+' : '' }}{{ person.economicContribution.toLocaleString() }}元
            </text>
          </view>
        </view>
        
        <!-- 操作按钮 -->
        <view class="actions" v-if="person.occupation && person.isAlive">
          <button class="quit-job-btn" @click="quitJob">辞职</button>
        </view>
        
        <!-- 家庭信息 -->
        <view class="family-info" v-if="person.partner || person.children.length > 0">
          <text class="section-title">家庭关系</text>
          <view class="info-row" v-if="person.partner">
            <text class="label">伴侣：</text>
            <text class="value">{{ person.partner.name }}</text>
          </view>
          <view class="info-row" v-if="person.children.length > 0">
            <text class="label">子女：</text>
            <text class="value">{{ person.children.length }}人</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'PersonDetailsModal',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    person: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['close'],
  methods: {
    closeModal() {
      this.$emit('close')
    },
    
    calculateExpense() {
      if (!this.person) return '0'
      
      // 计算基础支出（简化版本）
      let expense = 0
      if (this.person.age < 18) {
        expense = 15000 // 未成年人平均支出
      } else {
        expense = 28000 // 成年人平均支出
      }
      
      // 健康惩罚
      if (this.person.health < 70) {
        expense += Math.pow(70 - this.person.health, 2) * 10
      }
      
      // 子女抚养费已删除
      
      return Math.floor(expense).toLocaleString()
    },
    
    quitJob() {
      uni.showModal({
        title: '确认辞职',
        content: `确定要让${this.person.name}辞职吗？辞职后将失去收入并需要重新找工作。`,
        success: (res) => {
          if (res.confirm) {
            // 清空职业相关信息
            this.person.occupation = null
            this.person.income = 0
            this.person.workYears = 0
            this.person.jobSeeking = true
            this.person.lastPromotionYear = 0
            
            // 清理企业家特殊标记
            if (this.person.flags && this.person.flags.entrepreneurYears !== undefined) {
              delete this.person.flags.entrepreneurYears
            }
            
            uni.showToast({
              title: `${this.person.name}已辞职`,
              icon: 'success'
            })
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 16rpx;
  width: 90%;
  max-width: 600rpx;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #eee;
}

.modal-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
}

.close-btn {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  color: #666;
}

.person-info {
  padding: 30rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
}

.basic-info, .economic-info, .family-info {
  margin-bottom: 40rpx;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.label {
  font-size: 26rpx;
  color: #666;
}

.value {
  font-size: 26rpx;
  color: #333;
  font-weight: 500;
}

.value.alive {
  color: #4CAF50;
}

.value.dead {
  color: #F44336;
}

.value.positive {
  color: #4CAF50;
}

.value.negative {
  color: #F44336;
}

.value.retired {
  color: #9E9E9E;
}

.value.job-seeking {
  color: #FF9800;
}

.attributes {
  margin-bottom: 40rpx;
}

.attribute-item {
  margin-bottom: 30rpx;
}

.attribute-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10rpx;
}

.attribute-name {
  font-size: 26rpx;
  color: #333;
}

.attribute-value {
  font-size: 24rpx;
  color: #666;
}

.progress-bar {
  height: 16rpx;
  background: #f0f0f0;
  border-radius: 8rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 8rpx;
  transition: width 0.3s ease;
}

.progress-fill.health {
  background: linear-gradient(90deg, #4CAF50, #8BC34A);
}

.progress-fill.charm {
  background: linear-gradient(90deg, #E91E63, #F06292);
}

.progress-fill.intelligence {
  background: linear-gradient(90deg, #2196F3, #64B5F6);
}

.actions {
  padding: 30rpx 0 20rpx;
  text-align: center;
}

.quit-job-btn {
  background: linear-gradient(45deg, #f44336, #d32f2f);
  color: white;
  border: none;
  padding: 20rpx 40rpx;
  border-radius: 25rpx;
  font-size: 26rpx;
  font-weight: 500;
}
</style>