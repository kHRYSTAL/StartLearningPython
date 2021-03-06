- 博客系统
- CMDB 资产管理系统 如何去实现

>CMDB 即资产数据库

* 资产采集 放到资产数据库
* 将采集的数据通过api放到数据库, 认证
* 统计图, 可视化管理

        1. 需要完成资产的自动搜集, 且变更时有记录可寻
        2. 提供API URL (返回json, 支持jsonp)

        1. 资产自动收集
            - paramiko ansible fabric api与服务器之间通过paramiko的中控服务器交互
                通过API获取主机名, 利用paramiko链接服务获取数据, 解析成字典
                原理 ssh
                优点: 无依赖
                缺点: 慢

            - saltstack api与服务器之间通过saltstack master中转
                cmd: salt [hostname] cmd.   run [cmd]
                cmd: salt * cmd.run [cmd]
                原理 zeromq
                优点: 无依赖
                缺点: 相对ssh快 相对agent慢

            - puppet(主流)
                优点: 简单 且不需要定时任务 原生支持report报表
                缺点: ruby代码实现
                知识概要:
                    master: 直接安装 中控
                    slave: 服务器客户端 存在唯一标识 certname
                    配置文件: 编写模版 放置到master上 通知服务器客户端批量执行
                        如果不写命令修改时间, 默认每30分钟执行一次 master和slave进行一次连接

                    - report报表 每30分钟交互一次(包含许多获取远程机器基本信息的命令) 会生成一个yml文件 保存远程机器的基本信息
                        配置文件 report: cmdb.rb # 每30分钟交互时, 会执行指定目录下的cmdb.rb文件中的process函数

                        puppet中默认自带了5个report，放置在【/usr/lib/ruby/site_ruby/1.8/puppet/reports/】路径下。如果需要执行某个report，那么就在puppet的master的配置文件中做如下配置：

                            ######################## on master ###################
                            /etc/puppet/puppet.conf
                            [main]
                            reports = store #默认
                            #report = true #默认
                            #pluginsync ＝ true #默认


                            ####################### on client #####################

                            /etc/puppet/puppet.conf
                            [main]
                            #report = true #默认

                            [agent]
                            runinterval = 10
                            server = master.puppet.com
                            certname = c1.puppet.com

                            如上述设置之后，每次执行client和master同步，就会在master服务器的 【/var/lib/puppet/reports】路径下创建一个文件，主动执行：puppet agent  --test


                        - 在 /etc/puppet/modules 目录下创建如下文件结构：

                            modules
                            └── cmdb
                                ├── lib
                                │   └── puppet
                                │       └── reports
                                │           └── cmdb.rb
                                └── manifests
                                    └── init.pp

                            ################ cmdb.rb ################
                            # cmdb.rb
                            require 'puppet'
                            require 'fileutils'
                            require 'puppet/util'

                            SEPARATOR = [Regexp.escape(File::SEPARATOR.to_s), Regexp.escape(File::ALT_SEPARATOR.to_s)].join

                            Puppet::Reports.register_report(:cmdb) do
                              desc "Store server info
                                These files collect quickly -- one every half hour -- so it is a good idea
                                to perform some maintenance on them if you use this report (it's the only
                                default report)."

                              def process
                                certname = self.name
                                now = Time.now.gmtime
                                File.open("/tmp/cmdb.json",'a') do |f|
                                  f.write(certname)
                                  f.write(' | ')
                                  f.write(now)
                                  f.write("\r\n")
                                end

                              end
                            end


                            ################ 配置 ################
                            /etc/puppet/puppet.conf
                            [main]
                            reports = cmdb
                            #report = true #默认
                            #pluginsync ＝ true #默认



                    - cmdb.rb实例 获取远程机器内存信息

                            $LOAD_PATH.unshift(File.dirname(__FILE__)) unless $LOAD_PATH.include?(File.dirname(__FILE__))
                            require "rubygems"
                            require 'pp'
                            require 'json'
                            require 'utils'

                            def dmi_get_ram(cmd)

                                ram_slot = []

                                key_map = {
                                    'Size' => 'capacity',
                                    'Serial Number' => 'sn',
                                    'Type' => 'model',
                                    'Manufacturer' => 'manufactory',
                                    'Locator' => 'slot',
                                }

                                output = Utils.facter_exec(cmd)
                                devices = output.split('Memory Device')

                                devices.each do |d|
                                  next if d.strip.empty?
                                  segment = {}
                                  d.strip.split("\n\t").each do |line|
                                    key, value = line.strip.split(":")
                                    if key_map.has_key?(key.strip)
                                      if key.strip == 'Size'
                                        segment[key_map['Size']] = value.chomp("MB").strip.to_i / 1024.0 # unit GB
                                      else
                                        segment[key_map[key.strip]] =  value ? value.strip : ''
                                      end
                                    end
                                  end

                                  ram_slot.push(segment) unless segment.empty?
                                end

                                return ram_slot

                            end

                            Facter.add("ram") do
                              confine :kernel => "Linux"
                              setcode do

                                ram_slot = []
                                cmd = "dmidecode -q -t 17 2>/dev/null"
                                ram_slot = dmi_get_ram(cmd)

                                JSON.dump(ram_slot)

                              end
                            end


                            Facter.add("ram") do
                              confine :kernel => 'windows'
                              setcode do

                                ram_slot = []

                                if Facter.value(:manufacturer)  =~ /.*HP.*/i
                                  cli = 'C:\cmdb_report\dmidecode.exe'
                                  cmd = "#{cli} -q -t 17"
                                  ram_slot = dmi_get_ram(cmd) if File.exist?(cli)

                                else

                                  require 'facter/util/wmi'
                                  Facter::Util::WMI.execquery("select * from Win32_PhysicalMemory").each do | item |

                                    if item.DeviceLocator
                                      slot = item.DeviceLocator.strip
                                    else
                                      slot = ''
                                    end

                                    if item.PartNumber
                                      model = item.PartNumber.strip
                                    else
                                      model = ''
                                    end

                                    if item.SerialNumber
                                      sn = item.SerialNumber.strip
                                    else
                                      sn = ''
                                    end

                                    if item.Manufacturer
                                      manufactory = item.Manufacturer.strip
                                    else
                                      manufactory = ''
                                    end

                                    ram_slot.push({
                                     'capacity' => item.Capacity.to_i / (1024**3), # unit GB
                                     'slot' => slot,
                                     'model' => model,
                                     'sn' => sn,
                                     'manufactory' => manufactory,
                                   })

                                  end
                                end

                                JSON.dump(ram_slot)

                              end
                            end

            - 基于Agent自己实现CMDB
                    实际上就是在master上 subprocess.getoutput('cmd')# 执行命令获取返回结果 通知远程机器执行cmd
                    缺点: 每台机器都需要部署Agent
                    优点: 快



        =================================================================================
        所有CMDB的本质都是远程机器执行命令获取结果发送到master服务器
        不论原理是ssh, agent(subprocess), zeromq
        =================================================================================
        ===========================执行shell命令获取返回结果================================
        网卡, 硬盘, CPU...

        注意: sn号可以用于作为远程机器的唯一标识, 但是虚拟机的sn号有可能是重复的,
        因此需要改为其他方式作为唯一标识
        =================================================================================






