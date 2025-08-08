<template>
  <view class="family-tree">
    <!-- 第一代 -->
    <view class="generation" v-for="(generation, genIndex) in generations" :key="genIndex">
      <view class="generation-title">第{{ genIndex + 1 }}代</view>
      
      <!-- 同一代的夫妻组 -->
      <view class="couples-row">
        <view class="couple-group" v-for="(couple, coupleIndex) in generation" :key="coupleIndex">
          <!-- 夫妻卡片 -->
          <view class="couple-cards">
            <PersonCard 
              :person="couple.husband || couple.single" 
              @showDetails="$emit('showDetails', $event)"
            />
            <PersonCard 
              v-if="couple.wife"
              :person="couple.wife" 
              @showDetails="$emit('showDetails', $event)"
            />
          </view>
          
          <!-- 夫妻连线 -->
          <view class="couple-line" v-if="couple.wife"></view>
          
          <!-- 指向子女的连线 -->
          <view class="children-line" v-if="couple.children && couple.children.length > 0"></view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import PersonCard from './PersonCard.vue'

export default {
  name: 'FamilyTree',
  components: {
    PersonCard
  },
  props: {
    persons: {
      type: Array,
      default: () => []
    }
  },
  emits: ['showDetails'],
  computed: {
    generations() {
      // 按代数组织人物
      const genMap = new Map()
      
      // 先找出所有没有父母的人（第一代）
      const firstGen = this.persons.filter(person => 
        !person.parents || person.parents.length === 0
      )
      
      // 组织第一代的夫妻关系
      const firstGenCouples = this.organizeCouples(firstGen)
      if (firstGenCouples.length > 0) {
        genMap.set(0, firstGenCouples)
      }
      
      // 找出后续代数
      let currentGen = 1
      let processed = new Set(firstGen.map(p => p.id))
      
      while (processed.size < this.persons.length) {
        const thisGenPeople = this.persons.filter(person => 
          !processed.has(person.id) && 
          person.parents && 
          person.parents.every(parent => processed.has(parent.id))
        )
        
        if (thisGenPeople.length === 0) break
        
        const thisGenCouples = this.organizeCouples(thisGenPeople)
        if (thisGenCouples.length > 0) {
          genMap.set(currentGen, thisGenCouples)
        }
        
        thisGenPeople.forEach(p => processed.add(p.id))
        currentGen++
      }
      
      // 转换为数组并为每个夫妻组添加子女信息
      const result = []
      for (let [genIndex, couples] of genMap.entries()) {
        couples.forEach(couple => {
          const primaryPerson = couple.husband || couple.single
          if (primaryPerson && primaryPerson.children) {
            couple.children = primaryPerson.children
          }
        })
        result.push(couples)
      }
      
      return result
    }
  },
  methods: {
    organizeCouples(people) {
      const couples = []
      const processed = new Set()
      
      for (const person of people) {
        if (processed.has(person.id)) continue
        
        if (person.partner && this.persons.find(p => p.id === person.partner.id)) {
          // 有配偶且配偶也在persons数组中
          couples.push({
            husband: person.gender === '男' ? person : person.partner,
            wife: person.gender === '女' ? person : person.partner
          })
          processed.add(person.id)
          processed.add(person.partner.id)
        } else {
          // 单身
          couples.push({
            single: person
          })
          processed.add(person.id)
        }
      }
      
      return couples
    }
  }
}
</script>

<style scoped>
.family-tree {
  padding: 20rpx;
  display: flex;
  flex-direction: column;
  gap: 40rpx;
}

.generation {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.generation-title {
  font-size: 32rpx;
  font-weight: bold;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 20rpx;
  padding: 10rpx 20rpx;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16rpx;
}

.couples-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 40rpx;
}

.couple-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.couple-cards {
  display: flex;
  gap: 20rpx;
  margin-bottom: 20rpx;
}

.couple-line {
  width: 60rpx;
  height: 4rpx;
  background: rgba(255, 255, 255, 0.6);
  position: absolute;
  top: 160rpx;
  left: 50%;
  transform: translateX(-50%);
}

.children-line {
  width: 4rpx;
  height: 30rpx;
  background: rgba(255, 255, 255, 0.6);
  position: absolute;
  bottom: -30rpx;
  left: 50%;
  transform: translateX(-50%);
}
</style>