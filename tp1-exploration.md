TP1 :
1)
sudo docker run -d --name web1 --label adminapi.managed=true nginx:alpine
sudo docker run -d --name intrus nginx:alpine
sudo docker ps

2
princia@princia-VirtualBox:~/adminapi$ D=http://127.0.0.1:2375
princia@princia-VirtualBox:~/adminapi$ echo $D
http://127.0.0.1:2375
princia@princia-VirtualBox:~/adminapi$ curl -i -X POST $D/containers/web1/start
HTTP/1.1 204 No Content
api-version: 1.56
docker-experimental: false
ostype: linux
server: Docker/29.9.2 (linux)
date: Wed, 28 Oct 2026 07:27:05 GMT

princia@princia-VirtualBox:~/adminapi$ curl -s -o /dev/null -w "%{http_code}\n" $D/version
200
princia@princia-VirtualBox:~/adminapi$ curl -s -o /dev/null -w "%{http_code}\n" "$D/containers/json?all=true"
200
princia@princia-VirtualBox:~/adminapi$ curl -s -o /dev/null -w "%{http_code}\n" --get $D/containers/json --data-urlencode 'all=true' --data-urlencode 'filters={"label":["adminapi.managed=true"]}'
200
princia@princia-VirtualBox:~/adminapi$ curl -s -o /dev/null -w "%{http_code}\n" $D/containers/web1/json
200

3
princia@princia-VirtualBox:~/adminapi$ curl -i -X POST $D/containers/web1/stop
HTTP/1.1 204 No Content
api-version: 1.56
docker-experimental: false
ostype: linux
server: Docker/29.9.2 (linux)
date: Wed, 28 Oct 2026 07:48:29 GMT

princia@princia-VirtualBox:~/adminapi$ curl -i -X POST $D/containers/web1/stop
HTTP/1.1 304 Not Modified
api-version: 1.56
docker-experimental: false
ostype: linux
server: Docker/29.9.2 (linux)
date: Wed, 28 Oct 2026 07:48:33 GMT

princia@princia-VirtualBox:~/adminapi$ curl -i $D/containers/nexistepas/json
HTTP/1.1 404 Not Found
api-version: 1.56
content-type: application/json
docker-experimental: false
ostype: linux
server: Docker/29.9.2 (linux)
date: Wed, 28 Oct 2026 07:50:44 GMT
content-length: 44


4
princia@princia-VirtualBox:~/adminapi$ sudo docker compose up -d
[+] up 4/4
 ✔ Container apirest-netbox-redis-1    Running                              0.0s
 ✔ Container apirest-docker-api-1      Running                              0.0s
 ✔ Container apirest-netbox-1          Running                              0.0s
 ✔ Container apirest-netbox-postgres-1 Healthy                              0.6s

princia@princia-VirtualBox:~/adminapi$ curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8080/login/
200
## ouvrir l'interface et swagger ci-dessous les capture d'écran ##
#file:///home/princia/Images/Captures%20d%E2%80%99%C3%A9cran/Capture%20d%E2%80%99%C3%A9cran%20du%202026-10-27%2023-00-55.png#

#file:///home/princia/Images/Captures%20d%E2%80%99%C3%A9cran/Capture%20d%E2%80%99%C3%A9cran%20du%202026-10-27%2023-05-40.png#
 #obtenir un token par API"
princia@princia-VirtualBox:~/adminapi$ curl -s -X POST $N/users/tokens/provision/ -H "content-type: application/json" -H "Accept: application/json" -d '{"username": "admin", "password": "admin"}' | python3 -m json.tool
{
    "id": 1,
    "url": "http://127.0.0.1:8080/api/users/tokens/1/",
    "display_url": "http://127.0.0.1:8080/users/tokens/1/",
    "display": "27rzo0e0cfRI",
    "version": 2,
    "user": {
        "id": 1,
        "url": "http://127.0.0.1:8080/api/users/users/1/",
        "display": "admin",
        "username": "admin"
    },
    "key": "27rzo0e0cfRI",
    "created": "2026-10-27T22:12:30.399891Z",
    "expires": null,
    "last_used": null,
    "enabled": true,
    "write_enabled": true,
    "description": "",
    "allowed_ips": [],
    "token": "<masqué>"
}

 #Ranger le token dans .env #
