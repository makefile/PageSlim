#include "my_httpd.h"

void modify(int sock_fd,int len){
	char filename[MAX_FN];char dir[MAX_DIR];
	char realpath[MAX_URL];char boundary[128];
	bzero(filename,MAX_FN);bzero(dir,MAX_DIR);
	bzero(realpath,MAX_URL);bzero(boundary,128);
	int i;
	char *index;
	//下面才是line-based text data:filename=xx&user=xx
	int numchars = get_line(sock_fd, buffer, MAXBUF);
	while ((numchars > 0) && strcmp("\n", buffer)){
		info(buffer);
		if(strstr(buffer,"---")!=NULL){ 
			strcpy(boundary,buffer);
			boundary[numchars-1]='\0';//boundary[numbers-1] is '\n'
//			info(boundary);
		}else if ((index=strstr(buffer, "filename=")) !=NULL){
			sscanf(index,"filename=%s",filename);
//			info("the file name is:");info(filename);
			//strcpy(filename, &(buffer[9]));//
		}else if ((index=strstr(buffer, "dir=")) !=NULL){
			sscanf(index,"dir=%s",dir);
//			info("dir=");info(dir);
		}else if ((index=strstr(buffer, "Content-Type=")) !=NULL){
			//if(strstr(index,"text")!=NULL) isBin=0;
		}
		numchars = get_line(sock_fd, buffer,MAXBUF);
	}
	chinese2host(dir);chinese2host(filename);
	extern char webpage_root[];
	sprintf(realpath,"%s/%s/%s",webpage_root,dir,filename);
	FILE *fp;
	fp=fopen(realpath,"w");
	if(fp==NULL) info("create file error");
	numchars = get_line(sock_fd, buffer, MAXBUF);
	//discard '\n' line
	while ((numchars > 0) && strcmp("\n", buffer)==0)
		numchars = get_line(sock_fd, buffer, MAXBUF);
//	info("start write>>>");info(buffer);
	while (numchars>0&&(strstr(buffer,boundary)==NULL)){
		fwrite(buffer,numchars,1,fp);
		//唉，一失足成千古恨，fwrite个数千万别写成MAXBUF等固定值，可写成strlen，但不能是sizeof,因为buffer是个数组且从来没被初始化过。否则会残留冗余数据
		numchars = get_line(sock_fd, buffer, MAXBUF);
	}
	fclose(fp);
}
void handlePost(int sock,char *req,int len){
	if(strncasecmp(req,"/modify",7)==0){
		modify(sock,len);
		sendHead_sock(sock);
		//send()的时候千万注意strlen是遇到\n就终止，\r不会
	}else if(strncasecmp(req,"/upload",7)==0)
		uploadFile(sock,req,len);
	else return;
}
