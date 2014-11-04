#include"my_httpd.h"
void handleTCPClient(int new_fd){
	bzero(buffer,MAXBUF+1);
	char Req[MAXPATH+1]="";
	int contLen=0;
	int numchars = get_line(new_fd, buffer, sizeof(buffer));
	if (strncmp(buffer, "GET",3) == 0)//同什么的serve_file函数，对那些请求头进行忽略
	{
		sscanf(buffer,"GET %s HTTP",Req);
		bzero(buffer,MAXBUF+1);
		sprintf(buffer,"Request get: \"%s\"\n",Req);
		info(buffer);
		while ((numchars > 0) && strcmp("\n", buffer))//read & discard headers 
			numchars = get_line(new_fd, buffer, sizeof(buffer));

		FILE *clientFP=fdopen(new_fd,"w");//care!
		//获取文件描述符，能够使用fprintf,但不使用fread,因为难以把控
		if(clientFP==NULL){
			info("fdopen");
			exit(-1);
		}else{
			GiveResponse(clientFP,Req);//专门响应连接
			fclose(clientFP);
		}
	}else{//POST
		info(buffer);
		sscanf(buffer,"POST %s HTTP",Req);
		numchars = get_line(new_fd, buffer, sizeof(buffer));
		while ((numchars > 0) && strcmp("\n", buffer)){ 
			//notice there is a space after ':',sscanf须从第一个参数的地址开始处匹配，不能智能地搜寻自己想要的片段
			buffer[15] = '\0';
			if (strcasecmp(buffer, "Content-Length:") == 0)
				contLen = atoi(&(buffer[16]));//获取后面字符的个数	
			numchars = get_line(new_fd, buffer, sizeof(buffer));
		}
		bzero(buffer,MAXBUF+1);
		sprintf(buffer,"Request POST: \"%s\",len:%d\n",Req,contLen);
		info(buffer);
		//recv(new_fd,buffer,MAXBUF,0);
		//上传文件时浏览器向连接发送了三次数据，第一次是请求头信息，第二次是文件名等相关信息，第三次才是文件内容。需要三次读。
		//	sscanf(strstr(buffer,"boundary=")
		//			,"boundary=%s#",buffer);
		//	info(buffer);
		//uploadFile(new_fd,Req,contLen);
		handlePost(new_fd,Req,contLen);
		close(new_fd);
	}
}
