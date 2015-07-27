#include "my_httpd.h"
int file_exist(char *absname){
	if(access(absname,F_OK)!=-1){//unistd.h fcntl.h
		return 1;//other option:R_OK,W_OK,X_OK
	}else return 0;
}
int file_in_legal(char *absname){//check a file whether in the legal dir so that user can delete or modify it,forbid evil people
	extern char webpage_root[];
	if(strncmp(webpage_root,absname,strlen(webpage_root))==0)
		return 1;
	else return 0;
}
int delete_file(char *absname){
	if(file_in_legal(absname)){
		if(file_exist(absname)){
			remove(absname);//delete,in stdio.h,return 0 or -1
			return 0;
		}else	return -1;
	}else return 1;//denied
}
