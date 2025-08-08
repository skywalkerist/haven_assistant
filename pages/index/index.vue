<template>
  <view class="game-container">
    <!-- 游戏头部信息 -->
    <view class="game-header">
      <view class="game-title">中国式人生</view>
      <view class="game-stats">
        <view class="stat-item">
          <text class="stat-label">年份:</text>
          <text class="stat-value">{{ gameStore.currentYear }}</text>
        </view>
        <view class="stat-item">
          <text class="stat-label">经济:</text>
          <text class="stat-value" :class="{ 'negative': gameStore.globalEconomy < 0, 'danger': gameStore.globalEconomy < -200000 }">
            {{ gameStore.globalEconomy.toLocaleString() }}元
          </text>
          <text class="debt-warning" v-if="gameStore.globalEconomy < -200000">
            距破产还有{{ (300000 + gameStore.globalEconomy).toLocaleString() }}元
          </text>
        </view>
        <view class="stat-item">
          <text class="stat-label">人口:</text>
          <text class="stat-value">{{ alivePersonsCount }}</text>
        </view>
      </view>
      
      <!-- 游戏控制按钮 -->
      <view class="game-controls">
        <button 
          class="control-btn start-btn" 
          v-if="!gameStore.isGameStarted"
          @click="startGame"
        >
          开始游戏
        </button>
        <button 
          class="control-btn pause-btn"
          v-if="gameStore.isGameStarted"
          @click="togglePause"
        >
          {{ gameStore.isPaused ? '继续' : '暂停' }}
        </button>
        <button 
          class="control-btn save-btn"
          v-if="gameStore.isGameStarted"
          @click="saveGame"
        >
          保存游戏
        </button>
        <button 
          class="control-btn load-btn"
          @click="showLoadModal = true"
        >
          加载游戏
        </button>
        <button 
          class="control-btn reset-btn"
          v-if="gameStore.isGameStarted"
          @click="resetGame"
        >
          重新开始
        </button>
      </view>
    </view>
    
    <!-- 家族树区域 -->
    <view class="family-container">
      <scroll-view class="family-scroll" scroll-y="true" v-if="gameStore.persons.length > 0">
        <FamilyTree 
          :persons="gameStore.persons"
          @showDetails="showPersonDetails"
        />
      </scroll-view>
      
      <!-- 空状态 -->
      <view class="empty-state" v-if="gameStore.persons.length === 0">
        <text class="empty-text">点击"开始游戏"创造你的第一个人生</text>
      </view>
    </view>
    
    <!-- 人物详情弹窗 -->
    <PersonDetailsModal 
      :visible="showDetailsModal"
      :person="selectedPerson"
      @close="closePersonDetails"
    />
    
    <!-- 事件选择弹窗 -->
    <EventModal
      :visible="gameStore.isEventActive"
      :event="gameStore.currentEvent || {}"
      :globalEconomy="gameStore.globalEconomy"
      @selectOption="handleEventChoice"
    />
    
    <!-- 存档加载弹窗 -->
    <view class="modal-overlay" v-if="showLoadModal" @click="showLoadModal = false">
      <view class="load-modal" @click.stop>
        <view class="modal-header">
          <text class="modal-title">选择存档</text>
          <view class="close-btn" @click="showLoadModal = false">✕</view>
        </view>
        <scroll-view class="save-list" scroll-y="true">
          <view 
            class="save-item" 
            v-for="save in saveList" 
            :key="save._id"
            @click="loadGame(save._id)"
          >
            <text class="save-name">{{ save.save_name }}</text>
            <text class="save-info">第{{ save.current_year }}年 - {{ save.global_economy.toLocaleString() }}元</text>
            <text class="save-time">{{ formatTime(save.update_time) }}</text>
          </view>
          <view class="empty-saves" v-if="saveList.length === 0">
            <text>暂无存档</text>
          </view>
        </scroll-view>
      </view>
    </view>
  </view>
</template>

<script>
import { gameStore, gameComputed } from '@/store/gameStore.js'
import PersonCard from '@/components/PersonCard.vue'
import PersonDetailsModal from '@/components/PersonDetailsModal.vue'
import EventModal from '@/components/EventModal.vue'
import FamilyTree from '@/components/FamilyTree.vue'

