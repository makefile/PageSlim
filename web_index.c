#include "my_httpd.h"
char * init_read(char *indexHtml){
//main函数中初始化时读入，保存在全局变量 FILE *fp=NULL;
	int fd=open("www/index.html",O_RDONLY);
	if(fd==-1){
		info("index.html not exist");
		close(fd);
		return (char*)0;
	}
	int len=lseek(fd,0,SEEK_END);
//	printf("indexHtml len:%d\n",len);
//	printf("the init indexHtml is %x\n",indexHtml);
	indexHtml=(char *)malloc(len);
	bzero(indexHtml,len);
	lseek(fd,0,SEEK_SET);
	int ret=read(fd,indexHtml,len);
	if(ret<0){
		info("read index.html error");
		close(fd);
		return (char*)0;
	}
//	printf("indexHtml len:%d\n",strlen(indexHtml));
//	printf("after molloc indexHtml is %x\n",indexHtml);
	close(fd);
	fd=open("www/favicon.ico",O_RDONLY);
	if(fd==-1){
		info("/favicon.ico not exist");
		close(fd);
		return (char*)0;
	}
	len=lseek(fd,0,SEEK_END);
	extern char *favicon;
	favicon=(char *)malloc(len);
	bzero(favicon,len);
	lseek(fd,0,SEEK_SET);
	ret=read(fd,favicon,len);
	if(ret<0){
		info("read favicon error");
		close(fd);
		return (char*)0;
	}
	close(fd);
	return indexHtml;
}//the malloc space will be freed when process exit

void showIndexHtml(FILE *client){
//显示在浏览器中的登录界面包含游客浏览已存网页功能
	sendHead(client);
	extern char *indexHtml;
//	printf("extern indexHtml is %x\n",indexHtml);
//	info("start send index html");
//	printf("indexHtml len:%d\n",strlen(indexHtml));
	fputs(indexHtml,client);
	fflush(client);
//	info("end send");
}
void showFavicon(FILE *client){
//显示在浏览器中的登录界面包含游客浏览已存网页功能
	sendHead(client);
	extern char *favicon;
	fputs(favicon,client);
	fflush(client);
}
