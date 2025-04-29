# Connections 
`https://pinout.xyz/`
## USB Webcam
Plug in a working USB webcam to one of the Raspberry Pi USB ports
## Sensor 
sensor used in this project was the **SHT20** [Wiki link for sensor](https://wiki.dfrobot.com/SHT20_I2C_Temperature_%26_Humidity_Sensor__Waterproof_Probe__SKU__SEN0227)
### Enable **I2C**
Open terminal and run command `sudo raspi-config`
Use the arrow keys to navigate to **3 Interface Options**
Enable **I2C** by navigating to **15 I2C** and select **Yes**
Press **ESC** untill the menu closes


### *Pins Used:*
Red - Pin 1 (VCC)
Green - GND
Blue - Pin 3 (GPIO2 SDA)
Yellow - Pin 5 (GPIO3 SCL)

Once connected type command `sudo i2cdetect -y 1` and record the number
If the number is not `40` change the value in the file `farm_app_docker/farm_app/prog_files/temp_humid_sensor.py`, just change the 40 `sht = SHT20(1, 0x40)`
## 12v Relay Connection 
GND 
Pin 32 (GPIO12)
## 240v Relay Connections 
**GND**
5V - Pin 2 or 4
**MISTER**
Pin 18 (GPIO24)
**INLINE FAN** 
Pin 16 (GPIO23)
**HEAT MAT**
Pin 36 (GPIO16)
**LED LIGHT**
Pin 22(GPIO25)


When restarting the db, make a blank file called **farm_data.db** in the **databases** folder.

# Configurations 

## Creating the Backup Script (optional)
`https://rclone.org/remote_setup/` 
`https://www.youtube.com/watch?v=f8K-V3HHDA0`

Within the enviroment variables located `farm_app_docker/farm_app/.env` and add two entries:
`SCRIPT_LOCATION` - location of the scripts folder ie `/home/YOUR_USERNAME/farm_app_docker/farm_app/scripts/backup.sh`
`LOG_LOCATION` - location of logs ie `/home/YOUR_USERNAME/Documents/farm_app_docker/farm_app/farm_app.log`
### Rclone
Install using `sudo -v ; curl https://rclone.org/install.sh | sudo bash`
#### Steps 
1) rclone config
2) nremote
3) name remote "backup"
4) drive
5) press enter twice
6) 1
7) enter
8) n
9) y

### backup.sh script
```
#!/bin/bash

farm_app_database=*database location*
farm_app_logger="*log location*"

timestamp=$(date +%Y.%m.%d_%H.%M)

destination="*location of backup*/$timestamp"

mkdir -p "$destination"
if [ $? -ne 0 ]; then
    echo "Error creating directory '$destination'"
    exit 1
fi

cp -pv "$farm_app_database" "$destination"
if [ $? -ne 0 ]; then
    echo "Error copying '$farm_app_database'"
    exit 1
fi
echo "$farm_app_database copied to $destination"

cp -pv "$farm_app_logger" "$destination"
if [ $? -ne 0 ]; then
    echo "Error copying '$farm_app_database'"
    exit 1
fi
echo "$farm_app_logger copied to $destination"
```
# .env files
There are two .env files to configure
## farm_app/.env
All options should be filled in, some examples have been added 
```
SCRIPT_LOCATION = /home/YOUR_USERNAME/farm_app_docker/farm_app/scripts/backup.sh
LOG_LOCATION = /home/YOUR_USERNAME/Documents/farm_app_docker/farm_app/farm_app.log
STATE=0 #0 for colinisation and 1 for fruiting
TARGET_TEMP = 18 #goal temperature to maintain 
TEMP_THRESHOLD = 1 #
TARGET_HUMID = 90 #goal humidity to maintain
HUMID_THRESHOLD = 5
AIR_CYCLE_INTERVAL = 3600  # interval in which the air is cycled in seconds in this case 1 hour
COLONIZATION_AIR_CYCLE_INTERVAL = 43200 # interval in which air is cycled during the colinisation phase in seconds
```

## farm_app_docker/.env.prod
All options should be filled in
Explanation of options
```
S_KEY= #generate a key
DATABASE_URI=sqlite:////usr/src/app/farm_web_app/instance/site.db #no need to change 
PASSWORD_SALT= #Generate a password salt
M_UNAME=#Email address of the email that will be used by the app the send emails
M_PWD= #password of the email 
STATE=production #No need to change 
FLASK_APP=farm_web_app/wsgi.py #No need to change 
TOTP= #Generate a key to be usedthe by the TOTP 
FLASK_DEBUG=0 #No need to change 
ADMIN_EMAIL= #Admin Email
ADMIN_PASSWORD=#Admin Password
TEST1_EMAIL=#User 1 Email
TEST1_PASSWORD=#User 1 password
TEST1_USERNAME=#User 1 username
TEST2_EMAIL= #User 2 email
TEST2_PASSWORD=#User 2 Passwoed
TEST2_USERNAME=#User 2 usr
RESCUE_MAIL= #use the same email as M_UNAME
```

On starting the app using docker, connect to the docker container and attach a shell and navigate to `farm_web_user@farm_web_app:/usr/src/app`

Run command `python ./manage.py seed` to populate the database with the admin account 

Access the web app and finish the account set up by adding MFA
Use the TEST1 and TEST2 options to add the other users

Inspecting the logs for the web app container in docker will show that the app listening on `http://0.0.0.0:5000`


