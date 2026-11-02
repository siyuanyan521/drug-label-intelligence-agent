# CDE已验证技术经验

这些是历史观察，使用前验证当前页面，不能当永久API契约。

- Playwright CLI无头Edge曾返回HTTP400，有界面Edge能正常访问。先正常有界面访问，遇到验证提示记录，不改指纹或关闭证书校验。Skill不授权安装工具；有Playwright skill时遵循其CLI工作流。
- “上市药品信息”药品框曾为#drugname2；页面包含多个隐藏同名框，精确定位可见栏目。查询按钮成功不等于取得结果。
- 实际观察列表POST /main/xxgk/getPostMarketList，表单pageSize/pageNum/acceptid/drugname/company，响应data.records/total/pages；URL还有动态参数。监听点击产生、postData包含当前编码药名的response，避免捕获栏目初始请求。未经验证不能直接重放、猜动态参数或脱离会话批调。
- 正常分页/每页50条控件可用于取全；不要只查第一页。等待对应结果DOM更新，避免双击旧行。
- 双击受理号会打开popup；详情页曾使用/main/xxgk/postmarketpage?acceptidCODE=...。保留真实返回标识；未打开的链接注明未验证。
- 附件有时href为javascript:;，点击通过浏览器download事件取得data:application/octet-stream;base64文件。先监听download再点击，saveAs保存；不输出完整data URL/base64。只记录来源详情页、附件名称、下载机制、哈希，不把临时data URL当稳定下载链接。
- 网络可用时用CLI requests/request/request-body/response-body分析真实请求。run-code复杂脚本在Windows用--filename，避免命令行引号破坏。单药/单条先保存原始响应，即便下一条详情超时也能续跑。
