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

#define MAXPATH 512
#define MAXBUF 1024
#define NOFILE 8
#define MAX_FILE_SIZE 4096000//less than 4MB,4096*1024
char buffer[1025];
extern void init_daemon(const char *program,int facility);
extern int get_arg(char *cmd);
extern void info(char *msg);
extern void handleTCPClient(int sock);
extern void GiveResponse(FILE *client_sock,char *path);
extern void responseDoSlim(FILE *client_sock,char *request);
extern void handlePost(int sock,char *req,int len);
extern char file_type(mode_t st_mode);
extern char* dir_up(char *dirpath);
extern int get_addr(char *str);
extern void uploadFile(int fd,char *dir,int len);
extern int hexstr2int(char,char);
extern char* chinese2host(char*);
extern int get_line(int sock,char*buf,int size);
