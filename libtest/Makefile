CC=clang
CFLAGS=-fPIC -shared

all: libtest.so

%.so: %.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -rf libtest.so
