<template>
  <view class="person-card" :class="{ 'dead': !person.isAlive }" @click="showDetails">
    <!-- 年龄标签 -->
    <view class="age-tag">{{ person.age }}岁</view>
    
    <!-- 性别标签 -->
    <view class="gender-tag" :class="person.gender === '男' ? 'male' : 'female'">
      {{ person.gender }}
    </view>
    
    <!-- 人物头像区域 -->
    <view class="avatar">
      <text class="avatar-text">{{ getAvatarEmoji() }}</text>
    </view>
    
    <!-- 人物姓名 -->
    <view class="name">{{ person.name }}</view>
    
    <!-- 职业 -->
    <view class="occupation" v-if="person.occupation">{{ person.occupation }}</view>
    
    <!-- 学历 -->
    <view class="education" v-if="person.education && person.education !== '未入学'">
      {{ person.schoolLevel || person.education }}
    </view>
    
    <!-- 专业 -->
    <view class="major" v-if="person.major">
      {{ person.major }}
    </view>
    
    <!-- 经济贡献 -->
    <view class="economic-contribution" :class="person.economicContribution >= 0 ? 'positive' : 'negative'">
      {{ person.economicContribution >= 0 ? '+' : '' }}{{ person.economicContribution.toLocaleString() }}元/年
    </view>
    
    <!-- 生命状态指示器 -->
    <view class="life-indicator" :class="{ 'alive': person.isAlive, 'dead': !person.isAlive }"></view>
  </view>
</template>

<script>
export default {
  name: 'PersonCard',
  props: {
    person: {
      type: Object,
      required: true
    }
  },
  emits: ['showDetails'],
  methods: {
    showDetails() {
      this.$emit('showDetails', this.person)
    },
    
    getAvatarEmoji() {
      if (!this.person.isAlive) return '💀'
      
      if (this.person.age < 6) {
        return this.person.gender === '男' ? '👶' : '👶'
      } else if (this.person.age < 18) {
        return this.person.gender === '男' ? '🧒' : '👧'
      } else if (this.person.age < 60) {
        return this.person.gender === '男' ? '👨' : '👩'
      } else {
        return this.person.gender === '男' ? '👴' : '👵'
      }
    }
  }
}
</script>

<style scoped>
.person-card {
  position: relative;
  width: 200rpx;
  height: 320rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16rpx;
  padding: 20rpx;
  margin: 10rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: all 0.3s ease;
  border: 2rpx solid transparent;
}

.person-card:hover {
  transform: translateY(-4rpx);
  box-shadow: 0 12rpx 32rpx rgba(0, 0, 0, 0.2);
}

.person-card.dead {
  background: linear-gradient(135deg, #555 0%, #333 100%);
  opacity: 0.7;
}

.age-tag {
  position: absolute;
  top: 8rpx;
  left: 8rpx;
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  padding: 4rpx 8rpx;
  border-radius: 8rpx;
  font-size: 20rpx;
  font-weight: bold;
}

.gender-tag {
  position: absolute;
  top: 8rpx;
  right: 8rpx;
  padding: 4rpx 8rpx;
  border-radius: 8rpx;
  font-size: 20rpx;
  font-weight: bold;
  color: white;
}

.gender-tag.male {
  background: #4A90E2;
}

.gender-tag.female {
  background: #E24A90;
}

.avatar {
  margin-top: 40rpx;
  margin-bottom: 16rpx;
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
}

.avatar-text {
  font-size: 48rpx;
}

.name {
  color: white;
  font-size: 28rpx;
  font-weight: bold;
  margin-bottom: 8rpx;
  text-align: center;
}

.occupation {
  color: rgba(255, 255, 255, 0.9);
  font-size: 20rpx;
  text-align: center;
  margin-bottom: 4rpx;
  background: rgba(255, 255, 255, 0.1);
  padding: 2rpx 6rpx;
  border-radius: 6rpx;
}

.education {
  color: rgba(255, 255, 255, 0.8);
  font-size: 18rpx;
  text-align: center;
  margin-bottom: 2rpx;
  background: rgba(0, 150, 255, 0.2);
  padding: 2rpx 6rpx;
  border-radius: 6rpx;
}

.major {
  color: rgba(255, 255, 255, 0.7);
  font-size: 16rpx;
  text-align: center;
  margin-bottom: 4rpx;
  background: rgba(0, 200, 100, 0.2);
  padding: 2rpx 4rpx;
  border-radius: 4rpx;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.economic-contribution {
  font-size: 22rpx;
  font-weight: 500;
  text-align: center;
  padding: 6rpx 12rpx;
  border-radius: 12rpx;
  background: rgba(255, 255, 255, 0.1);
}

.economic-contribution.positive {
  color: #4CAF50;
}

.economic-contribution.negative {
  color: #F44336;
}

.life-indicator {
  position: absolute;
  bottom: 8rpx;
  right: 8rpx;
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
}

.life-indicator.alive {
  background: #4CAF50;
  box-shadow: 0 0 8rpx #4CAF50;
}

.life-indicator.dead {
  background: #F44336;
}
</style>