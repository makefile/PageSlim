#include "my_httpd.h"
#include "cJSON.h"
char *formatText(char *text);
//int hexstr2int(char x,char y);
char *postfix(char *file);
void listHomeFiles(FILE *client_sock,char *path);
void showSlimList(FILE *client,char *req);
void echoSlimPage(FILE *client,char *req);
void login_auth(FILE *client,char *req);
void delete_page(FILE *client,char *req);
//void signup(FILE *client,char *req);
/*
   以html响应客户端的请求，若请求是目录，则列出目录信息，若是文件，则将文件内容传送给客户端
   */
//the path is request,such as /blog,/showAll,not always be directory
void GiveResponse(FILE *client,char *req){
	if(strncasecmp(req,"/doslim",7)==0){//request doSlim
		responseDoSlim(client,req);
		return ;
	}else if(strncasecmp(req,"/showlist",9)==0){
		info("will showlist...");
		showSlimList(client,req);
	}else if(strncasecmp(req,"/view?resp=html",15)==0)
		echoHtmlPage(client,req);
	else if(strncasecmp(req,"/view",5)==0)
		echoSlimPage(client,req);
	//目前由于存储区域未进行按用户划分，因此验证登录多用户无现实意义
	//可以针对管理员设置密码，验证身份
	else if(strncasecmp(req,"/login",6)==0)
		login_auth(client,req);//?un=xx&pw=xx (md5)
//	else if(strncasecmp(req,"/signup",7)==0)
//		signup(client,req);//registe
	else if(strncasecmp(req,"/delete",7)==0)
		delete_page(client,req);//?abs=xx&un=xx&pw=xx
//	else if(strstr(webpage_root,req)!=NULL)
	else listHomeFiles(client,req);
}
/*将webpage_root下的所有文件夹下的文件名列成树形JSON列表
需要递归访问每个文件夹并填写JSON数据，这样客户端可以查看整个列表而不用多次访问网络
   */
void makeJson(char *abspath,cJSON *parent){//in curse,absolute path
	struct dirent *dirent;//dirent may statically a
	struct stat fileinfo;
	DIR *dir;
	char subdir[MAX_DIR];
	cJSON *sub ;
	stat(abspath,&fileinfo);
	if(S_ISREG(fileinfo.st_mode)){//st_mtime
//		info(abspath);
		cJSON_AddStringToObject(parent,abspath,"file");
	}else if(S_ISDIR(fileinfo.st_mode)){
		//只要是个文件夹就创建个对象
		dir=opendir(abspath);
		//note that realpath() is a function from limits.h and stdlib.h, I wrongly replaced the 'abspath',causes error
		sub = cJSON_CreateObject();
		while((dirent=readdir(dir))!=NULL){
			if('.'==dirent->d_name[0]) continue;
			sprintf(subdir,"%s/%s",abspath,dirent->d_name);
	//		info(subdir);
			makeJson(subdir,sub);//和下一句的顺序不要弄反，否则死循环
		}
		cJSON_AddItemToObject(parent,abspath,sub);
	}
}
/*在showlist和view中发送响应头后python客户端都会打印出脏数据，而去掉响应头直接发送正文，客户端竟然正常接收
   */
