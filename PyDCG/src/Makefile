ARCH := $(shell getconf LONG_BIT)

all:
	ln -sf bigint_$(ARCH).h bigint.h
	gcc geometricbasics.c -o geometricbasics.exe
	gcc -c -fPIC geometricbasics.c -o geometricbasics.o
	gcc -shared -Wl,-soname,geometricbasics.so -o geometricbasics geometricbasics.o 

clean:
	rm bigint.h
	rm geometricbasics
	rm geometricbasics.o
