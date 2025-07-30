<template>
	<view class="page-container">
		<view class="scroll-content">
			<!-- 1. 自定义导航栏 -->
			<view class="custom-nav-bar">
				<text class="nav-title">人员</text>
			</view>

			<!-- 2. 关怀通知 -->
			<view class="care-section">
				<text class="care-title">关怀通知</text>
				<view class="notification-cards">
					<view class="notification-card" v-for="item in careNotifications" :key="item.id">
						<view class="card-header">
							<image :src="item.avatar" class="avatar"></image>
							<view class="info">
								<text class="name">{{ item.name }}</text>
								<text class="details">{{ item.gender }} {{ item.age }}岁</text>
							</view>
						</view>
						<text class="message">{{ item.message }}</text>
						<button class="ack-button" @click="acknowledgeNotification(item.id)">我已知晓</button>
					</view>
				</view>
			</view>

			<!-- 3. 人员档案 -->
			<view class="personnel-section">
				<view class="personnel-header">
					<text class="personnel-title">人员档案</text>
					<view class="header-actions">
						<button class="face-register-button" @click="goToFaceEntry">人脸注册</button>
						<view class="search-bar">
							<input type="text" placeholder="搜索..." class="search-input" v-model="searchText" @input="handleSearch" />
						</view>
					</view>
				</view>
				<view class="personnel-grid">
					<view class="personnel-card" v-for="person in filteredPersonnelList" :key="person.id" @click="handlePersonClick(person)">
						<image :src="person.avatar" class="person-avatar"></image>
						<view class="person-info">
							<text class="person-name">{{ person.name }}</text>
							<text class="person-details">{{ person.gender }} {{ person.age }}岁</text>
						</view>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				searchText: '',
				careNotifications: [{
					id: 1,
					avatar: '/static/icon_user.png',
					name: '刘秀丽',
					gender: '女',
					age: 73,
					message: '今天是刘秀丽奶奶的73周岁生日，祝她生日快乐吧'
				}, {
					id: 2,
					avatar: '/static/icon_user.png',
					name: '李善良',
					gender: '男',
					age: 81,
					message: '李爷爷最近经常提起小女儿，提醒家人常来看看吧'
				}],
				personnelList: [
					{ id: 1, avatar: '/static/icon_user.png', name: '刘秀丽', gender: '女', age: 73 },
					{ id: 2, avatar: '/static/icon_user.png', name: '李善良', gender: '男', age: 81 },
					{ id: 3, avatar: '/static/icon_user.png', name: '王大爷', gender: '男', age: 75 },
					{ id: 4, avatar: '/static/icon_user.png', name: '张奶奶', gender: '女', age: 68 },
					{ id: 5, avatar: '/static/icon_user.png', name: '赵叔叔', gender: '男', age: 72 },
					{ id: 6, avatar: '/static/icon_user.png', name: '孙阿姨', gender: '女', age: 69 },
					{ id: 7, avatar: '/static/icon_user.png', name: '陈爷爷', gender: '男', age: 78 },
					{ id: 8, avatar: '/static/icon_user.png', name: '林奶奶', gender: '女', age: 71 },
				]
			};
		},
		computed: {
			filteredPersonnelList() {
				if (!this.searchText) {
					return this.personnelList;
				}
				return this.personnelList.filter(person => 
					person.name.includes(this.searchText)
				);
			}
		},
		onShow() {
			// 每次显示页面时可以加载最新数据
			this.loadPersonnelData();
		},
		methods: {
			goToFaceEntry() {
				uni.navigateTo({
					url: '/pages/face_entry/index'
				});
			},
			
			loadPersonnelData() {
				// 这里可以从云端或本地存储加载人员数据
				// 保留原有的后端交互逻辑
				console.log('加载人员数据');
			},
			handlePersonClick(person) {
				uni.showModal({
					title: '人员详情',
					content: `姓名: ${person.name}\n性别: ${person.gender}\n年龄: ${person.age}岁`,
					showCancel: false
				});
			},
			acknowledgeNotification(notificationId) {
				// 处理"我已知晓"按钮点击
				this.careNotifications = this.careNotifications.filter(item => item.id !== notificationId);
				uni.showToast({
					title: '已确认',
					icon: 'success'
				});
			},
			handleSearch() {
				// 搜索功能，通过计算属性filteredPersonnelList实现
				console.log('搜索:', this.searchText);
			}
		}
	}
