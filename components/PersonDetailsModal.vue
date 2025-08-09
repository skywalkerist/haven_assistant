<template>
  <view class="modal-overlay" v-if="visible" @click="closeModal">
    <view class="modal-content" @click.stop>
      <view class="modal-header">
        <text class="modal-title">{{ person.name }}的详细信息</text>
        <view class="close-btn" @click="closeModal">✕</view>
      </view>
      
      <view class="person-info">
        <view class="basic-info">
          <view class="info-item">
            <view class="info-content">
              <text class="info-label">年龄</text>
              <text class="info-value">{{ person.age }}岁</text>
            </view>
            <view class="info-arrow">→</view>
          </view>
          <view class="info-item">
            <view class="info-content">
              <text class="info-label">性别</text>
              <text class="info-value">{{ person.gender }}</text>
            </view>
            <view class="info-arrow">→</view>
          </view>
          <view class="info-item">
            <view class="info-content">
              <text class="info-label">状态</text>
              <text class="info-value" :class="person.isAlive ? 'alive' : 'dead'">
                {{ person.isAlive ? '健在' : '已故' }}
              </text>
            </view>
            <view class="info-arrow">→</view>
          </view>
          <view class="info-item">
            <view class="info-content">
              <text class="info-label">职业</text>
              <text class="info-value">{{ person.occupation || '无' }}</text>
            </view>
            <view class="info-arrow">→</view>
          </view>
          <view class="info-item">
            <view class="info-content">
              <text class="info-label">教育</text>
              <text class="info-value">{{ person.education }}</text>
            </view>
            <view class="info-arrow">→</view>
          </view>
          <view class="info-item" v-if="person.schoolLevel">
            <view class="info-content">
              <text class="info-label">学历档次</text>
              <text class="info-value">{{ person.schoolLevel }}</text>
            </view>
            <view class="info-arrow">→</view>
          </view>
          <view class="info-item" v-if="person.major">
            <view class="info-content">
              <text class="info-label">专业</text>
              <text class="info-value">{{ person.major }}</text>
            </view>
            <view class="info-arrow">→</view>
          </view>
          <view class="info-item" v-if="person.workYears > 0">
            <view class="info-content">
              <text class="info-label">工作年限</text>
              <text class="info-value">{{ person.workYears }}年</text>
            </view>
            <view class="info-arrow">→</view>
          </view>
          <view class="info-item" v-if="person.isRetired">
            <view class="info-content">
              <text class="info-label">状态</text>
              <text class="info-value retired">已退休</text>
            </view>
            <view class="info-arrow">→</view>
          </view>
          <view class="info-item" v-if="person.jobSeeking">
            <view class="info-content">
              <text class="info-label">状态</text>
              <text class="info-value job-seeking">正在找工作</text>
            </view>
            <view class="info-arrow">→</view>
          </view>
        </view>
        
        <!-- 核心属性 -->
        <view class="attributes">
          <text class="section-title">核心属性</text>
          <view class="attribute-item">
            <view class="attribute-header">
              <text class="attribute-name">健康</text>
              <text class="attribute-value">{{ person.health || 0 }}/100</text>
            </view>
            <view class="progress-bar">
              <view class="progress-fill health" :style="{ width: (person.health || 0) + '%' }"></view>
            </view>
          </view>
          
          <view class="attribute-item">
            <view class="attribute-header">
              <text class="attribute-name">魅力</text>
              <text class="attribute-value">{{ person.charm || 0 }}/100</text>
            </view>
            <view class="progress-bar">
              <view class="progress-fill charm" :style="{ width: (person.charm || 0) + '%' }"></view>
            </view>
          </view>
          
          <view class="attribute-item">
            <view class="attribute-header">
              <text class="attribute-name">智力</text>
              <text class="attribute-value">{{ person.intelligence || 0 }}/100</text>
            </view>
            <view class="progress-bar">
              <view class="progress-fill intelligence" :style="{ width: (person.intelligence || 0) + '%' }"></view>
            </view>
          </view>
          
          <view class="attribute-item">
            <view class="attribute-header">
              <text class="attribute-name">稳定性</text>
              <text class="attribute-value">{{ person.stability || 50 }}/100</text>
            </view>
            <view class="progress-bar">
              <view class="progress-fill stability" :style="{ width: (person.stability || 50) + '%' }"></view>
            </view>
          </view>
          
          <view class="attribute-item">
            <view class="attribute-header">
              <text class="attribute-name">动力</text>
              <text class="attribute-value">{{ person.motivation || 50 }}/100</text>
            </view>
            <view class="progress-bar">
              <view class="progress-fill motivation" :style="{ width: (person.motivation || 50) + '%' }"></view>
            </view>
          </view>
          
          <view class="attribute-item">
            <view class="attribute-header">
              <text class="attribute-name">创造力</text>
              <text class="attribute-value">{{ person.creativity || 50 }}/100</text>
            </view>
            <view class="progress-bar">
              <view class="progress-fill creativity" :style="{ width: (person.creativity || 50) + '%' }"></view>
            </view>
          </view>
        </view>
        
        <!-- 状态属性 -->
        <view class="state-attributes">
          <text class="section-title">状态信息</text>
          <view class="info-item">
            <view class="info-content">
              <text class="info-label">压力水平</text>
              <text class="effect-item" :class="getStressClass(person.stress || 0)">{{ person.stress || 0 }}/100</text>
            </view>
            <view class="info-arrow">→</view>
          </view>
          <view class="info-item" v-if="person.occupation">
            <view class="info-content">
              <text class="info-label">工作满意度</text>
              <text class="effect-item" :class="getSatisfactionClass(person.satisfaction || 50)">{{ person.satisfaction || 50 }}/100</text>
            </view>
            <view class="info-arrow">→</view>
          </view>
          <view class="info-item" v-if="(person.cumStudyHours || 0) > 0">
            <view class="info-content">
              <text class="info-label">累计学习</text>
              <text class="effect-item">{{ person.cumStudyHours || 0 }}小时</text>
            </view>
            <view class="info-arrow">→</view>
          </view>
          <view class="info-item" v-if="person.flags?.burnoutThisYear">
            <view class="info-content">
              <text class="info-label">状态</text>
              <text class="effect-item burnout">今年倦怠中</text>
            </view>
            <view class="info-arrow">→</view>
          </view>
          <!-- 新经济系统属性 -->
          <view class="info-item" v-if="person.psyche !== undefined">
            <view class="info-content">
              <text class="info-label">心理健康</text>
              <text class="effect-item" :class="getPsycheClass(person.psyche || 50)">{{ person.psyche || 50 }}/100</text>
            </view>
            <view class="info-arrow">→</view>
          </view>
          <view class="info-item" v-if="person.strain !== undefined">
            <view class="info-content">
              <text class="info-label">生活压力</text>
              <text class="effect-item" :class="getStrainClass(person.strain || 0)">{{ person.strain || 0 }}/100</text>
            </view>
            <view class="info-arrow">→</view>
          </view>
          <view class="info-item" v-if="person.competitiveness !== undefined && person.competitiveness > 0">
            <view class="info-content">
              <text class="info-label">竞争力</text>
              <text class="effect-item">{{ Math.round(person.competitiveness) }}/100</text>
            </view>
            <view class="info-arrow">→</view>
          </view>
        </view>
        
        <!-- 经济信息 -->
        <view class="economic-info">
          <text class="section-title">经济状况</text>
          <view class="info-item">
            <view class="info-content">
              <text class="info-label">年收入</text>
              <text class="cost positive">{{ person.income ? person.income.toLocaleString() : '0' }}元</text>
            </view>
            <view class="info-arrow">→</view>
          </view>
          <view class="info-item">
            <view class="info-content">
              <text class="info-label">年支出</text>
              <text class="cost">{{ calculateExpense() }}元</text>
            </view>
            <view class="info-arrow">→</view>
          </view>
          <view class="info-item">
            <view class="info-content">
              <text class="info-label">年收支</text>
              <text class="cost" :class="person.economicContribution >= 0 ? 'positive' : ''">
                {{ person.economicContribution >= 0 ? '+' : '' }}{{ person.economicContribution.toLocaleString() }}元
              </text>
            </view>
            <view class="info-arrow">→</view>
          </view>
        </view>
        
        <!-- 操作按钮 -->
        <view class="actions" v-if="person.occupation && person.isAlive">
          <text class="section-title">操作选项</text>
          <view class="info-item action-item" @click="quitJob">
            <view class="info-content">
              <text class="info-label">职业操作</text>
              <text class="cost">辞职</text>
            </view>
            <view class="info-arrow">→</view>
          </view>
        </view>
        
        <!-- 家庭信息 -->
        <view class="family-info" v-if="person.partner || person.children.length > 0">
          <text class="section-title">家庭关系</text>
          <view class="info-item" v-if="person.partner">
            <view class="info-content">
              <text class="info-label">伴侣</text>
              <text class="info-value">{{ person.partner.name }}</text>
            </view>
            <view class="info-arrow">→</view>
          </view>
          <view class="info-item" v-if="person.children.length > 0">
            <view class="info-content">
              <text class="info-label">子女</text>
              <text class="info-value">{{ person.children.length }}人</text>
            </view>
            <view class="info-arrow">→</view>
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
      
      // 使用新经济系统的完整支出计算
      // 支出数据已在updatePersonEconomics中计算并存储
      // 这里计算收入-贡献得到支出
      const income = this.person.income || 0
      const contribution = this.person.economicContribution || 0
      const expense = income - contribution
      
      return Math.max(0, expense).toLocaleString()
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
            this.person.satisfaction = 50 // 重置满意度
            
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
    },
    
    getStressClass(stress) {
      if (stress >= 80) return 'stress-critical'
      if (stress >= 60) return 'stress-high'
      if (stress >= 40) return 'stress-medium'
      return 'stress-low'
    },
    
    getSatisfactionClass(satisfaction) {
      if (satisfaction >= 80) return 'satisfaction-high'
      if (satisfaction >= 60) return 'satisfaction-medium'
      if (satisfaction >= 40) return 'satisfaction-low'
      return 'satisfaction-critical'
    },
    
    getPsycheClass(psyche) {
      if (psyche >= 80) return 'psyche-excellent'
      if (psyche >= 60) return 'psyche-good' 
      if (psyche >= 40) return 'psyche-fair'
      return 'psyche-poor'
    },
    
    getStrainClass(strain) {
      if (strain >= 80) return 'strain-critical'
      if (strain >= 60) return 'strain-high'
      if (strain >= 40) return 'strain-medium'
      return 'strain-low'
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
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
}

