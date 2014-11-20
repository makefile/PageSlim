#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>
#include<strings.h>//bzero
#include<string.h>
#include<sys/socket.h>
#include<netinet/in.h>
#include<arpa/inet.h>
#include<sys/syslog.h>//syslog
#include<signal.h>
#include<pthread.h>
#include<sys/types.h>
#include<pwd.h>//struct passwd,getpwuid()
#include<grp.h>//struct group,getgrgid
#include<errno.h>
#include<sys/ioctl.h>
#include<sys/stat.h> //file stat
#include<sys/dir.h>
#include<net/if.h>//ifreq
#include<time.h>
#include<fcntl.h>//O_RDONLY

//#define __DEBUG 1
#define MAXPATH 512
#define MAXBUF 1024
#define NOFILE 8
#define MAX_FILE_SIZE 4096000//less than 4MB,4096*1024
char buffer[MAXBUF+1];
#define MAX_FN 128 //FILE NAME
#define MAX_URL 512 //A TARGET URL LEN
#define MAX_DIR 128 
#define MAX_MSG 1024 //LOG MSG
#define MAX_UN 30 //USERNAME AND PASSWD
//#define MAX_
//#define MAX_
extern void init_daemon(const char *program,int facility);
extern int get_arg(char *cmd,char *buf,char *glb_var);
extern int getAllArg();
extern void info(char *msg);
extern void handleTCPClient(int sock);
extern void GiveResponse(FILE *client_sock,char *path);
extern void responseDoSlim(FILE *client_sock,char *request);
extern void echoHtmlPage(FILE *client_sock,char *path);
extern void handlePost(int sock,char *req,int len);
extern char file_type(mode_t st_mode);
extern char* dir_up(char *dirpath);
extern int get_addr(char *str);
extern void uploadFile(int fd,char *dir,int len);
extern int hexstr2int(char,char);
extern char* chinese2host(char*);
extern int get_line(int sock,char*buf,int size);
extern void sendHead(FILE *client);
extern void sendHead_sock(int sock);
extern int delete_file(char *fn);
extern char* formatText(char *text);
