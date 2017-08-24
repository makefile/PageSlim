CC	= gcc 
CFLAGS=-Wall #-fno-stack-protector
#CFLAGS = -Wall #-g,no need to place .h file there in case be deleted by clean
SRCDIR=.
OUTDIR=bin
SOURCES	= myhttpd.c response.c upload.c httpd_util.c doSlim.c handlePost.c cJSON.c handleClient.c fileUtils.c makeHtml.c auth.c web_index.c
#OBJECTS	= ${SOURCES:.c=.o}
OBJECTS = $(patsubst %.c,$(OUTDIR)/%.o,$(wildcard *.c))
OUT	= httpd #myHttpd
LIBS = -lm -lpthread
#LIBS	= -lungif -L/usr/X11R6/lib 

all: $(OUT)
	@echo Build DONE.

$(OUT): $(OBJECTS)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $(OUT) $(OBJECTS) $(LIBS)
$(OBJECTS): $(OUTDIR)/%.o : $(SRCDIR)/%.c
	$(CC) $(CFLAGS) -c $< -o $@ 
clean:
	rm -f $(OUTDIR)/*  $(OUT)

distclean: clean
