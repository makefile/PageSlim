#include "my_httpd.h"
void init_daemon(const char *pname,int facility){
	int i,pid;
	signal(SIGTTOU,SIG_IGN);//处理可能的终端信号
	signal(SIGTTIN,SIG_IGN);
	signal(SIGTSTP,SIG_IGN);
	signal(SIGHUP,SIG_IGN);
	if(pid=fork()) exit(0);
	else if(pid<0){
		perror("fork");exit(-1);
	}
	setsid();//设置新会话组长，新进程组长，脱离终端
	if(pid=fork()) exit(0);//子进程不能再申请终端
	else if(pid<0){
		perror("fork");
		exit(-1);
	}
	for(i=0;i<NOFILE;++i) close(i);
	open("/dev/null",O_RDONLY);
	open("/dev/null",O_RDWR);//描述符0,1,2都定向到null
	open("/dev/null",O_RDWR);
	chdir("/tmp");//修改主目录
	umask(0);//重置文件掩码
	signal(SIGCHLD,SIG_IGN);
	openlog(pname,LOG_PID,facility);
	//与守护进程建立联系，加上进程号，文件名
	return ;
}
void info(char *msg){
#if defined __DEBUG
	syslog(LOG_INFO,"%s",msg);
#else
	fprintf(stderr,"%s\n",msg);
#endif
}
void sendHead(FILE *sock){
	//fprintf(sock,"HTTP/1.1 200 OK\r\nServer:Honey\r\nConnection:close\r\n\r\n");//两个\r\n,头部结束，HTTP1.0默认close,1.1默认keep-alive
	fprintf(sock,"HTTP/1.1 200 OK\r\n");
	fprintf(sock,"Server: Honey\r\n");
	fprintf(sock,"Connection: close\r\n\r\n");
	fflush(sock);
}
void sendHead_sock(int sock){
	send(sock,"HTTP/1.1 200 OK\r\n",16,0);//其实发送的时候并没有发送'\n'，16是strlen的长度，遇到\n或\0就终止计算长度
	send(sock,"Server: Honey\r\n",15,0);
	send(sock,"Connection:close\r\n",17,0);
}
/*读取配置文件/etc/ my_httpd.conf,进行字符串匹配*/
int get_arg(char *cmd,char *buf,char *glb_var){
/*	FILE *fp;
	char buf[1024];
	fp=fopen("/etc/pageSlim/my_httpd.conf","r");
	bytes_read=fread(buf,1,sizeof(buf),fp);//file size
	fclose(fp);
	if(bytes_read==0||bytes_read==sizeof(buffer)) 
		return 0;//没读到或文件太大
	buf[bytes_read]='\0';
*/	size_t bytes_read;
	char * match=NULL;
//	extern char ip[],home_dir[],upload_root[],webpage_root[],port[],back[],username[],passwd[];
	if(!strncmp(cmd,"home_dir",8)){
		match=strstr(buf,"home_dir=");
		if(match==NULL) return 0;
		bytes_read=sscanf(match,"home_dir=%s",glb_var);
		//bytes_read is 1
		bytes_read=strlen(glb_var);
		if(glb_var[bytes_read-1]=='/')
			glb_var[bytes_read-1]='\0';
		return bytes_read;
	}else if(!strncmp(cmd,"upload_dir",10)){
		match=strstr(buf,"upload_dir=");
		if(match==NULL) return 0;
		bytes_read=sscanf(match,"upload_dir=%s",glb_var);
		bytes_read=strlen(glb_var);
		if(glb_var[bytes_read-1]=='/')
			glb_var[bytes_read-1]='\0';
		return bytes_read;
	}else if(!strncmp(cmd,"webpage_dir",11)){
		match=strstr(buf,"webpage_dir=");
		if(match==NULL) return 0;
		bytes_read=sscanf(match,"webpage_dir=%s",glb_var);
		bytes_read=strlen(glb_var);
		if(glb_var[bytes_read-1]=='/')
			glb_var[bytes_read-1]='\0';
		return bytes_read;
	}else if(!strncmp(cmd,"port",4)){
		match=strstr(buf,"port=");
		if(match==NULL) return 0;
		bytes_read=sscanf(match,"port=%s",glb_var);
		return bytes_read;
	}else if(!strncmp(cmd,"ip",4)){
		match=strstr(buf,"ip=");
		if(match==NULL) return 0;
		bytes_read=sscanf(match,"ip=%s",glb_var);
		return bytes_read;
	}else if(!strncmp(cmd,"back",4)){
		match=strstr(buf,"back=");
		if(match==NULL) return 0;
		bytes_read=sscanf(match,"back=%s",glb_var);
		return bytes_read;
	}else if(!strncmp(cmd,"username",8)){
		match=strstr(buf,"username=");
		if(match==NULL) return 0;
		bytes_read=sscanf(match,"username=%s",glb_var);
		return bytes_read;
	}else if(!strncmp(cmd,"passwd",6)){
		match=strstr(buf,"passwd=");
		if(match==NULL) return 0;
		bytes_read=sscanf(match,"passwd=%s",glb_var);
		return bytes_read;
	}else return 0;
}
int getAllArg(){//上面的get_arg写的罗嗦了一些，但为了方便以后提取单个属性
	FILE *fp;
	char buf[1024];
	size_t bytes_read;
	char * match=NULL;
	extern char ip[],home_dir[],upload_root[],webpage_root[],port[],back[],username[],passwd[];
	fp=fopen("/etc/pageSlim/my_httpd.conf","r");
	bytes_read=fread(buf,1,sizeof(buf),fp);//file size
	fclose(fp);
	if(bytes_read==0||bytes_read==sizeof(buffer)) 
		return 0;//没读到或文件太大
	buf[bytes_read]='\0';
	if(get_arg("home_dir",buf,home_dir)==0)//从配置文件读取参数
		sprintf(home_dir,"%s","/tmp");
//	info(home_dir);
	if(get_arg("upload_dir",buf,upload_root)==0) 
		sprintf(upload_root,"%s","/var/www");
	if(get_arg("webpage_dir",buf,webpage_root)==0) 
		sprintf(webpage_root,"%s","/var/www");
	if(get_arg("ip",buf,ip)==0) get_addr("eth0");//本机ip
	if(get_arg("port",buf,port)==0) sprintf(port,"%s","80");//默认80
	if(get_arg("back",buf,back)==0) sprintf(back,"%s","5");
	if(get_arg("username",buf,username)==0) sprintf(username,"%s","admin");
	if(get_arg("passwd",buf,passwd)==0) sprintf(passwd,"%s","");
	return 1;
}
char *chinese2host(char *path){
	int fd,len,ret,i=0,sum=0;
	char chinese[256];
	for(ret=0,len=strlen(path);ret<len;ret++){
		if(path[ret]=='%') {
			path[ret+2]=hexstr2int(path[ret+1],
					path[ret+2]);
			ret+=2;
		}
	}
	for(ret=0;ret<len;ret++){
		if(path[ret]=='%'){
			chinese[i++]=path[ret+2];
			ret+=2;
		}else
			chinese[i++]=path[ret];
	}
	chinese[i]='\0';
	if(i>0) strcpy(path,chinese);
	return path;
}

