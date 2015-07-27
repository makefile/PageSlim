#include "my_httpd.h"
//static int check_passwd(char * uid,char* passwd);
void browser_login(FILE* client,char *req){//web login button onClick
	char user[MAX_UN],pw[MAX_UN];
	//extern char username[],passwd[];
	sscanf(req,"/check!account.action?un=%[^&]&pw=%s",user,pw);
	chinese2host(user);
	
	if(check_passwd(user,pw)==1){
		char root[MAX_UN+1]="";
		sprintf(root,"/%s",user);
		listHomeFiles(client,root);//second param must not be const
	}//	return 0;
	else{
		sendHead(client);//200 OK
		fputs("login_deny",client);
	}
	fflush(client);
//	info("end of browser_login");
}
//strrchr(.)获得.后边的扩展名
//客户端登陆验证，同样与浏览器一样发送url，不同点是返回的内容不同
void login_auth(FILE *client,char *req){
	char user[MAX_UN],pw[MAX_UN];
//	extern char username[],passwd[];
	sscanf(req,"/login?un=%[^&]&pw=%s",user,pw);
	chinese2host(user);
	sendHead(client);//200 OK
//	info("conf:username:");info(username);
//	info(passwd);
	if(check_passwd(user,pw)==1)
		fputs("login_ok",client);
	else fputs("login_deny",client);
	fflush(client);
}
//从密码文件中检查是否正确，uid与密码间以：分开且：左右有空格
//return 1 for pass check,0 for wrong info,-1 for user not exist
//static 
int check_passwd(char * uid,char* passwd){
	char user[MAX_UN],pw[MAX_UN];
	char line[512];//max len
	FILE* fp=fopen("etc/passwd","r");
	int rtn=-1;
	while(!feof(fp)){
		fgets(line,sizeof(line),fp);  //读取一行
		if(strlen(line)<1) continue;
		sscanf(line,"%s : %s",user,pw);
		if(strcmp(user,uid)==0){
			if(strncasecmp(pw,passwd,strlen(passwd))==0){
				rtn=1;
			}else{
				rtn= 0;
			}
			break;
		}
	}
	fclose(fp);
	return rtn;
}
