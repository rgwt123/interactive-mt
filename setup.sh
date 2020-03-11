# load docker images
echo loading mysql-mt image
docker load -i docker_images/mysql-mt
echo load mysql-mt successfully!

echo loading phpmyadmin
docker load -i docker_images/phpmyadmin-mysql
echo load phpmyadmin successfully!

echo loading interactive-mt server
docker load -i docker_images/interactive-mt-base2
echo load interactive-mt server successfully!

