<!--
container_name="$(kubectl get pod -l app=khww-wordpress,tier=mysql -o custom-columns=NAME:.metadata.name --no-headers)"
wp_pass=$(kubectl logs $container_name | grep "ROOT PASSWORD:" | awk '{print $NF}')
bzcat wp_mysqldump.sql.bz2 | kubectl exec -i $container_name -- mysql -u root -p$wp_pass

container_name="$(kubectl get pod -l app=khww-wordpress,tier=frontend -o custom-columns=NAME:.metadata.name --no-headers)"
cat wp_wordpress.tar.bz2 | kubectl exec -i $container_name -- tar xfj - -C /var/www
-->