void showSlimList(FILE *client,char *req){
	extern char webpage_root[];
	sendHead(client);
	cJSON *root;
	root = cJSON_CreateObject();
	makeJson(webpage_root,root);
	info("send json");
	char *result = cJSON_Print(root);
//	info("the json is:");//send
//	info(result);//send,puts
	fputs(result,client);
	fflush(client);
	free(result);
	cJSON_Delete(root);
//	char msg[100];
//	sprintf(msg,"size:%d",strlen(result));
//	info(msg);
}
/*给手机客户端发送所请求的文本的内容*/
void echoSlimPage(FILE *client,char *req){
//	req include a absolute path of a file
	///view?dir=xxx
	char abspath[MAXPATH];
	extern char webpage_root[];
	sscanf(req,"/view?dir=%s",abspath);
	chinese2host(abspath);
	if(strncasecmp(webpage_root,abspath,strlen(webpage_root))!=0){
		fputs("Permission denied!",client);
		return;
	}
	int fd=open(abspath,O_RDONLY);
	if(fd==-1){
		info("open file error:");
		info(abspath);
		sendHead(client);
		fputs("open file error!",client);
		return;
	}
	int len=lseek(fd,0,SEEK_END);
	char* p=(char *)malloc(len+1);//maybe need '\0'
	bzero(p,len+1);
	lseek(fd,0,SEEK_SET);
	int ret=read(fd,p,len);//一次性读取文件，对于大文件会出错，有时间再改，分批读取和传送文件
	//char logmsg[30];
	if(ret<0) info("droid:read fail");
	close(fd);
	sendHead(client);
//	char msg[128];
//	sprintf(msg,"strlen of head:%d",strlen(packHead_close));
//	info(msg);
	fwrite(p,len,1,client);//send file content
	fflush(client);
	free(p);
}
void listHomeFiles(FILE *client_sock,char *path){
	struct dirent *dirent;
	struct stat fileinfo;
	char Filename[MAXPATH];
	DIR *dir;
	int fd,len,ret;
	//FILE *fp;
	char *p,*realpath,*realFilename,*nport;
	struct passwd *p_passwd;
	struct group *p_group;
//	char chinese[MAXPATH];
	extern char home_dir[],ip[],port[],webpage_root[];
	//extern char packHead_close[];
	//目前未容许选择可上传到的路径，统一放在/upload目录下
	char uploadHtml[]="<form method=\"POST\" action=\"/upload\" enctype=\"multipart/form-data\">上传文件"
		"<input name=\"image\" type=\"file\" />"
		"<input type=\"submit\" value=\"Upload\" /></form>";
	//the action will exist in the head:POST /dir HTTP...
	//将url的16进制编码的中文名还原成主机能够识别的编码
	chinese2host(path);
	//因请求的文件是以服务器主目录为根目录如/var/www/,因此需要加该根目录才是绝对路径
	len=strlen(home_dir)+strlen(path)+1;
	realpath=malloc(len+1);
	bzero(realpath,len+1);
	sprintf(realpath,"%s%s",home_dir,path);
	//get port
	len=strlen(port)+1;
	nport=malloc(len+1);
	bzero(nport,len+1);
	sprintf(nport,":%s",port);
	//file state
	if(stat(realpath,&fileinfo)){//fail
		sendHead(client_sock);
		fprintf(client_sock,"<html lang=\"zh-cn\"><html><head><meta charset=\"utf-8\"><title>%d - %s</title></head>"
			"<body><font size=+4>Linux HTTP server</font><br><hr width=\"100%%\"><br><center><table border cols=3 width=\"100%%\"></table><font color=\"CC0000\" size=+2> connect to administrator,error path is: \n%s %s</font></body></html>",errno,strerror(errno),path,strerror(errno));
		goto out;
	}
	if(S_ISREG(fileinfo.st_mode)){//send file content
		fd=open(realpath,O_RDONLY);
		len=lseek(fd,0,SEEK_END);
		p=(char *)malloc(len+2048);//plus 2048 is due to i when display the text,need extra space:'<' changes to &#60;
		bzero(p,len+2048);
//		info(realpath);info(webpage_root);
		if(strncmp(realpath,webpage_root,strlen(webpage_root))==0){
			sprintf(p,"/view?resp=html&dir=%s",realpath);
			echoHtmlPage(client_sock,p);
			free(p);
			close(fd);
			goto out;
		}
		lseek(fd,0,SEEK_SET);
		ret=read(fd,p,len);//一次性读取文件，对于大文件会出错，有时间再改，分批读取和传送文件
//		char logmsg[MAX_MSG];
		if(ret<0) info("read fail");
		close(fd);		
		char *type=postfix(path);
		if(strcmp("c",type)==0||strcmp("java",type)==0
			||strcmp("py",type)==0||strcmp("txt",type)==0){
		//<的转义序列为&lt; or &#60;,> &gt; &#62;,&的转义为&amp; or &#38; 不转义的话<stdio.h>被当作标签，但不显示
			sendHead(client_sock);
			fprintf(client_sock,"<html lang=\"zh-cn\"><html><head><meta charset=\"utf-8\"><title>content of %s</title></head><body><font size=+4>网文快传-Server</font><br><hr width=\"100%%\"><br><font color=\"119966\" size=+3>%s</font></body></html>"//<center>
					,path,formatText(p));
		}else if(strcmp("jpg",type)==0||strcmp("png",type)==0){
			fprintf(client_sock,"HTTP/1.1 200 OK\r\nServer:Test http server\r\nConnection:keep-alive\r\nContent-type:image\r\nContent-Length: %d\r\n\r\n",len);
			fwrite(p,len,1,client_sock);//send file content
			
		}else if(strcmp("html",type)==0){
			sendHead(client_sock);
			fwrite(p,len,1,client_sock);//send file content
		}else{
			fprintf(client_sock,"HTTP/1.1 200 OK\r\nServer:Test http server\r\nConnection:keep-alive\r\nContent-type:application/*\r\nContent-Length:%d\r\n\r\n",len);
			//for transport file,so keep-alive
			fwrite(p,len,1,client_sock);//send file content
		}
		free(p);
	}else if(S_ISDIR(fileinfo.st_mode)){
		dir=opendir(realpath);
		sendHead(client_sock);
		fprintf(client_sock,"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0 Transitional//EN\"><html lang=\"zh-cn\"><html><head><meta charset=\"utf-8\"><title>%s</title></head><body><font size=+4>网文快传-Server</font><br><hr width=\"100%%\"><br>%s<center>"
			"<table border cols=3 width=\"100%%\">",path
				,uploadHtml);
		fprintf(client_sock,"<caption><font size=+3> Directory %s</font></caption>\n",path);//表格头信息，便于显示
		fprintf(client_sock,"<tr><th>name</th><th>type</th><th>owner</th><th>group</th><th aligh=\"center\">size</th><th>modify time</th></tr>\n");
		if(dir==NULL){//打开目录失败
			fprintf(client_sock,"</table><font color=\"CC0000\" size=+2>%s</font></body></html>",strerror(errno));
			return ;
		}
		fprintf(client_sock,"<th><a href=\"http://%s%s%s\">..parent..</a></th><br>",ip,atoi(port)==80?"":nport,dir_up(path));//go to parent dir
		while((dirent=readdir(dir))!=NULL){
			if(strcmp(path,"/")==0)//website root,no display parent fold
				sprintf(Filename,"/%s",dirent->d_name);
				//create web absolute dir
			else sprintf(Filename,"%s/%s",path,dirent->d_name);
			if(dirent->d_name[0]=='.')
				continue;//隐藏文件不列出,以及..和.
			fprintf(client_sock,"<tr>");
			len=strlen(home_dir)+strlen(Filename)+1;
			realFilename=malloc(len+1);
			bzero(realFilename,len+1);
			sprintf(realFilename,"%s/%s",home_dir,Filename);//主机上的绝对路径
			if(stat(realFilename,&fileinfo)==0){
				 fprintf(client_sock,"<td><a href=\"http://%s%s%s\">%s</a></td>",ip,atoi(port)==80?"":nport,Filename,dirent->d_name);
				//p_time=ctime(&info.st_mtime);
				p_passwd=getpwuid(fileinfo.st_uid);//文件拥有者
				p_group=getgrgid(fileinfo.st_gid);//拥有者组

				fprintf(client_sock,"<td>%c</td>",file_type(fileinfo.st_mode));
				fprintf(client_sock,"<td>%s</td>",p_passwd->pw_name);//the file hoster
				fprintf(client_sock,"<td>%s</td><td align=\"right\">%d</td><td>%s</td>",p_group->gr_name,(int)fileinfo.st_size,ctime(&fileinfo.st_ctime));
			}
			fprintf(client_sock,"</tr>\n");
			free(realFilename);
		}//while end
		fprintf(client_sock,"</table></center></body></html>");
	}else{//neither file or dir,forbid access
		sendHead(client_sock);
		fprintf(client_sock,"<html lang=\"zh-cn\"><html><head><meta charset=\"utf-8\"><title>Permission denied</title></head><body><font size=+4>网文快传-Server</font><br><hr width=\"100%%\"><br><table border cols=3 width=\"100%%\">");
		fprintf(client_sock,"</table><font color=\"CC0000\" size=+2> you access resource '%s' forbid to access,communicate with the admintor </font></body></html>",path);
	}
out:
	free(realpath);
	free(nport);
}

