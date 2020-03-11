echo start running mysql-mt server
docker run -p 3306:3306 --name mysql-mt -v $PWD/mysql/conf:/etc/mysql/conf.d -v $PWD/mysql/logs:/logs -v $PWD/mysql/data:/var/lib/mysql --restart=always -d 894c6592ada1

echo start running phpmyadmin server
docker run --name phpmyadmin -d -e PMA_HOST=172.17.0.1 -e PMA_PORT=3306 -p 8081:80 --restart=always 669d24d5c54a

echo start running interactive-mt-base2
nvidia-docker run -d --name interactive-mt -p 8080:80 -v $PWD:/interactive-mt --restart=always 0660fac8ac50
