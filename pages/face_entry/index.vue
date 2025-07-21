<template>
	<view class="page-container">
		<view class="content-wrapper">
			<text class="title">请面对摄像头，输入人员姓名</text>
			<input class="name-input" type="text" v-model="name" placeholder="在此输入姓名" />
			<button class="action-button" @click="startRegistration">开始注册人脸</button>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				name: ''
			};
		},
		methods: {
			startRegistration() {
				if (!this.name.trim()) {
					uni.showToast({
						title: '请输入名字',
						icon: 'none'
					});
					return;
				}
				// Placeholder for actual face registration logic
				uni.showToast({
					title: `已为 ${this.name} 开始注册`,
					icon: 'success'
				});
			}
		}
	}
</script>

<style>
	.page-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding-top: 80rpx;
		background-color: #f8f8f8;
		min-height: 100vh;
	}
	.content-wrapper {
		width: 80%;
		display: flex;
		flex-direction: column;
		align-items: center;
	}
	.title {
		font-size: 36rpx;
		font-weight: bold;
		margin-bottom: 60rpx;
		text-align: center;
	}
	.name-input {
		width: 100%;
		height: 100rpx;
		background-color: #FFFFFF;
		border-radius: 20rpx;
		padding: 0 40rpx;
		font-size: 32rpx;
		text-align: center;
		margin-bottom: 60rpx;
		box-shadow: 0 2rpx 6rpx rgba(0,0,0,0.05);
	}
	.action-button {
		width: 100%;
		height: 100rpx;
		line-height: 100rpx;
		font-size: 34rpx;
		color: #FFFFFF;
		background-color: #007aff;
		border-radius: 50rpx;
	}
</style>
