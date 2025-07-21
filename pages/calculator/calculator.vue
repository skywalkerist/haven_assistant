<template>
  <view class="container">
    <view class="calculator">
      <input class="input-field" type="number" v-model.number="numA" placeholder="输入第一个数字" />
      <text class="plus-sign">+</text>
      <input class="input-field" type="number" v-model.number="numB" placeholder="输入第二个数字" />
      <button class="calculate-button" @click="calculateSum">计算</button>
      <view class="result-area" v-if="sum !== null">
        <text class="result-text">结果: {{ sum }}</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      numA: null,
      numB: null,
      sum: null
    };
  },
  methods: {
    calculateSum() {
      if (typeof this.numA !== 'number' || typeof this.numB !== 'number') {
        uni.showToast({
          title: '请输入有效的数字',
          icon: 'none'
        });
        return;
      }

      uni.showLoading({
        title: '计算中...'
      });

      uniCloud.callFunction({
        name: 'add',
        data: {
          a: this.numA,
          b: this.numB
        }
      }).then(res => {
        uni.hideLoading();
        if (res.result && res.result.success) {
          this.sum = res.result.sum;
        } else {
          throw new Error(res.result.message || '计算失败');
        }
      }).catch(err => {
        uni.hideLoading();
        uni.showToast({
          title: err.message || '计算失败',
          icon: 'none'
        });
      });
    }
  }
};
</script>

<style>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f0f0;
}
.calculator {
  width: 80%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}
.input-field {
  width: 100%;
  height: 40px;
  padding: 0 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  text-align: center;
}
.plus-sign {
  font-size: 24px;
  font-weight: bold;
}
.calculate-button {
  width: 100%;
  height: 45px;
  background-color: #007aff;
  color: white;
  border: none;
  border-radius: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
}
.result-area {
  margin-top: 20px;
  padding: 20px;
  background-color: #fff;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.result-text {
  font-size: 20px;
  font-weight: bold;
}
</style>