When restarting the db, make a blank file called site.db in the **instance** folder.

# Docker-Network
At this stage the web application is ready to start reciving traffic. 
## Prerequisits 
Create a folder called **docker-network** this will contain what is needed to enable external connections.

Create 4 files:
 - Caddyfile
 - docker-compose.yml
 - Dockerfile
 - .env
  
### Caddyfile 
The **Caddyfile** acts as the configuration for the reverse proxy. Copy the code into the file. If you are not using Cloudflare remove **tls** options and edit the **content security policy**.
```
{
    debug
}
{$MY_DOMAIN} {
    log {
        output file /var/log/caddy/access.log {
            roll_size 10MB
            roll_keep 5
            roll_keep_for 14d
            include X-Forwarded-For
        }
    }

    defender drop {
        ranges aws gcloud openai deepseek githubcopilot
    }

    rate_limit {
        zone general_limit {
            match {
                method GET
                header X-RateLimit-Apply true
            }
            key {remote_host}
            events 100
            window 30s
        }

        zone dynamic {
            key {remote_host}
            events 100
            window 30s
        }
    }

    reverse_proxy farm_web_app:5000

    encode gzip zstd

    tls {
        dns cloudflare {env.CLOUDFLARE_API_TOKEN}
    }

    header / {
        -Server
        Access-Control-Allow-Origin YOURDOMAIN/
        Access-Control-Allow-Methods "GET, POST"
        Access-Control-Allow-Headers "Accept, Authorization, Content-Type, X-Requested-With"
        Access-Control-Allow-Credentials false
        Access-Control-Max-Age 3600 
        X-Frame-Options: SAMEORIGIN
        X-XSS-Protection "1; mode=block"
        Content-Security-Policy "default-src 'self'; script-src 'self' https://cdnjs.cloudflare.com https://code.jquery.com/jquery-3.6.0.min.js https://cdn.jsdelivr.net/npm/chart.js https://static.cloudflareinsights.com https://cdnjs.cloudflare.com/ajax/libs/justgage/1.2.9/justgage.min.js https://cdnjs.cloudflare.com/ajax/libs/raphael/2.1.4/raphael-min.js; style-src 'self' 'unsafe-inline'; img-src 'self' blob:; font-src 'self' cdnjs.cloudflare.com; frame-ancestors 'self';"

    }

}
```
### docker-compose.yml
This file contains the information required to create the docker containers and network. Copy the file below and make the required changes to suit your configurations.

```
services:
  caddy:
    container_name: caddy
    build:
      context: .
      target: caddy
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"
    env_file: .env
    environment:
      - MY_DOMAIN
      - CLOUDFLARE_API_TOKEN
      - CROWDSEC_API_KEY
    volumes:
      - caddy-data:/data
      - caddy-config:/config
      - ./caddy-logs:/var/log/caddy
      - ./Caddyfile:/etc/caddy/Caddyfile
    networks:
      farm_network:
    security_opt:
      - no-new-privileges=true


  web:
    build: ../farm_app_docker/services/web  
    user: "${UID}:${GID}"
    command: gunicorn --bind 0.0.0.0:5000 --workers 2 manage:app
    hostname: farm_web_app
    expose:
      - 5000
    security_opt:
      - no-new-privileges=true
    env_file:
      - /home/YOUR_USERNAME/Documents/farm_app_docker/.env.prod
    volumes:
      - type: bind
        source: /home/YOUR_USERNAME/Documents/farm_app_docker/services/web/farm_web_app/instance/site.db
        target: /usr/src/app/farm_web_app/instance/site.db
        read_only: false
      - type: bind
        source: /home/YOUR_USERNAME/Documents/farm_app_docker/farm_app/databases/farm_data.db
        target: /usr/src/app/farm_web_app/farm_data_database/farm_data.db
        read_only: false
      - type: bind
        source: /home/YOUR_USERNAME/Documents/farm_app_docker/farm_app/images
        target: /usr/src/app/farm_web_app/images
        read_only: true
    networks:
      - farm_network
volumes:
  access.log:
  caddy-data:
  caddy-config:

networks:
  farm_network:
    driver: bridge  

```

### Dockerfile
Below is the Dockerfile for Caddy
```
FROM caddy:2.9.1-builder AS builder

RUN xcaddy build v2.9.1 \
    --with github.com/caddy-dns/cloudflare \
    --with github.com/jasonlovesdoggo/caddy-defender \
    --with github.com/mholt/caddy-ratelimit \
    --with github.com/mholt/caddy-l4

FROM caddy:2.9.1 as caddy


COPY --from=builder /usr/bin/caddy /usr/bin/caddy


```

Set up your router to forward or traffic for ports **80** and **443** to the IP address of the **RaspberryPI** which then forwards all the traffic into the docker network.

A url can either be purchased or a free one can be used. A `.xyz` domain can be bought for cheap. 

Set up a cloudflare tunnel and configure the web application firewall that cloudflare provides to your needs. For example cloudflare can block any requests from countries outside a specified list.

## docker-network/.env
Copy this into your .env and make the required changes

```
TZ=CHANGE_TO_YOUR_TIMEZONE IE Europe/London
DOCKER_MY_NETWORK=farm_network
MY_DOMAIN=YOUR_DOMAIN
CLOUDFLARE_API_TOKEN=YOUR_CROWDSEC_API
UID=1000
GID=1000
```

