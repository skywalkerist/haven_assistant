<template>
	<view class="page-container">
		<!-- 1. 自定义导航栏 -->
		<view class="custom-nav-bar">
			<text class="back-arrow" @click="goBack">&lt;</text>
			<text class="nav-title">添加路线</text>
		</view>

		<!-- 2. 新增路线区域 -->
		<view class="new-route-section">
			<text class="section-title">新增路线</text>
			<view v-if="selectedPoints.length === 0" class="empty-prompt">
				请至少添加两个点位
			</view>
			<view v-else class="selected-points-container">
				<view class="selected-point-card" v-for="(point, index) in selectedPoints" :key="index">
					<text class="point-order">{{ index + 1 }}</text>
					<view class="point-info">
						<text class="point-name">{{ point.name }}</text>
						<text class="point-location">{{ point.location }}</text>
					</view>
					<button class="delete-button" @click="removePointFromRoute(index)">删除</button>
				</view>
			</view>
		</view>

		<!-- 3. 点位选择区域 -->
		<view class="point-selection-section">
			<text class="section-title">点位选择</text>
			<view class="available-points-grid">
				<view class="available-point-card" v-for="(point, index) in availablePoints" :key="index">
					<image src="/static/icon_positon.png" class="point-icon" mode="aspectFit"></image>
					<view class="point-info">
						<text class="point-name">{{ point.name }}</text>
						<text class="point-location">{{ point.location }}</text>
					</view>
					<button class="add-button" @click="addPointToRoute(index)">添加</button>
				</view>
			</view>
		</view>

		<!-- 4. 确认按钮 -->
		<view class="confirm-button-container">
			<button class="confirm-button" :disabled="selectedPoints.length < 2" @click="confirmAddRoute">确定添加</button>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				availablePoints: [],
				selectedPoints: []
			};
		},
		onLoad() {
			// 加载所有可用点位，不再过滤
			this.availablePoints = uni.getStorageSync('points') || [];
		},
		methods: {
			goBack() {
				uni.navigateBack();
			},
			addPointToRoute(index) {
				const point = this.availablePoints.splice(index, 1)[0];
				this.selectedPoints.push(point);
			},
			removePointFromRoute(index) {
				const point = this.selectedPoints.splice(index, 1)[0];
				this.availablePoints.push(point);
			},
			confirmAddRoute() {
				if (this.selectedPoints.length < 2) {
					uni.showToast({
						title: '请至少选择两个点位',
						icon: 'none'
					});
					return;
				}

				const routes = uni.getStorageSync('patrol_routes') || [];

				// 检查是否存在完全相同的路线
				const isDuplicate = routes.some(route => {
					if (route.points.length !== this.selectedPoints.length) {
						return false;
					}
					for (let i = 0; i < route.points.length; i++) {
						if (route.points[i].name !== this.selectedPoints[i].name) {
							return false;
						}
					}
					return true;
				});

				if (isDuplicate) {
					uni.showToast({
						title: '该路线已存在',
						icon: 'none'
					});
					return;
				}

				const newRoute = {
					name: `路线 ${routes.length + 1}`,
					description: '自定义路线',
					points: this.selectedPoints
				};
				routes.push(newRoute);

				uni.setStorageSync('patrol_routes', routes);
				uni.$emit('routes-updated');

				uni.showToast({
					title: '路线添加成功',
					icon: 'success'
				});

				setTimeout(() => {
					uni.navigateBack();
				}, 1500);
			}
		}
	}
</script>

<style>
	.page-container {
		display: flex;
		flex-direction: column;
		background: linear-gradient(to bottom, #49C6A7, #F4F4F4 30%);
		height: 100vh;
	}
	.custom-nav-bar {
		position: relative;
		display: flex;
		justify-content: center;
		align-items: center;
		height: 90rpx;
		padding-top: var(--status-bar-height);
	}
	.back-arrow {
		position: absolute;
		left: 40rpx;
		font-size: 48rpx;
		font-weight: bold;
		color: #000000;
	}
	.nav-title {
		font-size: 36rpx;
		font-weight: bold;
		color: #000000;
	}
	.section-title {
		font-size: 36rpx;
		font-weight: bold;
		margin-bottom: 30rpx;
		color: #000000;
	}
	.new-route-section {
		padding: 20rpx 40rpx;
	}
	.empty-prompt {
		color: #666;
		text-align: center;
		padding: 40rpx 0;
	}
	.selected-points-container {
		display: flex;
		flex-wrap: wrap;
		gap: 20rpx;
	}
	.selected-point-card {
		background-color: #FFF;
		border-radius: 20rpx;
		padding: 20rpx;
		display: flex;
		align-items: center;
		gap: 20rpx;
	}
	.point-order {
		font-size: 60rpx;
		font-weight: bold;
		color: #E0E0E0;
	}
	.point-info {
		display: flex;
		flex-direction: column;
	}
	.point-name {
		font-size: 30rpx;
		font-weight: bold;
	}
	.point-location {
		font-size: 24rpx;
		color: #999;
	}
	.delete-button {
		background-color: #FF4D4F;
		color: #FFF;
		font-size: 24rpx;
		padding: 5rpx 15rpx;
		border-radius: 20rpx;
		border: none;
	}
	.point-selection-section {
		flex: 1;
		background-color: #F4F4F4;
		border-top-left-radius: 40rpx;
		border-top-right-radius: 40rpx;
		padding: 40rpx;
		margin-top: 20rpx;
		overflow-y: auto;
	}
	.available-points-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 30rpx;
	}
	.available-point-card {
		background-color: #FFF;
		border-radius: 20rpx;
		padding: 20rpx;
		display: flex;
		align-items: center;
		gap: 20rpx;
	}
	.point-icon {
		width: 60rpx;
		height: 60rpx;
	}
	.add-button {
		background-color: #28a745;
		color: #FFF;
		font-size: 24rpx;
		padding: 5rpx 15rpx;
		border-radius: 20rpx;
		border: none;
	}
	.confirm-button-container {
		padding: 20rpx 40rpx;
		background-color: #F4F4F4;
	}
	.confirm-button {
		background-color: #28a745;
		color: #FFF;
		font-size: 36rpx;
		border-radius: 50rpx;
		height: 100rpx;
		line-height: 100rpx;
	}
	.confirm-button[disabled] {
		background-color: #A9D4B5;
		color: #E0E0E0;
	}
</style>