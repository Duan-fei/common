# dokcer-openvpn
---

- 此openvpn采用账号密码方式登陆
- 采用一份客户端配置文件，无需证书等文件
- 可以自定义配置文件server.conf以及client.conf
- 所有文件只需配置密码文件即可


#### 1. 修改docker-compose.yml
- SERVER ——openvpn 服务的服务地址以及分发给客户端的地址, 前面为ip地址后面为掩码, 以空格分隔. VPN网络使用的网段要避免和本地网段冲突.
- PUSH ——允许客户端访问的服务器地址(如: 172.31.0.0 255.255.0.0)
- CLIENTREMOTE ——客户端需要连接的服务端器地址(如: 55.10.123.57)
- KEY_COUNTRT ——定义所在的国家(如: CN, 此变量需要注意长度一般为2位)
- KEY_PROVINCE ——定义所在的省份(如: BJ, 此变量需要注意长度一般为2位)
- KEY_CITY ——定义所在的城市(如: Beijing)
- KEY_ORG ——定义所在的组织(如: shannon.ai)
- KEY_EMAIL ——定义邮箱地址(如: contact@shannonai.com)
- KEY_OU ——定义所在的单位(如: shannon.ai)
- KEY_SIZE ——定义生成私钥的大小(一般为1024或者2048)

#### 2. 运行方式
进入openvpn
> \$ docker built -t openvpn .  
> \$ docker-composer up -d 

**因需要生成证书等配置文件所以可能会需要等待3~5分钟**

#### 3. 其他

- 只需修改挂载的文件中的password添加账号密码即可连接(xxxx xxxx)
- 前为账号 后面为密码 以空格进行分隔

#### 4. 示例
如果在vagrant中运行openvpn, vagrant 虚拟机的内网网段是 10.0.2.0/24, 公网IP是 192.168.33.10, VPN 网络的网段是 172.19.0.0/16, 则对应的 docker-compose.yml 如下:

```shell
version: '3.2'
services:
    openvpn:
        image: registry.cn-beijing.aliyuncs.com/shannonai/openvpn
        container_name: openvpn
        network_mode: host
        restart: always
        volumes:
            - ./data:/etc/openvpn
        ports:
            - "1194"
        cap_add:
            - NET_ADMIN
        environment:
            - SERVER=172.19.0.0 255.255.0.0  # VPN network segment (LAN IP)
            - PUSH=10.0.2.0 255.255.255.0 # LAN network segment of host machine
            - CLIENTREMOTE=192.168.33.10  # VPN server WAN IP
            - KEY_COUNTRY=CN  # The state abbreviation
            - KEY_PROVINCE=BJ  # Province shorthand
            - KEY_CITY=BeiJing # City
            - KEY_ORG=ShannonAI LLC  # organization
            - KEY_OU=shannonai.com # affiliated unit
            - KEY_EMAIL=contact@shannonai.com # Email
            - KEY_SIZE=2048  # The private key size: 2048, 4096

```
