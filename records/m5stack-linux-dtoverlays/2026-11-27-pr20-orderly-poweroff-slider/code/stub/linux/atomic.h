#ifndef STUB_ATOMIC_H
#define STUB_ATOMIC_H
#include "../stubcore.h"
typedef struct { int counter; } atomic_t;
#define atomic_read(a)        ((a)->counter)
#define atomic_set(a, v)      ((a)->counter = (v))
#define atomic_xchg(a, v)     ({ int __o = (a)->counter; (a)->counter = (v); __o; })
#endif