char file_type(mode_t st_mode){
	if((st_mode&S_IFMT)==S_IFSOCK) return 's';
	else if((st_mode&S_IFMT)==S_IFLNK) return 'l';
	else if((st_mode&S_IFMT)==S_IFREG) return '-';
	else if((st_mode&S_IFMT)==S_IFBLK) return 'b';
	else if((st_mode&S_IFMT)==S_IFCHR) return 'c';
	else if((st_mode&S_IFMT)==S_IFIFO) return 'p';
	else return 'd';
}
//search the up-path of dirpath
char *dir_up(char *dirpath){
	static char Path[MAXPATH];
	int len;
	strcpy(Path,dirpath);
	len=strlen(Path);
	if(len>1&&Path[len-1]=='/') len--;
	while(Path[len-1]!='/'&&len>1)
		len--;
	Path[len]=0;
	return Path;
}

int get_addr(char *str){
	int inet_sock;
	struct ifreq ifr;
	extern char ip[];
	inet_sock=socket(AF_INET,SOCK_STREAM,0);
	strcpy(ifr.ifr_name,"eth0");//本机接口名
	if(ioctl(inet_sock,SIOCGIFADDR,&ifr)<0){//获取接口信息
		info("ioctl,fail to get eth0 ip");
		exit(-1);
	}
	sprintf(ip,"%s",inet_ntoa(((struct sockaddr_in*)&(ifr.ifr_addr))->sin_addr));
	return 0;
}
	
