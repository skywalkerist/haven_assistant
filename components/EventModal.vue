<template>
  <view class="modal-overlay" v-if="visible">
    <view class="modal-content">
      <view class="modal-header">
        <text class="modal-title">人生选择</text>
      </view>
      
      <view class="event-content">
        <view class="person-info">
          <text class="person-name">{{ event.person.name }}</text>
          <text class="person-age">{{ event.person.age }}岁</text>
        </view>
        
        <view class="event-title">{{ event.type }}</view>
        
        <view class="event-description">
          {{ getEventDescription() }}
        </view>
        
        <view class="options-list">
          <view 
            class="option-item" 
            v-for="(option, index) in event.options" 
            :key="index"
            @click="selectOption(option)"
            :class="{ 'disabled': globalEconomy - option.cost < -300000 }"
          >
            <view class="option-content">
              <text class="option-text">{{ option.text }}</text>
              <view class="option-effects">
                <text class="cost" v-if="option.cost > 0">
                  费用: {{ option.cost.toLocaleString() }}元
                </text>
                <view class="effects" v-if="Object.keys(option.effects).length > 0">
                  <text 
                    class="effect-item" 
                    v-for="(value, key) in option.effects" 
                    :key="key"
                  >
                    {{ getEffectText(key, value) }}
                  </text>
                </view>
              </view>
            </view>
            <view class="option-arrow">→</view>
          </view>
        </view>
        
        <view class="economy-info">
          <text class="economy-text">当前经济: {{ globalEconomy.toLocaleString() }}元</text>
          <text class="bankruptcy-line">破产线: -300,000元</text>
          <text class="available-debt" :class="{ 'warning': globalEconomy < 0 }">
            可用额度: {{ (globalEconomy + 300000).toLocaleString() }}元
          </text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'EventModal',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    event: {
      type: Object,
      default: () => ({})
    },
    globalEconomy: {
      type: Number,
      default: 0
    }
  },
  emits: ['selectOption'],
  methods: {
    selectOption(option) {
      if (this.globalEconomy - option.cost < -300000) {
        uni.showToast({
          title: '此选择将导致破产',
          icon: 'none',
          duration: 3000
        })
        return
      }
      this.$emit('selectOption', option)
    },
    
    getEventDescription() {
      const descriptions = {
        // 重要事件
        '高考': '人生的重要转折点，高考成绩将决定你能进入什么档次的大学。',
        '读研选择': '继续深造还是直接就业？读研可以提升学历但需要时间和金钱投入。',
        '找工作': '选择人生第一份工作，不同职业的收入和发展前景差异很大。',
        '升职机会': '通过努力工作获得了升职的机会，是否争取更高的职位和薪酬？',
        '择偶': '在婚恋市场上寻找人生伴侣，需要考虑双方的条件和匹配度。',
        '生育': '是否生育后代延续血脉？需要考虑经济能力和抚养责任。',
        '退休': '到了退休年龄，是否继续工作还是享受退休生活？',
        
        // 教育阶段事件
        '早教班': '孩子在婴儿期是否需要早期教育来开发智力？',
        '幼儿园择校': '选择公立还是私立幼儿园，会影响孩子的早期发展。',
        '小学择校': '选择合适的小学对孩子的成长很重要，学区房是否值得购买？',
        '课外补习': '补习班可以提高成绩，但也可能增加孩子的压力。',
        '小升初': '选择普通初中还是民办名校，也可以选择辍学就业。',
        '高中选择': '高中阶段的选择将直接影响高考成绩和大学入学。',
        '高中恋爱': '青春期的恋爱可能会影响学习成绩，但也能提升魅力。',
        
        // 职业发展事件
        'MBA深造': '追求更高学历和管理技能，但需要大量时间和金钱投入。',
        '大学创业': '在校期间参与创业项目，可能成功也可能失败。',
        '中年危机': '中年阶段面临事业瀑颈，是安于现状还是寻求突破？',
        
        // 生活事件
        '买房': '是否购买人生第一套住房，需要考虑经济能力和地段选择。',
        '副业投资': '选择副业或投资项目来增加收入，但也存在风险。',
        '父母养老': '父母老了需要照顾，选择送养老院还是在家照料。',
        
        // 随机事件
        '健身年卡': '是否办理健身卡来保持身体健康和提升个人魅力？',
        '买彩票': '小试运气购买彩票，虽然中奖概率很小但万一呢？',
        '医美抗衰': '通过医美手段保持青春和魅力，但也有一定风险。',
        '健康作息': '改善生活作息来提高身体健康，需要一定的意志力。',
        '重病': '不幸患上重病，需要选择治疗方案，不同治疗效果和费用差异很大。',
        '意外': '遇到了不可预见的意外事件，只能接受现实。'
      }
      return descriptions[this.event.type] || '面临人生选择，请慎重考虑。'
    },
    
    getEffectText(key, value) {
      const effectNames = {
        health: '健康',
        charm: '魅力', 
        intelligence: '智力',
        occupation: '职业'
      }
      
      if (key === 'occupation') {
        return `职业: ${value}`
      } else {
        const sign = value > 0 ? '+' : ''
        return `${effectNames[key]}: ${sign}${value}`
      }
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
  padding: 40rpx 30rpx 20rpx;
  text-align: center;
  border-bottom: 1rpx solid #eee;
}

.modal-title {
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
}

.event-content {
  padding: 30rpx;
}

.person-info {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30rpx;
  padding: 20rpx;
  background: #f8f9fa;
  border-radius: 12rpx;
}

.person-name {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-right: 20rpx;
}

.person-age {
  font-size: 28rpx;
  color: #666;
  background: #e9ecef;
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
}

.event-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #2c3e50;
  text-align: center;
  margin-bottom: 20rpx;
}

.event-description {
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
  margin-bottom: 40rpx;
  padding: 20rpx;
  background: #f8f9fa;
  border-radius: 12rpx;
  border-left: 4rpx solid #007bff;
}

.options-list {
  margin-bottom: 30rpx;
}

.option-item {
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

.option-item:hover {
  border-color: #007bff;
  box-shadow: 0 4rpx 12rpx rgba(0, 123, 255, 0.15);
}

.option-item.disabled {
  opacity: 0.5;
  background: #f8f9fa;
  border-color: #dee2e6;
}

.option-content {
  flex: 1;
}

.option-text {
  font-size: 30rpx;
  font-weight: 500;
  color: #333;
  display: block;
  margin-bottom: 8rpx;
}

.option-effects {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.cost {
  font-size: 24rpx;
  color: #dc3545;
  font-weight: 500;
}

.effects {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.effect-item {
  font-size: 22rpx;
  color: #28a745;
  background: #d4edda;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  border: 1rpx solid #c3e6cb;
}

.option-arrow {
  font-size: 32rpx;
  color: #007bff;
  font-weight: bold;
}

.economy-info {
  text-align: center;
  padding: 20rpx;
  background: #e3f2fd;
  border-radius: 12rpx;
}

.economy-text {
  font-size: 26rpx;
  color: #1976d2;
  font-weight: 500;
  display: block;
  margin-bottom: 8rpx;
}

.bankruptcy-line {
  font-size: 22rpx;
  color: #f44336;
  display: block;
  margin-bottom: 8rpx;
}

.available-debt {
  font-size: 24rpx;
  color: #4caf50;
  font-weight: 500;
  display: block;
}

.available-debt.warning {
  color: #ff9800;
}
</style>