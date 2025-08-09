<template>
  <view class="sheet-overlay" v-if="visible" @click="handleOverlayClick">
    <view class="sheet" @click.stop>
      <view class="header">
        <text class="icon">{{ event?.icon || '🔔' }}</text>
        <view class="titles">
          <text class="title">{{ event?.title || '事件' }}</text>
          <text class="subtitle">{{ event?.text || '' }}</text>
        </view>
      </view>

      <view class="choices" v-if="event?.choices?.length">
        <button 
          v-for="(choice, index) in event.choices" 
          :key="index"
          class="choice" 
          @click="handleChoose(index)"
        >
          {{ choice.text }}
        </button>
      </view>

      <button class="cancel" @click="handleClose">稍后处理</button>
    </view>
  </view>
</template>

<script>
export default {
  name: 'EventSheet',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    event: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['update:visible', 'choose', 'close'],
  methods: {
    handleChoose(index) {
      this.$emit('choose', index)
      this.handleClose()
    },
    
    handleClose() {
      this.$emit('update:visible', false)
      this.$emit('close')
    },
    
    handleOverlayClick() {
      // 点击遮罩关闭
      this.handleClose()
    }
  }
}
</script>

<style scoped>
.sheet-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 999;
  animation: fadeIn 0.3s ease;
}

.sheet {
  background: #fff;
  border-radius: 16rpx 16rpx 0 0;
  padding: 32rpx;
  width: 100%;
  max-height: 60vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

.header {
  display: flex;
  gap: 16rpx;
  align-items: flex-start;
  margin-bottom: 24rpx;
}

.icon {
  font-size: 40rpx;
  line-height: 1;
}

.titles {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  flex: 1;
}

.title {
  font-weight: 600;
  font-size: 32rpx;
  color: #333;
  line-height: 1.3;
}

.subtitle {
  color: #666;
  font-size: 26rpx;
  line-height: 1.4;
}

.choices {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  margin-bottom: 20rpx;
}

.choice {
  background: linear-gradient(45deg, #007AFF, #0056CC);
  color: white;
  border: none;
  border-radius: 12rpx;
  padding: 24rpx;
  font-size: 28rpx;
  font-weight: 500;
  text-align: center;
  transition: all 0.2s ease;
}

.choice:active {
  transform: scale(0.98);
  opacity: 0.8;
}

.cancel {
  background: #f6f6f6;
  color: #666;
  border: none;
  border-radius: 12rpx;
  padding: 20rpx;
  font-size: 26rpx;
  text-align: center;
  margin-top: 8rpx;
}

.cancel:active {
  background: #e6e6e6;
}
</style>