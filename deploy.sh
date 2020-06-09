scp -P 222 -r . root@ik1-420-42243.vs.sakura.ne.jp:/root/deploy/
ssh root@ik1-420-42243.vs.sakura.ne.jp -p 222 "bash /root/deploy/restart.prod.sh"