.modal-content {
  background: white;
  border-radius: 20rpx;
  width: 90%;
  max-width: 700rpx;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20rpx 60rpx rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 40rpx 30rpx 20rpx;
  border-bottom: 1rpx solid #eee;
}

.modal-title {
  font-size: 40rpx;
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

.basic-info, .economic-info, .family-info, .state-attributes, .actions {
  margin-bottom: 40rpx;
}

.info-item {
  background: white;
  border: 2rpx solid #e9ecef;
  border-radius: 16rpx;
  margin-bottom: 16rpx;
  padding: 24rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: all 0.3s ease;
}

.info-item:hover {
  border-color: #007bff;
  box-shadow: 0 4rpx 12rpx rgba(0, 123, 255, 0.15);
}

.action-item {
  cursor: pointer;
}

.action-item:hover {
  border-color: #dc3545;
  box-shadow: 0 4rpx 12rpx rgba(220, 53, 69, 0.15);
}

.info-content {
  flex: 1;
}

.info-label {
  font-size: 26rpx;
  color: #666;
  display: block;
  margin-bottom: 4rpx;
}

.info-value {
  font-size: 26rpx;
  color: #333;
  font-weight: 500;
}

.info-arrow {
  font-size: 32rpx;
  color: #007bff;
  font-weight: bold;
}

.cost {
  font-size: 24rpx;
  color: #dc3545;
  font-weight: 500;
}

.cost.positive {
  color: #28a745;
}

.effect-item {
  font-size: 22rpx;
  color: #28a745;
  background: #d4edda;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  border: 1rpx solid #c3e6cb;
}

.info-value.alive {
  color: #4CAF50;
}

.info-value.dead {
  color: #F44336;
}

.info-value.positive {
  color: #4CAF50;
}

.info-value.negative {
  color: #F44336;
}

.info-value.retired {
  color: #9E9E9E;
}

.info-value.job-seeking {
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

.progress-fill.stability {
  background: linear-gradient(90deg, #795548, #A1887F);
}

.progress-fill.motivation {
  background: linear-gradient(90deg, #FF9800, #FFB74D);
}

.progress-fill.creativity {
  background: linear-gradient(90deg, #9C27B0, #CE93D8);
}

.state-attributes {
  margin-bottom: 40rpx;
}

.stress-critical {
  background: #ffebee !important;
  color: #F44336 !important;
  border: 1rpx solid #ffcdd2 !important;
}

.stress-high {
  background: #fff3e0 !important;
  color: #FF9800 !important;
  border: 1rpx solid #ffcc02 !important;
}

.stress-medium {
  background: #fffde7 !important;
  color: #FFC107 !important;
  border: 1rpx solid #ffeb3b !important;
}

.stress-low {
  background: #e8f5e8 !important;
  color: #4CAF50 !important;
  border: 1rpx solid #c8e6c9 !important;
}

.satisfaction-high {
  background: #e8f5e8 !important;
  color: #4CAF50 !important;
  border: 1rpx solid #c8e6c9 !important;
}

.satisfaction-medium {
  background: #f1f8e9 !important;
  color: #8BC34A !important;
  border: 1rpx solid #dcedc8 !important;
}

.satisfaction-low {
  background: #fff3e0 !important;
  color: #FF9800 !important;
  border: 1rpx solid #ffcc02 !important;
}

.satisfaction-critical {
  background: #ffebee !important;
  color: #F44336 !important;
  border: 1rpx solid #ffcdd2 !important;
}

.burnout {
  background: #ffebee !important;
  color: #D32F2F !important;
  border: 1rpx solid #ef9a9a !important;
}


/* 新经济系统样式 */
.psyche-excellent {
  background: #e8f5e8 !important;
  color: #4CAF50 !important;
  border: 1rpx solid #c8e6c9 !important;
}

.psyche-good {
  background: #f1f8e9 !important;
  color: #8BC34A !important;
  border: 1rpx solid #dcedc8 !important;
}

.psyche-fair {
  background: #fff3e0 !important;
  color: #FF9800 !important;
  border: 1rpx solid #ffcc02 !important;
}

.psyche-poor {
  background: #ffebee !important;
  color: #F44336 !important;
  border: 1rpx solid #ffcdd2 !important;
}

.strain-critical {
  background: #ffebee !important;
  color: #F44336 !important;
  border: 1rpx solid #ffcdd2 !important;
}

.strain-high {
  background: #fff3e0 !important;
  color: #FF9800 !important;
  border: 1rpx solid #ffcc02 !important;
}

.strain-medium {
  background: #fffde7 !important;
  color: #FFC107 !important;
  border: 1rpx solid #ffeb3b !important;
}

.strain-low {
  background: #e8f5e8 !important;
  color: #4CAF50 !important;
  border: 1rpx solid #c8e6c9 !important;
}
</style>