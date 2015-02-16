CC=clang
CFLAGS=-fPIC -shared

all: _libtest.so

_%.so: %.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -rf _libtest.so