- 组合搜索组件

    * 组合搜索: 在页面上通过一类或多类标签进行过滤数据库查询
    * 难点: 多类标签时 选择一类标签时需要固定其他类的标签选择
    * 优化: html中可以使用自定义函数 优化标签代码 (参考templatetags/custom_tpl_func.py)


        urls.py:

            url(r'^article-(?P<article_type_id>\d+)-(?P<category_id>\d+).html', views.article, name='article')

        views.py:
        def article(request, *args, **kwargs):
            # 获取当前url
            print(request.path_info)
            # 通过url别名反向获取url
            from django.urls import reverse
            url = reverse('article', kwargs=kwargs)
            print(url)

            """
            :param request:
            :param args: 用于接收没有指明key的正则参数
            :param kwargs: 用于接受指明key的正则参数 字典
                {'article_type_id': '1', 'category_id': '0'}
            :return:
            """
            condition = {}  # 空字典为默认值, 相当于没有增加文章查询条件
            for k, v in kwargs.items():
                if v == '0':  # 数据库id是从1开始的, 所以当为0时 认为是查询全部
                    pass
                else:
                    condition[k] = v

            article_type_list = models.ArticleType.objects.all()
            category_list = models.Category.objects.all()
            # 字典解包,当作参数传递
            article_list = models.Article.objects.filter(**condition)
            return render(request, 'article.html', {
                'article_type_list': article_type_list,
                'category_list': category_list,
                'article_list': article_list
            })