export default {
  components: {
    PersonCard,
    PersonDetailsModal,
    EventModal,
    FamilyTree
  },
  data() {
    return {
      gameStore,
      showDetailsModal: false,
      selectedPerson: {},
      showLoadModal: false,
      saveList: []
    }
  },
  computed: {
    alivePersonsCount() {
      return gameComputed.alivePersonsCount.value
    }
  },
  onLoad() {
    
  },
  onUnload() {
    // 页面卸载时清理定时器
    if (gameStore.gameTimer) {
      clearInterval(gameStore.gameTimer)
    }
  },
  methods: {
    startGame() {
      gameStore.initGame()
      uni.showToast({
        title: '游戏开始！',
        icon: 'success'
      })
    },
    
    togglePause() {
      gameStore.togglePause()
      uni.showToast({
        title: gameStore.isPaused ? '游戏暂停' : '游戏继续',
        icon: 'none'
      })
    },
    
    resetGame() {
      uni.showModal({
        title: '确认重置',
        content: '确定要重新开始游戏吗？当前进度将丢失。',
        success: (res) => {
          if (res.confirm) {
            if (gameStore.gameTimer) {
              clearInterval(gameStore.gameTimer)
            }
            gameStore.isGameStarted = false
            gameStore.currentYear = 0
            gameStore.persons = []
            gameStore.isPaused = false
            gameStore.isEventActive = false
            gameStore.currentEvent = null
            uni.showToast({
              title: '游戏已重置',
              icon: 'success'
            })
          }
        }
      })
    },
    
    showPersonDetails(person) {
      this.selectedPerson = person
      this.showDetailsModal = true
      // 打开人物详情时自动暂停游戏
      if (gameStore.isGameStarted && !gameStore.isPaused) {
        gameStore.isPaused = true
      }
    },
    
    closePersonDetails() {
      this.showDetailsModal = false
      // 关闭人物详情时恢复游戏（如果之前是运行状态）
      if (gameStore.isGameStarted && gameStore.isPaused && !gameStore.isEventActive) {
        gameStore.isPaused = false
      }
    },
    
    handleEventChoice(option) {
      gameStore.handleEventChoice(option)
    },
    
    async saveGame() {
      try {
        await gameStore.saveToCloud()
      } catch (error) {
        console.error('保存游戏失败:', error)
      }
    },
    
    async loadGame(saveId) {
      try {
        await gameStore.loadFromCloud(saveId)
        this.showLoadModal = false
      } catch (error) {
        console.error('加载游戏失败:', error)
      }
    },
    
    async loadSaveList() {
      try {
        this.saveList = await gameStore.getSaveList()
      } catch (error) {
        console.error('获取存档列表失败:', error)
        this.saveList = []
      }
    },
    
    formatTime(dateStr) {
      const date = new Date(dateStr)
      return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`
    }
  },
  
  watch: {
    showLoadModal(newVal) {
      if (newVal) {
        this.loadSaveList()
      }
    }
  }
}
</script>

<style scoped>
.game-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
}

.game-header {
  background: rgba(255, 255, 255, 0.95);
  padding: 30rpx 20rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.1);
}

.game-title {
  font-size: 48rpx;
  font-weight: bold;
  color: #333;
  text-align: center;
  margin-bottom: 20rpx;
}

.game-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20rpx;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 24rpx;
  color: #666;
  margin-bottom: 5rpx;
}

.stat-value {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
}

.stat-value.negative {
  color: #ff9800;
}

.stat-value.danger {
  color: #f44336;
}

.debt-warning {
  font-size: 20rpx;
  color: #f44336;
  margin-top: 4rpx;
}

.game-controls {
  display: flex;
  justify-content: center;
  gap: 20rpx;
}

.control-btn {
  padding: 16rpx 32rpx;
  border-radius: 25rpx;
  font-size: 28rpx;
  font-weight: 500;
  border: none;
  color: white;
}

.start-btn {
  background: linear-gradient(45deg, #4CAF50, #45a049);
}

.pause-btn {
  background: linear-gradient(45deg, #ff9800, #f57c00);
}

.save-btn {
  background: linear-gradient(45deg, #2196F3, #1976D2);
}

.load-btn {
  background: linear-gradient(45deg, #9C27B0, #7B1FA2);
}

.reset-btn {
  background: linear-gradient(45deg, #f44336, #d32f2f);
}

.family-container {
  flex: 1;
  padding: 20rpx;
}

.family-scroll {
  width: 100%;
  height: calc(100vh - 280rpx);
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300rpx;
}

.empty-text {
  font-size: 32rpx;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
}

/* 加载弹窗样式 */
.load-modal {
  background: white;
  border-radius: 20rpx;
  width: 90%;
  max-width: 700rpx;
  height: 80vh;
  display: flex;
  flex-direction: column;
}

.save-list {
  flex: 1;
  padding: 0 30rpx;
}

.save-item {
  background: #f8f9fa;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 16rpx;
  border: 2rpx solid transparent;
  transition: all 0.3s ease;
}

.save-item:hover {
  border-color: #007bff;
  box-shadow: 0 4rpx 12rpx rgba(0, 123, 255, 0.15);
}

.save-name {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 8rpx;
}

.save-info {
  font-size: 26rpx;
  color: #666;
  display: block;
  margin-bottom: 4rpx;
}

.save-time {
  font-size: 24rpx;
  color: #999;
  display: block;
}

.empty-saves {
  text-align: center;
  padding: 100rpx 0;
  color: #999;
  font-size: 28rpx;
}
</style>
