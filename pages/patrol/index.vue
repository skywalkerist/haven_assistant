<template>
	<view class="page-container">
		<!-- 1. 自定义导航栏 -->
		<view class="custom-nav-bar">
			<text class="back-arrow" @click="goBack">&lt;</text>
			<text class="nav-title">安防巡逻</text>
		</view>

		<!-- 2. 路线选择 -->
		<view class="route-selection-section">
			<text class="section-title">路线选择</text>
			<view class="route-grid">
				<view class="route-card" v-for="(route, index) in routes" :key="index" @click="renameRoute(index)">
					<view class="route-info">
						<text class="route-name">{{ route.name }}</text>
						<text class="route-description">{{ route.description }}</text>
					</view>
					<view class="route-actions">
						<button class="start-button" @click.stop="startPatrol(index)">开始</button>
						<button class="delete-button" @click.stop="deleteRoute(index)">删除</button>
					</view>
				</view>
			</view>
		</view>

		<!-- 3. 添加路线按钮 -->
		<view class="add-route-button-container">
			<button class="add-route-button" @click="addRoute">添加路线</button>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				routes: []
			};
		},
		onLoad() {
			this.loadRoutes();
			this.updateRoutesHandler = () => {
				this.loadRoutes();
			};
		},
		onShow() {
			// 在页面每次显示时重新加载数据并监听事件
			this.loadRoutes();
			uni.$on('routes-updated', this.updateRoutesHandler);
		},
		onHide() {
			// 在页面隐藏时移除监听，避免重复注册
			uni.$off('routes-updated', this.updateRoutesHandler);
		},
		onUnload() {
			// 在页面卸载时彻底移除监听器
			uni.$off('routes-updated', this.updateRoutesHandler);
		},
		methods: {
			goBack() {
				uni.navigateBack();
			},
			loadRoutes() {
				console.log('--- [INDEX.VUE] LOAD ROUTES TRIGGERED ---');
				const storedRoutes = uni.getStorageSync('patrol_routes');
				console.log('--- [INDEX.VUE] LOADED FROM STORAGE ---');
				console.log(JSON.stringify(storedRoutes, null, 2));
				if (storedRoutes && storedRoutes.length > 0) {
					this.routes = storedRoutes;
				} else {
					// Default data if storage is empty
					this.routes = [{
						name: '路线1',
						description: '住宿区专线',
						points: []
					}];
					this.saveRoutes(); // Add this line to persist the default route
				}
			},
			saveRoutes() {
				uni.setStorageSync('patrol_routes', this.routes);
			},
			startPatrol(index) {
				const route = this.routes[index];
				uni.showToast({
					title: `${route.name} 已开始巡逻`,
					icon: 'none'
				});
			},
			addRoute() {
				uni.navigateTo({
					url: '/pages/patrol/add'
				});
			},
			renameRoute(index) {
				uni.showModal({
					title: '重命名路线',
					content: this.routes[index].name,
					editable: true,
					success: (res) => {
						if (res.confirm && res.content) {
							this.routes[index].name = res.content;
							this.saveRoutes();
							uni.showToast({
								title: '重命名成功',
								icon: 'success'
							});
						}
					}
				});
			},
			deleteRoute(index) {
				uni.showModal({
					title: '确认删除',
					content: `您确定要删除路线 "${this.routes[index].name}" 吗？`,
					success: (res) => {
						if (res.confirm) {
							this.routes.splice(index, 1);
							this.saveRoutes();
							uni.showToast({
								title: '删除成功',
								icon: 'success'
							});
						}
					}
				});
			}
		}
	}
</script>

<style>
	.page-container {
		display: flex;
		flex-direction: column;
		background: linear-gradient(to bottom, #49C6A7, #F4F4F4 50%);
		height: 100vh;
		color: #333;
	}

	/* 自定义导航栏 */
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
		top: 50%;
		transform: translateY(-50%);
		font-size: 48rpx;
		font-weight: bold;
		color: #000000;
	}
	.nav-title {
		font-size: 36rpx;
		font-weight: bold;
		color: #000000;
	}

	/* 路线选择 */
	.route-selection-section {
		padding: 40rpx;
		flex: 1;
		overflow-y: auto;
	}
	.section-title {
		font-size: 36rpx;
		font-weight: bold;
		margin-bottom: 30rpx;
		color: #000000;
	}
	.route-grid {
		display: flex;
		flex-direction: column;
		gap: 30rpx;
	}
	.route-card {
		background-color: #FFFFFF;
		border-radius: 20rpx;
		padding: 30rpx;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	.route-info {
		display: flex;
		flex-direction: column;
		flex: 1;
	}
	.route-actions {
		display: flex;
		flex-direction: row;
		align-items: center;
		gap: 20rpx;
	}
	.delete-button {
		background-color: #FF4D4F;
		color: #FFFFFF;
		font-size: 24rpx;
		padding: 5rpx 20rpx;
		border-radius: 30rpx;
		line-height: 1.5;
		border: none;
	}
	.route-name {
		font-size: 32rpx;
		font-weight: bold;
	}
	.route-description {
		font-size: 24rpx;
		color: #999;
		margin-top: 5rpx;
	}
	.start-button {
		background-color: #28a745;
		color: #FFFFFF;
		font-size: 28rpx;
		padding: 10rpx 30rpx;
		border-radius: 30rpx;
		line-height: 1.5;
		border: none;
	}

	/* 添加路线按钮 */
	.add-route-button-container {
		padding: 40rpx;
		background-color: #F4F4F4;
	}
	.add-route-button {
		background-color: #28a745;
		color: #FFFFFF;
		font-size: 36rpx;
		font-weight: bold;
		border-radius: 50rpx;
		height: 100rpx;
		line-height: 100rpx;
		text-align: center;
	}
</style>