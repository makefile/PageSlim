#include "my_httpd.h"
//strcase str
int get_line(int sock,char *buf,int size);
void uploadFile(int sock_fd,char *path,int contLen){
	//	struct dirent *dirent;
	//	struct stat fileinfo;
	char filename[MAXPATH];
	//	DIR *dir;
	int isBin=1;
//	int binBuf[4096],isBin=1;//contBuf[MAX_FILE_SIZE] is too large and segment err
	int len,i=0,sum=0;
	char *realpath,*index;
	char logmsg[MAX_MSG],boundary[64];
	extern char upload_root[];
	//	sprintf(logmsg,"contLen:%d\n",contLen);
	//	info(logmsg);
	//将中文名还原成主机能够识别的编码
	path=chinese2host(path);
	//	printf("chinese is %s\n",path);
	//以服务器主目录为根目录如/var/www/,因此需要加该根目录才是绝对路径
	//	fread(contBuf,contLen,1,fp);//will recv all at a time
	//	recv(sock_fd,buffer,MAXBUF,0);//filename etc
	//	info(buffer);
	//	sscanf(strstr(buffer,"filename="),"filename=\"%s ",filename);
	int numchars = get_line(sock_fd, buffer, MAXBUF);
	while ((numchars > 0) && strcmp("\n", buffer))//这里同样是忽略请求头
	{//读到空行为止
		//	info(buffer);
		//boundary的行should be:--boundary,结尾：--boundary--
		if(strstr(buffer,"-----")!=NULL){ 
			strcpy(boundary,buffer);
			boundary[numchars-1]='\0';//boundary[numbers-1] is '\n'
			//info(boundary);}
	}else if ((index=strstr(buffer, "filename=")) !=NULL){
		//sscanf(index,"filename=\"%s\"",filename);
		for(i=0,index=index+10;*index!='"';index++)
			filename[i++]=*index;
		filename[i]='\0';
		info("the file name is:");
		//strcpy(filename, &(buffer[9]));//
	}
	else if ((index=strstr(buffer, "Content-Type=")) !=NULL){
		if(strstr(index,"text")!=NULL) isBin=0;
	}
	numchars = get_line(sock_fd, buffer, sizeof(buffer));
}
len=strlen(upload_root)+strlen(path)+strlen(filename)+1;
realpath=malloc(len);
bzero(realpath,len);
sprintf(realpath,"%s/%s/%s",upload_root,&path[1],filename);
info(realpath);
//you should create your directory of /upload first
/*if((fd=open(realpath,O_CREAT|O_WRONLY,0644))==-1){
  sprintf(logmsg,"upload:create file '%s' error\n",realpath);
  info(logmsg);
  }*/
FILE  * stream;
stream = fopen(realpath,"w+b");
free(realpath);
//contBuf=(int *)malloc(contLen);
//bzero(contBuf,contLen);
//接受顺序是无续的，需要控制组织接受到的片段。对于大文件可能，本程序现在难以招架
//需要根据Content-Type来接受，二进制还是文本
//	if(recv(sock_fd,contBuf,contLen-sum,0)>0)//file content
//		write(fd,contBuf,1081);
char tmp[MAXBUF];int tmp_num=0;
numchars = get_line(sock_fd, buffer, sizeof(buffer));
while (numchars > 0) 
{//读到boundary为止

		if(numchars==1){
			tmp_num = get_line(sock_fd, tmp, MAXBUF);
			if(strstr(buffer,boundary)) break;
	//这一句很有必要，否则链接一直不断开，无法跳出循环，并跳转网页
			fwrite(buffer,numchars, 1, stream );
			sum+=numchars;
			strcpy(buffer,tmp);
			numchars=tmp_num;
		}else if(strstr(buffer,boundary)==NULL){
			fwrite(buffer,numchars, 1, stream );
			sum+=numchars;
			numchars = get_line(sock_fd, buffer,MAXBUF);
		}else break;
}
fclose(stream);
//fseek(stream, -1, SEEK_END);
//while((numchars=fread(binBuf,4096,1,stream))==4096)
//	fwrite(buffer,4096,1,stream);
//fwrite(,1,1,stream);
info("write success\n");
sprintf(logmsg,"contLen:%d\n",sum-1);//content lenth include headers etc
info(logmsg);
//close(fd);
//free(contBuf);
//	while(recv(sock_fd,buffer,sizeof(buffer),0)>0)
//		recv(sock_fd,buffer,sizeof(buffer),0);//抛弃剩余的
char success[]="HTTP/1.1 200 OK\r\nServer:Test http server\r\nConnection:close\r\n\r\n<html><script language=\"javascript\" type=\"text/javascript\"> var i = 5;var intervalid; "
"intervalid = setInterval(\"fun()\", 1000); "//every 1 s
"function fun() { if (i == 0) {window.location.href =\"http://localhost:8080\";" 
"clearInterval(intervalid); }i--;}" 
"</script> <body><center><h1>Upload success!</h1><br>will return home page after 5 secs.</center></body></html>\r\n\r\n";
send(sock_fd,success,sizeof(success),0);
}
/* Get a line from a socket, whether the line ends in a newline, 
 * carriage return, or a CRLF combination.  Terminates the string read 
 * with a null character.  If no newline indicator is found before the 
 * end of the buffer, the string is terminated with a null.  If any of 
 * the above three line terminators is read, the last character of the 
 * string will be a linefeed and the string will be terminated with a 
 * null character. 
 * Parameters: the socket descriptor 
 *             the buffer to save the data in 
 *             the size of the buffer 
 * Returns: the number of bytes stored (excluding null) */  

int get_line(int sock, char *buf, int size) {  
	int i = 0;  
	char c = '\0';  
	int n;  
	//	bzero(buf,sizeof(buf));//no need
	while ((i < size - 1) && (c != '\n')) {  
		n = recv(sock, &c, 1, 0);  
		/* DEBUG printf("%02X\n", c); */  
		if (n > 0) {  
			if (c == '\r') {  
				n = recv(sock, &c, 1, MSG_PEEK);  
				/* DEBUG printf("%02X\n", c); */  
				if ((n > 0) && (c == '\n'))  
					recv(sock, &c, 1, 0);  
				else  
					c = '\n'; //将\r 转成\n 
			}  
			buf[i] = c;  
			i++;  
		} else  
			c = '\n';  
	}  
	buf[i] = '\0';  

	return (i);  
}  
