#include "my_httpd.h"
int doSlimSave(char *url,char *dir,char *name){//name is in & out type
	//call doSlim.py,save to /dir/filename,
	//dir,name can be default,return filename
	int status;
	char workdir[]="core/";//but if i was run as daemon,maybe changed to work in /var/log for create sys logs
	char command[MAX_URL+MAX_DIR+MAX_FN];//SO BIG
	sprintf(command,"python %sdoSlim.py '%s' %s %s",
			workdir,url,dir,name);
//use single ' is for that linux shell won't take it as a back job if the url include symbol '&'
	info(command);
	status=system(command);//system is different from exc series fun,for system will block the parent process
	//doSlim.py add the webpage name to a table,simplily just append to a file:newest
	char status_code[5];
	sprintf(status_code,"%d",status);
	info("exec doSlim.py use system() end with status:");info(status_code);
	
	if(strcmp(name,"default")==0){
		FILE *fp;
		fp=fopen("/dev/shm/newest","r");///tmp/newest
		if(fp!=NULL){//file not exist,maybe caused by doSlim.py corrupt or OS problem
			fgets(name,MAX_FN,fp);
			fclose(fp);
		}else{
			info("WARNING:/dev/shm/newest not exist");//info(name);
		}
	}
	//if(!WIFEXITED(status))
	return status;
}
void sendHeader(FILE *client,int size){
	//extern char packHead_close[];
//	fprintf(client,packHead_close);//200 OK
	//如果没有下面的一些额外的信息，python或其他的客户端找不到对应的状态行的话会报错，尤其是Content-type
	fprintf(client,"HTTP/1.1 200 OK\r\nServer: myserver\r\nContent-type: text/plain\r\nContent-Length: %d\r\nConnection: keep-alive\r\n\r\n",size);//text/plain
	fflush(client);///////////////////////
	/**************************
	  学到了重要的只是：一定要及时刷新缓冲区啊，何况把socket当文件流来处理。否则造成客户端python的badstatusline,客户端也应设置超时处理。
	  **************************/
}
void responseDoSlim(FILE *client,char *req){
	//handle request:doslim?url=xxx&dir=xxx&name=xxx
	//save the content to the named file,if name=default,in doSlim.py find the title or h1 as file name
	//send the content to client right away
	//int i=0;
	extern char webpage_root[];
	char url[MAX_URL];char name[MAX_FN];char dir[MAX_DIR];
	char msg[MAX_MSG];
	char realpath[MAXPATH];
	char uid[MAX_UN];
	int numchars=0;
	char *match=NULL;
	FILE *stream;
	int filesize;
	struct stat tmp;
	bzero(url,MAX_URL);bzero(name,MAX_FN);
	bzero(dir,MAX_DIR);bzero(realpath,MAXPATH);
	int i,j=0,url_len=strlen(req);
	for(i=url_len-1;i>0;i--){
		if(req[i]=='&') j++;
		if(j==3) break;
	}
	sscanf(&req[i],"&dir=%[^&]&name=%[^&]&uid=%s",dir,name,uid);//%*[^:]:%s
//	info(name);
	for(j=12;j<i;j++)
		url[j-12]=req[j];
	//sscanf(req,"/doslim?url=%[^&]&dir=%[^&]&name=%s",url,dir,name);//%*[^:]:%s
	chinese2host(dir);chinese2host(name);
	chinese2host(uid);
	/*
	match=strstr(url,"&dir=");
	sscanf(match,"&dir=%s",dir);
	match=strstr(dir,"&name=");
	sscanf(match,"&name=%s",name);
	*/
//sprintf(msg,"[s]url=%s,dir=%s,name=%s[e]\n[s]webpage_root:%s[e]\n",url,dir,name,webpage_root);
	//前面设置msg的大小时设小了，结果导致溢出了,结果真是吓人，浪费了我两个小时
//	info(msg);
	//if(strcmp(name,"default")==0),name will be modified in doSlimSave
	sprintf(realpath,"%s/%s/%s",webpage_root,uid,dir);
//	info(realpath);info(name);
	int status=doSlimSave(url,realpath,name);//save to file
	
	if(!WIFEXITED(status)){//status==-1脚本异常中断
		info("server corrupt:doSlim.py run with problem");
		fprintf(client,"filename:server error\n");
		fprintf(client,"**ERROR:server internel error!\n");
		fflush(client);
		return;
	}
	info("WIFEXITED");
	status=WEXITSTATUS(status);
	sprintf(realpath,"%d",status);
	info("real status:");info(realpath);
	if(status==2) {//没有被中断等，自行结束
		info("notify client:URL is invalid");
		fprintf(client,"filename:invalid\n");
		fprintf(client,"**ERROR:URL is invalid or malformed!\n");
		return;
	}
	
	bzero(realpath,MAXPATH);
//	info(webpage_root);
	sprintf(realpath,"%s/%s/%s/%s",webpage_root,uid,dir,name);
//info(realpath);
	if(stat(realpath,&tmp)==-1){//error,file not exist,for me,the file name maybe to long,exceed my limit:128
		fprintf(client,"filename:%s\n",name);
		fprintf(client,"**ERROR:filename is too long!\n");
	}else{
	filesize=tmp.st_size;//or use fseek and ftell
	sendHeader(client,filesize);
	stream=fopen(realpath,"rb");
	sprintf(msg,"in doSlim:start send file size:%d\n",filesize);
	info(msg);
	fprintf(client,"filename:%s\n",name);
	//the first line of file is title
	fflush(client);
	filesize=0;
/*
C语言学习两年，至今未掌握精髓！仅仅凭借自己的凭空猜测和类比推测来使用一个函数很可能造成自己难以发现的隐患，尤其是在没有完全验证的情况下。下面的循环会发送完整的内容，但最后一次发送时发送了冗余数据，导致自己认为fread没有读取完全，费了很长时间才发现。fread返回的是读取的块数，如果一次读取1块MAXBUF大小，则大多数情况下返回1,在遇到结尾和错误时返回0,因此读取最后一块时会返回0,辨别错误与文件尾应该用feof,ferr

	while((numchars=fread(buffer,MAXBUF,1,stream))>0){
				//BUFSIZ is a micro
		fputs(buffer,client);//发现了这里与fprintf的区别，fprintf遇到换行或\0才会去发，而fputs能保证给你发过去
		fflush(client);
		filesize+=MAXBUF;
	}
*/
	int sock_fd=fileno(client);
	while(1){//feof return non-zero if reach end file
		bzero(buffer,MAXBUF);
		fread(buffer,MAXBUF,1,stream);//牛逼的函数没有给你归0化存储区
		if(feof(stream)){
			send(sock_fd,buffer,strlen(buffer),0);//notice
			break;
		}else
			send(sock_fd,buffer,MAXBUF,0);
	}
	if(ferror(stream))
		info("read content error");
	fclose(stream);//fflush()是为了写回磁盘
//	printf("last buffer:%s\n",&buffer[512]);//当作字符串输出仅输出\0之前
	info("end send");
	}
}