char *formatText(char *text){
	int i=0,j=0;
	char *ft=malloc(strlen(text)*10);//设小了不行，double free or corruption
	//it is big bug use sizeof(text),because big file will overflow
//	memset(ft,0,(ft));
	//the size of space ,use strcpy +1,not sizeof.
	while(text[i]!='\0'){
		if(text[i]=='<')
			strncpy(ft+j,"&#60;",5);
		else if(text[i]=='>')
			strncpy(ft+j,"&#62;",5);
		else if(text[i]==' '){
			strncpy(ft+j,"&#160;",6);//&nbsp;
			j++;
		}
		else if(text[i]=='&')
			strncpy(ft+j,"&#38;",5);
		else if(text[i]=='\n')
			strncpy(ft+j,"</br>",5);
		else if(text[i]=='\t'){//TAB键并没有html的转义字符
		//但可在<pre></pre>标签中使用&#9;表示
			strncpy(ft+j,"&nbsp;&nbsp;&nbsp;&nbsp;",24);
			j+=19;
		}
		else {
			ft[j]=text[i];
			j-=4;
		}
		i++;
		j+=5;
	}
	ft[j]='\0';
	text=realloc(text,strlen(ft));
	//the original text size is too small,and cause error:double free or corruption
	strcpy(text,ft);
	free(ft);
	ft=NULL;
	return text;
}

int hexstr2int(char x,char y){//姑且假设文件名中仅含有字母数字及中文连字符空格
	int ret=16776960,i,tmp=0;//0xffff00
	char a[]={x,y};
	for(i=0;i<2;i++){
		if(a[i]>='0'&&a[i]<='9') tmp=tmp*16+a[i]-'0';
		else tmp=tmp*16+a[i]-55;//-65+10 ascii:A65,a97
		//Path中的中文编码是大写的，如'传':%E4%BC%A0,实际为16进制0xFFFFE4...
	}
	ret=ret+tmp;
	return ret;
}
/*返回文件的后缀名，此处仅简单判断最后的.后的字符，因此不适用于.tar.gz等以及后缀名与属性不符的情形，后续改进 */
char *postfix(char *file){
	int i=0,lastIndex=0;
	while(file[i]!='\0'){
		if(file[i]=='.') lastIndex=i;
		i++;
	}
	return &file[lastIndex+1];
}
//strrchr(.)获得.后边的扩展名
void login_auth(FILE *client,char *req){
	char user[MAX_UN],pw[MAX_UN];
	extern char username[],passwd[];
	sscanf(req,"/login?un=%[^&]&pw=%s",user,pw);
	chinese2host(user);
	sendHead(client);//200 OK
//	info("conf:username:");info(username);
//	info(passwd);
	if(strcmp(user,username)==0
			&&strncasecmp(pw,passwd,strlen(passwd))==0)
		fputs("login_ok",client);
	else fputs("login_deny",client);
	fflush(client);
}
void delete_page(FILE *client,char *req){
	//delete the saved html slimed page,for security check the username and passwd and modified to /delete/(abs)/php_(un)_(pw).jsp this requests that the un and pw should not includeunderline and dot
	char user[MAX_UN],pw[MAX_UN],abspath[MAXPATH];
	extern char username[],passwd[];
	sscanf(req,"/delete/%[^/]/php_%[^_]_%[^.].jsp",abspath,user,pw);
	chinese2host(abspath);
	chinese2host(user);
	sendHead(client);//200 OK
//	info(passwd);
	if(strcmp(user,username)==0
			&&strncasecmp(pw,passwd,strlen(passwd))==0){
		if(delete_file(abspath)==0)
			fputs("delete_ok",client);
		else fputs("delete_error",client);//file not exists or write protected
	}
	else fputs("login_deny",client);
	fflush(client);
}

