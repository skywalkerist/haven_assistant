<script>
	export default {
		onLaunch: function() {
			console.log('App Launch')
			// 每次启动应用时清理过期的云端任务
			this.cleanupExpiredTasks()
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		},
		methods: {
			async cleanupExpiredTasks() {
				try {
					console.log('开始清理过期云端任务...')
					const result = await uniCloud.callFunction({
						name: 'cleanupExpiredCommands'
					})
					
					if (result.result.success) {
						console.log(`清理完成，清理了 ${result.result.cleaned_count} 个过期任务`)
					} else {
						console.error('清理过期任务失败:', result.result.message)
					}
				} catch (error) {
					console.error('调用清理云函数失败:', error)
				}
			}
		}
	}
</script>

<style>
	/*每个页面公共css */
	page {
		background-image: url('/static/background.png');
		background-size: cover;
		background-repeat: no-repeat;
		background-position: center;
		background-attachment: fixed; /* 防止背景随滚动而移动 */
	}
</style>
