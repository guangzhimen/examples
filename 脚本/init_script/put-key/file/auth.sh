#!/bin/bash
	keys=`cat ~/.ssh/authorized_keys |grep "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA7OvIMl01gTgvnr6t7KQUvBR0Q43cfRvTWqiE8II1NVdkjU8yw4HCJqokdw15KtRvchWlj/jES8dexcw6d5rk+XG2YlzaZHlsFjHGC6Y12Zl48oy1ZWRowohlduvvmN+SdSRj/7/ZjkEexEwoK2h3BL0TngcvQiHxrkk3XFHO8bggM2DbOll0vEKOHFCNWh7FG/KL32AAaezwt4+3oEpetGidYqLa5KD47nOg/xytuGL+Tu23gMdiuE4eCh9Wi9WXVPgXxtqQVYfhpuP3AcBsEM/C/1ujNqj5Gzd92gHkxDb6N9Eg1GR/9uo3qWuoQpP8lGtj4RaxxYMtmuD/YbbWLQ== root@mysql-141-32" |wc -l`
	if [ $keys -eq 0 ] || [ ! -f ~/.ssh/authorized_keys ];then
		echo "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA7OvIMl01gTgvnr6t7KQUvBR0Q43cfRvTWqiE8II1NVdkjU8yw4HCJqokdw15KtRvchWlj/jES8dexcw6d5rk+XG2YlzaZHlsFjHGC6Y12Zl48oy1ZWRowohlduvvmN+SdSRj/7/ZjkEexEwoK2h3BL0TngcvQiHxrkk3XFHO8bggM2DbOll0vEKOHFCNWh7FG/KL32AAaezwt4+3oEpetGidYqLa5KD47nOg/xytuGL+Tu23gMdiuE4eCh9Wi9WXVPgXxtqQVYfhpuP3AcBsEM/C/1ujNqj5Gzd92gHkxDb6N9Eg1GR/9uo3qWuoQpP8lGtj4RaxxYMtmuD/YbbWLQ== root@mysql-141-32" >> ~/.ssh/authorized_keys
	fi	