</script>

<style lang="scss">
	.page-container {
		display: flex;
		flex-direction: column;
		height: 100vh;
		/* background is now handled globally in App.vue */
	}

	.scroll-content {
		flex: 1;
		overflow-y: auto;
		padding-bottom: 30rpx; /* 适配原生TabBar */
	}

	/* 自定义导航栏 */
	.custom-nav-bar {
		display: flex;
		align-items: flex-end;
		padding: 20rpx 40rpx;
		height: 120rpx;
		padding-top: var(--status-bar-height);
		background-color: transparent;
	}

	.nav-title {
		font-size: 36rpx;
		font-weight: bold;
		color: #000000;
	}

	/* 关怀通知 */
	.care-section {
		background: linear-gradient(180deg, #63D8A2 0%, #90E5B4 100%);
		padding: 30rpx 40rpx;
		border-bottom-left-radius: 40rpx;
		border-bottom-right-radius: 40rpx;
	}

	.care-title {
		font-size: 40rpx;
		font-weight: bold;
		color: #FFFFFF;
		margin-bottom: 30rpx;
		display: block;
	}

	.notification-cards {
		display: flex;
		justify-content: space-between;
		gap: 20rpx;
	}

	.notification-card {
		background-color: rgba(255, 255, 255, 0.8);
		border-radius: 20rpx;
		padding: 20rpx;
		width: 48%;
		box-sizing: border-box;
	}

	.card-header {
		display: flex;
		align-items: center;
		margin-bottom: 15rpx;
	}

	.avatar {
		width: 80rpx;
		height: 80rpx;
		border-radius: 50%;
		margin-right: 20rpx;
	}

	.info {
		display: flex;
		flex-direction: column;
	}

	.name {
		font-size: 30rpx;
		font-weight: bold;
	}

	.details {
		font-size: 24rpx;
		color: #666;
	}

	.message {
		font-size: 26rpx;
		color: #333;
		line-height: 1.4;
		display: block;
		margin-bottom: 20rpx;
	}

	.ack-button {
		background-color: #28a745;
		color: #FFFFFF;
		font-size: 24rpx;
		border-radius: 30rpx;
		padding: 10rpx 0;
		text-align: center;
		width: 80%;
		margin: 0 auto;
	}

	/* 人员档案 */
	.personnel-section {
		padding: 40rpx;
	}

	.personnel-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 30rpx;
	}

	.header-actions {
		display: flex;
		align-items: center;
		gap: 20rpx;
	}

	.face-register-button {
		background-color: #28a745;
		color: #FFFFFF;
		font-size: 26rpx;
		font-weight: bold;
		border-radius: 30rpx;
		padding: 12rpx 24rpx;
		border: none;
		box-shadow: 0 2rpx 8rpx rgba(40, 167, 69, 0.2);
		transition: all 0.2s ease-in-out;
		white-space: nowrap;
	}

	.face-register-button:active {
		transform: scale(0.96);
		box-shadow: 0 1rpx 4rpx rgba(40, 167, 69, 0.3);
	}

	.personnel-title {
		font-size: 36rpx;
		font-weight: bold;
	}

	.search-bar {
		position: relative;
		width: 200rpx;
		flex-shrink: 0;
	}

	.search-input {
		background-color: #FFFFFF;
		border-radius: 30rpx;
		padding: 10rpx 20rpx;
		font-size: 26rpx;
		text-align: center;
	}

	.personnel-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 25rpx;
	}

	.personnel-card {
		background-color: #FFFFFF;
		border-radius: 20rpx;
		padding: 20rpx;
		display: flex;
		align-items: center;
	}

	.person-avatar {
		width: 90rpx;
		height: 90rpx;
		border-radius: 50%;
		margin-right: 20rpx;
	}

	.person-info {
		display: flex;
		flex-direction: column;
	}

	.person-name {
		font-size: 30rpx;
		font-weight: bold;
	}

	.person-details {
		font-size: 24rpx;
		color: #666;
	}
</style>