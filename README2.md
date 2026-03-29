需要知道的文件修改：
scripts下包含了自动化脚本

团队主页通过team.liqud和person_detail.liquid实现更改，基本信息存放在people.md其他信息存放在_pages/[lang]/people对应文件夹下（包含头像描述）

managetool下包含管理脚本（不一定能使用）

汉化通过修改页面以及string.yml
注意构建中英文页面时按照正常al-folio形式构建即可不要踩坑了，team.liqud和person_detail.liquid中区分中英文实际上不是一个特别好的做法，如果对于页面上的固定文字可以区分中英文编写，但是对于动态内容，最好是通过读取md文件内容呈现。

publication界面的序号通过更改publication.md以及main.scss实现

github仓库通过Edit the `_data/repositories.yml` and change the `github_users` and `github_repos` lists to include your own GitHub profile and repositories.

在导航栏上隐藏/显示项目通过更改_pages下的front matter实现。

新闻通过在news下增加md文件即可，新闻模板的{}自动填充字段请看news.csv但year，month，date字段只能通过{time}统一调用

想要精选文章在papers.bib相应文章加上selected={true}字段

想要增加活动，在_events文件夹下新增md文件

所有可能用到的图片都在assets/img/相应名称下存放

没有提及的东西基本上在_pages文件夹下修改

最后注意，所有要构建页面的md文件一定得是utf-8编码！！！不能with BOM！！！
