<template>
	<view class="container">
		<view class="button-list">
			<view class="button-wrapper">
				<button class="styled-button" @click="goToVoiceManagement">声音音色管理</button>
			</view>
			<view class="button-wrapper">
				<button class="styled-button" @click="goToVoiceCloning">语音个性化模仿</button>
			</view>
			<view class="button-wrapper">
				<button class="styled-button" @click="goToFaceEntry">人脸系统录入</button>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		methods: {
			goToVoiceCloning() {
				uni.navigateTo({
					url: '/pages/voice_cloning/index'
				});
			},
			goToFaceEntry() {
				uni.navigateTo({
					url: '/pages/face_entry/index'
				});
			},
			goToVoiceManagement() {
				uni.navigateTo({
					url: '/pages/voice_management/index'
				});
			}
		}
	}
</script>

<style>
	.container {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding-top: 80rpx;
		background-color: #f8f8f8;
		min-height: 100vh;
	}
	.button-list {
		width: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
	}
	.button-wrapper {
		width: 80%;
		margin-bottom: 40rpx;
	}
	.styled-button {
		width: 100%;
		height: 120rpx;
		line-height: 120rpx;
		font-size: 34rpx;
		color: #333;
		background-color: #FFFFFF;
		border-radius: 20rpx;
		box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
		text-align: center;
	}
</style>
