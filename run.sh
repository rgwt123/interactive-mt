cd /interactive-mt/transerver
nohup /opt/conda/bin/python server.py &
/usr/sbin/nginx -g "daemon off;"
