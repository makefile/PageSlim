#include "my_httpd.h"
void echoHtmlPage(FILE *client,char *req){
//use the plain text to fill the html template
//这个函数派上用场实在单独的一个web页面中（<a href=xxx,不同于其他链接）
	///view?resp=html&dir=xxx,dir is absname
	char abspath[MAXPATH];
	extern char webpage_root[];
	sscanf(req,"/view?resp=html&dir=%s",abspath);
	
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
	if(ret<0) info("echoHtmlPage:read fail");
	close(fd);
	
	sendHead(client);
//	char msg[128];
//	sprintf(msg,"strlen of head:%d",strlen(packHead_close));
//	info(msg);
	char title[MAX_FN];//,time[MAX_FN];
	sscanf(p,"%s",title);
	p=formatText(p,len);//space -> &nbsp; etc
//	info("there");
	fprintf(client,"<html lang=\"zh-cn\"><html><head><meta charset=\"utf-8\"><title>Online</title></head><body><font color=\"115599\" size=+3>%s</font><br><hr width=\"100%%\"><br><font color=\"119966\" size=+2>%s</body></html>",title,p);
//	fwrite(p,len,1,client);//send file content
	fflush(client);
	free(p);
}