princia@princia-VirtualBox:~/adminapi$ curl -s -X POST $N/users/tokens/provision/ -H "content-type: application/json" -H "Accept: application/json" -d '{"username": "admin", "password": "admin"}' | python3 -m json.tool
{
    "id": 1,
    "url": "http://127.0.0.1:8080/api/users/tokens/1/",
    "display_url": "http://127.0.0.1:8080/users/tokens/1/",
    "display": "27rzo0e0cfRI",
    "version": 2,
    "user": {
        "id": 1,
        "url": "http://127.0.0.1:8080/api/users/users/1/",
        "display": "admin",
        "username": "admin"
    },
    "key": "27rzo0e0cfRI",
    "created": "2026-10-27T22:12:30.399891Z",
    "expires": null,
    "last_used": null,
    "enabled": true,
    "write_enabled": true,
    "description": "",
    "allowed_ips": [],
    "token": "<masqué>"
}
princia@princia-VirtualBox:~/adminapi$ nano .env
princia@princia-VirtualBox:~/adminapi$ cp .env.example .env
princia@princia-VirtualBox:~/adminapi$ nano .env
princia@princia-VirtualBox:~/adminapi$ curl -s -X POST $N/users/tokens/provision/ -H "content-type: application/json" -H "Accept: application/json" -d '{"username": "admin", "password": "admin"}' | python3 -c "import sys, json; d =json; d = json.load(sys.stdin); print('nbt_' + d['key'] + '.' + d['token'])"
nbt_<key>.<token> (rangé dans .env, noncommité

 #Créer type de cluster 'Docker' puis cluster 'docker-local'#

princia@princia-VirtualBox:~/adminapi$ curl -i -X POST $N/virtualization/cluster-types/ -H "$A" -H "content-type: application/json" -H "Accept: application/json" -d '{"name": "Docker", "slug": "docker"}' 
HTTP/1.1 201 Created
content-type: application/json
location: http://127.0.0.1:8080/api/virtualization/cluster-types/1/
etag: W/"2026-10-27T23:08:52.990278+00:00"
vary: HX-Request, Accept-Language, Cookie, origin
allow: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
x-request-id: 7b872fd6-21a4-417e-a090-436a8e9d131e
api-version: 4.7
x-content-type-options: nosniff
referrer-policy: same-origin
cross-origin-opener-policy: same-origin
x-frame-options: SAMEORIGIN
content-length: 371
content-language: en
server: granian
date: Tue, 27 Oct 2026 23:08:53 GMT

{"id":1,"url":"http://127.0.0.1:8080/api/virtualization/cluster-types/1/","display_url":"http://127.0.0.1:8080/virtualization/cluster-types/1/","display":"Docker","name":"Docker","slug":"docker","description":"","owner":null,"comments":"","tags":[],"custom_fields":{},"created":"2026-10-27T23:08:52.990246Z","last_updated":"2026-10-27T23:08:52.990278Z","cluster_count":0}


princia@princia-VirtualBox:~/adminapi$ curl -i -X POST $N/virtualization/clusters/ -H "$A" -H "content-type: application/json" -H "Accept: application/json" -d '{"name": "docker-local", "type": 1}' 
HTTP/1.1 201 Created
content-type: application/json
location: http://127.0.0.1:8080/api/virtualization/clusters/1/
etag: W/"2026-10-27T23:14:01.883030+00:00"
vary: HX-Request, Accept-Language, Cookie, origin
allow: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
x-request-id: 4fe8e11e-5dce-4e53-9556-cc8fdf885a73
api-version: 4.7
x-content-type-options: nosniff
referrer-policy: same-origin
cross-origin-opener-policy: same-origin
x-frame-options: SAMEORIGIN
content-length: 719
content-language: en
server: granian
date: Tue, 27 Oct 2026 23:14:02 GMT

{"id":1,"url":"http://127.0.0.1:8080/api/virtualization/clusters/1/","display_url":"http://127.0.0.1:8080/virtualization/clusters/1/","display":"docker-local","name":"docker-local","type":{"id":1,"url":"http://127.0.0.1:8080/api/virtualization/cluster-types/1/","display":"Docker","name":"Docker","slug":"docker","description":""},"group":null,"status":{"value":"active","label":"Active"},"tenant":null,"scope_type":null,"scope_id":null,"scope":null,"description":"","owner":null,"comments":"","tags":[],"custom_fields":{},"created":"2026-10-27T23:14:01.882993Z","last_updated":"2026-10-27T23:14:01.883030Z","device_count":0,"virtualmachine_count":0,"allocated_vcpus":null,"allocated_memory":null,"allocated_disk":null}
