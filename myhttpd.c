#include"my_httpd.h"
char ip[128],port[8];//全是字符串
char back[8],home_dir[MAX_DIR];//listen队列大小，浏览主目录
char upload_root[MAX_DIR];
char webpage_root[MAX_DIR];
//char username[MAX_UN];
//char passwd[MAX_UN];
char *indexHtml=NULL;//=0
char *favicon=NULL;
struct ThreadArgs{
	int clntSock;
};
void *ThreadMain(void *arg);
void sig_handler();
int main(int argc,char **argv){
	struct sockaddr_in addr;
	int sock_fd;
	unsigned int addrlen;
	if((indexHtml=init_read(indexHtml))==(char*)0) return -1;
	if(argc>1 &&strcmp("-d",argv[1])==0) init_daemon(argv[0],LOG_INFO);
//micro define determine whether to compile the code segment
#if defined __DEBUG
#else
	init_daemon(argv[0],LOG_INFO);//运行守护进程
#endif
/**
设置信号处理器，kill默认是-15 SIGTERM，而Ctrl+C是-2,SIGINT
*/
	(void)signal(SIGINT, sig_handler);
	(void)signal(SIGTERM,sig_handler);
	if(getAllArg()==0){//return >0 if read sucess
		info("PANIC:can't locate configuration file");
		exit(-1);//从配置文件读取参数
	}//get args:home_dir,webpage_root etc.
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
		info(ip);
		info("bind");info(strerror(errno));
		exit(errno);
	}
	if(listen(sock_fd,atoi(back))<0){
		info("listen");exit(-1);
	}
	int new_fd;
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
	close(sock_fd);//not reach here
//	free(indexHtml);
	return 0;
}
void *ThreadMain(void *threadArgs){
	pthread_detach(pthread_self());//容许在完成时无需父线程的干预即可释放线程状态
	int clntSock=((struct ThreadArgs*)threadArgs)->clntSock;
	free(threadArgs);//deallocate memory
	handleTCPClient(clntSock);
	return (void *)NULL;
}
//捕获信号，对内存中的重要数据进行持久存储
void sig_handler(int sig) {//也可无参数
	if(sig==SIGTERM){ //may be caused by:kill <pid>
		info("caught SIGTERM.server to be down.");
	}else if(sig==SIGINT){ //printf("\t你按了ctrl c\n");
		info("caught SIGINT.server to be down.");
	}
	exit(1);
	//(void) signal(SIGINT,SIG_DFL);//再按一次Ctrl+c退出
}
