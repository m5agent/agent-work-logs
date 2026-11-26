#ifndef STUB_INTERRUPT_H
#define STUB_INTERRUPT_H
#include "../stubcore.h"
typedef int irqreturn_t;
#define IRQ_HANDLED 1
#define IRQ_NONE 0
typedef irqreturn_t (*irq_handler_t)(int, void *);
int devm_request_irq(struct device *dev, unsigned int irq, irq_handler_t h,
		     unsigned long flags, const char *name, void *arg);
void disable_irq_nosync(unsigned int irq);
void enable_irq(unsigned int irq);
#endif
