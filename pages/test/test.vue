<template>
  <view class="test-page">
    <view class="test-header">
      <text class="test-title">游戏功能测试</text>
    </view>
    
    <view class="test-buttons">
      <button @click="testEvents" class="test-btn">测试事件系统</button>
      <button @click="testEconomics" class="test-btn">测试经济系统</button>
      <button @click="testPersonCreation" class="test-btn">测试人物创建</button>
      <button @click="viewGameState" class="test-btn">查看游戏状态</button>
    </view>
    
    <view class="test-results">
      <text class="result-title">测试结果：</text>
      <text class="result-text">{{ testResult }}</text>
    </view>
  </view>
</template>

<script>
import { gameStore } from '@/store/gameStore.js'

export default {
  data() {
    return {
      testResult: '点击按钮开始测试...'
    }
  },
  methods: {
    testEvents() {
      if (gameStore.persons.length === 0) {
        gameStore.createInitialPerson()
      }
      
      const person = gameStore.persons[0]
      person.age = 18
      person.intelligence = 85
      
      const events = gameStore.getAgeEvents(18, person)
      const options = gameStore.getEventOptions('高考志愿', person)
      
      this.testResult = `年龄${person.age}岁可触发事件: ${events.join(', ')}\n高考选项数量: ${options.length}`
    },
    
    testEconomics() {
      if (gameStore.persons.length === 0) {
        gameStore.createInitialPerson()
      }
      
      const person = gameStore.persons[0]
      person.age = 25
      person.occupation = '程序员'
      person.intelligence = 80
      person.charm = 70
      person.health = 90
      
      gameStore.updatePersonEconomics(person)
      
      this.testResult = `职业: ${person.occupation}\n经济贡献: ${person.economicContribution}元/年\n收入: ${person.income}元/年`
    },
    
    testPersonCreation() {
      gameStore.createInitialPerson()
      const person = gameStore.persons[gameStore.persons.length - 1]
      
      this.testResult = `创建了新人物:\n姓名: ${person.name}\n性别: ${person.gender}\n健康: ${person.health}\n魅力: ${person.charm}\n智力: ${person.intelligence}`
    },
    
    viewGameState() {
      this.testResult = `游戏状态:\n是否开始: ${gameStore.isGameStarted}\n当前年份: ${gameStore.currentYear}\n全局经济: ${gameStore.globalEconomy}元\n人物数量: ${gameStore.persons.length}`
    }
  }
}
</script>

<style scoped>
.test-page {
  padding: 40rpx;
  background: #f5f5f5;
  min-height: 100vh;
}

.test-header {
  text-align: center;
  margin-bottom: 40rpx;
}

.test-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
}

.test-buttons {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin-bottom: 40rpx;
}

.test-btn {
  background: #007bff;
  color: white;
  border: none;
  border-radius: 12rpx;
  padding: 24rpx;
  font-size: 28rpx;
}

.test-results {
  background: white;
  padding: 30rpx;
  border-radius: 12rpx;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.1);
}

.result-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 20rpx;
}

.result-text {
  font-size: 26rpx;
  color: #666;
  line-height: 1.6;
  white-space: pre-line;
}
</style>