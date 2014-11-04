#include"my_httpd.h"
char ip[128],port[8];//全是字符串
char back[8],home_dir[128];//listen队列大小，浏览主目录
char upload_root[128];
char webpage_root[128];
char username[30];
char passwd[30];
struct ThreadArgs{
	int clntSock;
};
void *ThreadMain(void *arg);
int main(int argc,char **argv){
	struct sockaddr_in addr;
	int sock_fd;
	unsigned int addrlen;
//	init_daemon(argv[0],LOG_INFO);//运行守护进程
	if(get_arg("home_dir")==0)//从配置文件读取参数
		sprintf(home_dir,"%s","/tmp");
	info(home_dir);
	if(get_arg("upload_dir")==0) 
		sprintf(upload_root,"%s","/var/www");
	if(get_arg("webpage_dir")==0) 
		sprintf(webpage_root,"%s","/var/www");
	if(get_arg("ip")==0) get_addr("eth0");//本机ip
	if(get_arg("port")==0) sprintf(port,"%s","80");//默认80
	if(get_arg("back")==0) sprintf(back,"%s","5");
	if(get_arg("username")==0) sprintf(username,"%s","admin");
	if(get_arg("passwd")==0) sprintf(passwd,"%s","");
	if((sock_fd=socket(PF_INET,SOCK_STREAM,0))<0){
		info("socket()");//对syslog(LOG_INFO,"%s",msg)的包装
		exit(-1);
	}
	addrlen=1;//any integer,value-result argument
	setsockopt(sock_fd,SOL_SOCKET,SO_REUSEADDR,&addrlen,sizeof(addrlen));//容许重用本地地址和端口
	addr.sin_family=AF_INET;
	addr.sin_port=htons(atoi(port));
	addr.sin_addr.s_addr=inet_addr(ip);
	addrlen=sizeof(struct sockaddr_in);
	if(bind(sock_fd,(struct sockaddr*)&addr,addrlen)<0){
		info("bind");exit(-1);
	}
	if(listen(sock_fd,atoi(back))<0){
		info("listen");exit(-1);
	}
	int len,new_fd;
	while(1){
		//addrlen=sizeof(struct sockaddr_in);
		new_fd=accept(sock_fd,(struct sockaddr*)&addr,&addrlen);
		if(new_fd<0){
			info("accept");
			exit(-1);
		}
	//	bzero(buffer,MAXBUF+1);//似乎buffer,BUFSIZ都在标准库,对超出的内存区域初始化会段错误，不知+1后会不会超出
		//in strings.h,but memset in string.h
		sprintf(buffer,"connect come from: %s:%d\n",inet_ntoa(addr.sin_addr),ntohs(addr.sin_port));
		info(buffer);//log
/*		pid_t pid;
		int contLen=0;
		if((pid=fork())==-1){
			info("fork");
			exit(-1);
		}
		if(pid==0){//child
			close(sock_fd);
			continue;
		}
*/
		struct ThreadArgs *threadArgs=(struct ThreadArgs*)malloc(sizeof(struct ThreadArgs));
		if(threadArgs==NULL){ info("malloc failed!!");break;}
		threadArgs->clntSock=new_fd;
		pthread_t threadID;
		int ret=pthread_create(&threadID,NULL,ThreadMain,threadArgs);
		if(ret!=0){info("pthread_create error:");strerror(ret);}
	}
	close(sock_fd);
	return 0;
}
void *ThreadMain(void *threadArgs){
	pthread_detach(pthread_self());//容许在完成时无需父线程的干预即可释放线程状态
	int clntSock=((struct ThreadArgs*)threadArgs)->clntSock;
	free(threadArgs);//deallocate memory
	handleTCPClient(clntSock);
	return;
}
