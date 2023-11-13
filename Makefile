check:
	# 查看无用的依赖
	@pip-autoremove -l
req:
	# 生成配置依赖，变更后需要同步到setup.py的install_requires中
	@pip freeze -l >requirements.txt
