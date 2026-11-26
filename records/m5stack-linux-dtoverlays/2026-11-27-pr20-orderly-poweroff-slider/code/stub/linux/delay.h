#ifndef STUB_DELAY_H
#define STUB_DELAY_H
#include "../stubcore.h"
#define msecs_to_jiffies(m) ((unsigned long)(m))
#define msleep(ms) sim_msleep(ms)
#endif