- JSONP 跨域请求的 jQuery 实现

        由于浏览器具有同源策略导致
        解决方式
            - 创建script标签
            - src = 远程地址
            - 返回的数据必须是js格式
        缺陷: 只能发GET请求

        Ajax直接请求普通文件存在跨域无权限访问的问题(浏览器会拦截你的请求 防止恶意代码)，甭管你是静态页面、动态网页、web服务、WCF，只要是跨域请求，一律不准；
        不过我们又发现，Web页面上调用js文件时则不受是否跨域的影响（不仅如此，我们还发现凡是拥有"src"这个属性的标签都拥有跨域的能力，比如<script>、<img>、<iframe>）；

        于是可以判断，当前阶段如果想通过纯web端（ActiveX控件、服务端代理、属于未来的HTML5之Websocket等方式不算）跨域访问数据就只有一种可能，那就是在远程服务器上设法把数据装进js格式的文件里，供客户端调用和进一步处理；
        恰巧我们已经知道有一种叫做JSON的纯字符数据格式可以简洁的描述复杂数据，更妙的是JSON还被js原生支持，所以在客户端几乎可以随心所欲的处理这种格式的数据；
        这样子解决方案就呼之欲出了，web客户端通过与调用脚本一模一样的方式，来调用跨域服务器上动态生成的js格式文件（一般以JSON为后缀），显而易见，服务器之所以要动态生成JSON文件，目的就在于把客户端需要的数据装入进去。
        客户端在对JSON文件调用成功之后，也就获得了自己所需的数据，剩下的就是按照自己需求进行处理和展现了，这种获取远程数据的方式看起来非常像AJAX，但其实并不一样。
        为了便于客户端使用数据，逐渐形成了一种非正式传输协议，人们把它称作JSONP，该协议的一个要点就是允许用户传递一个callback参数给服务端，然后服务端返回数据时会将这个callback参数作为函数名来包裹住JSON数据，这样客户端就可以随意定制自己的函数来自动处理返回数据了。

        原理实际上就是在head里快速的增加一端js代码 代码参数为请求的json 然后快速删除
        告诉浏览器 这段伪js可以请求到

        (只能发GET请求)

        参考jsonp.html

- XSS过滤KindEditor传入的html

        1.使用BeautifulSoup 进行标签隐藏和标签内容过滤

        参考util/xss_filter.py

        2. 注意 在列表遍历时 是不能进行插入删除操作的 会直接报错, 因为会影响到计算结果
            因此 在遍历时 应该把列表转换为迭代器,再进行操作 因为迭代器不会计算长度 每次next只会获取下一项
            实际上相当于拷贝了一份列表 然后对原始列表进行操作

        3. 单例模式避免重复请求时重复创建对象处理
                通用操作封装在对象中, 占用的内存大 应该使用单例模式

            第一种方式: 通过getInstance获取单例对象
                class Boo(object):
                    # 静态字段 只属于类 且只存在一份
                    instance = None

                    """ 第一种单例模式 """
                    def __init__(self):
                        pass

                    @classmethod
                    def get_instance(self):
                        """ 类方法 不需要实例化 """
                        if Boo.instance:
                            return Boo.instance
                        else:
                            Boo.instance = Boo()
                            return Boo.instance

                    def process(self):
                        return '123'

            第二种方式: 基于__new__方法 不会改变开发习惯

                class Poo(object):
                    instance = None

                    def __init__(self):
                        pass

                    def __new__(cls, *args, **kwargs):
                        # # 默认实现方法 内部会执行Poo.__init__
                        # obj = object.__new__(cls, *args, **kwargs)
                        # return obj
                        if Poo.instance:
                            return Poo.instance
                        else:
                            Poo.instance = object.__new__(cls, *args, **kwargs)
                            return Poo.instance

- 数据库的事务操作, 事务中, 所有操作执行完 统一提交给数据库

            from django.db import transaction
            with transaction.atomic():
                # 进行事务的数据库操作
                tags = form.cleaned_data.pop('tags')
                content = form.cleaned_data.pop('content')
                print(content)
                content = XSSFilter().process(content)
                form.cleaned_data['blog_id'] = request.session['user_info']['blog__nid']
                obj = models.Article.objects.create(**form.cleaned_data)
                models.ArticleDetail.objects.create(content=content, article=obj)
                tag_list = []
                for tag_id in tags:
                    tag_id = int(tag_id)
                    tag_list.append(models.Article2Tag(article_id=obj.nid, tag_id=tag_id))
                models.Article2Tag.objects.bulk_create(tag_list)

- 筛选条件: 利用数据库内置函数实现筛选
    * 文章分类
    * 标签分类
    * 日期区间 需要将数据库中的毫秒数格式化为年月 进行分类
        models.Article.objects.raw("原生sql语句")

            date_list = models.Article.objects.raw('select nid, count(nid) as num,strftime("%Y-%m",create_time)
                as ctime from repository_article group by strftime("%Y-%m",create_time)')

            查询nid 数量 格式化为年月的时间, 以 时间为分组

        在django中 如果where语句需要使用原生sql语句
        需要在where后紧跟 extra 在extra中写原生where的sql

            article_list = models.Article.objects.filter(blog=blog).extra(
                where=['strftime("%%Y-%%m",create_time)=%s'], params=[val, ]).all()


- CMDB开发 (ITIL构建基础服务)
    TIL即IT基础架构庫(Information Technology Infrastructure Library, ITIL, 信息基础架构庫)

![](https://images2015.cnblogs.com/blog/425762/201702/425762-20170217211746050-1719289549.jpg)


