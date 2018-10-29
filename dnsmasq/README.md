# dokcer-dnsmasq
---

- DNSmasq是一个小巧且方便地用于配置DNS和DHCP的工具，适用于小型网络，
它提供了DNS功能和可选择的DHCP功能。它服务那些只在本地适用的域名，
这些域名是不会在全球的DNS服务器中出现的。DHCP服务器和DNS服务器结合，
并且允许DHCP分配的地址能在DNS中正常解析，而这些DHCP分配的地址和相关命令可以配置到每台主机中，
也可以配置到一台核心设备中（比如路由器），DNSmasq支持静态和动态两种DHCP配置方式。
- 目前只采用了DNSmasq中的DNS服务
- 无需修改任何配置文件，开启就可以使用


#### 1. 运行方式
进入openvpn
> \$ docker built -t dnsmasq .  
> \$ docker-composer up -d 

**需要将本地下/etc/resolv.conf文件中的nameserver修改成当前的内网IP**

#### 2. 其他

> $ vim ~/dnsmasq_data/def_set/dnsmasq.resolv
    
    这个文件主要是对dns服务器的修改，默认会使用本地的dns，当本地dns匹配不到相应的ip时，会读取
    这个文件中的dns，修改此文件，dnsmasq会重新读取无需重启

> $ vim ~/dnsmasq_data/def_set/dnsmasq.hosts
    
    这个文件主要是做域名解析，即自定义解析a记录，例如：192.168.115.10 www.baidu.com baidu.com
    访问baidu.com或www.baidu.com时的所有域名都会被解析成192.168.115.10, 修改此文件dnsmasq
    不会默认读取，你可以重启服务或者对此服务发送一个kill -1 PID这样的信号(PID是你宿主机中dnsmasq的PID)，
    只需在宿主机中执行此命令即可
    
> $ vim ~/dnsmasq_data/dns_set/dnsmasq_server.conf
    
    指定使用哪个DNS服务器进行解析，对于不同的网站可以使用不同的域名对应解析。
    例如：server=/google.com/8.8.8.8 #表示对于google的服务，使用谷歌的DNS解析。
    此配置需重启服务
    
> $ vim ~/dnsmasq_data/dns_set/dnsmasq_address.conf
    
    启用泛域名解析，即自定义解析a记录，例如：address=/long.com/192.168.115.10 
    访问long.com时的所有域名都会被解析成192.168.115.10, 此配置和dnsmasq.hosts目的是相同的
    此配置也需要重启服务


