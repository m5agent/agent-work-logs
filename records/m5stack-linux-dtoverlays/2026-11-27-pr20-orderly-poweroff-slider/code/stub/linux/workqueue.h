#ifndef STUB_WORKQUEUE_H
#define STUB_WORKQUEUE_H
#include "../stubcore.h"
struct work_struct { void (*func)(struct work_struct *); };
struct delayed_work { struct work_struct work; };
#define INIT_WORK(w, f) do { (w)->func = (f); } while (0)
#define INIT_DELAYED_WORK(w, f) do { (w)->work.func = (f); } while (0)
#define to_delayed_work(w) container_of(w, struct delayed_work, work)
bool schedule_work(struct work_struct *w);
bool schedule_delayed_work(struct delayed_work *w, unsigned long delay);
bool cancel_work_sync(struct work_struct *w);
bool cancel_delayed_work_sync(struct delayed_work *w);
#endif
