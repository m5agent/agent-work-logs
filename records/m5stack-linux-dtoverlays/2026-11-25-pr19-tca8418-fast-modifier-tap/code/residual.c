#include <stdio.h>
#include "tca8418_fsm.c"
static const char *sn(tca8418_t*m){static const char*n[]={"IDLE","ACTIVE","WAIT","ONESHOT","HOLD","LOCKED","LOCKED_WAIT","LOCKED_LEAVE"};return n[m->state];}
void emit_key_pres_status(tca8418_t*m){(void)m;}
void emit_key_release_status(tca8418_t*m){(void)m;}
void led_ON(tca8418_t*m){(void)m;}
void led_OFF(tca8418_t*m){(void)m;}
void led_BLINK(tca8418_t*m){(void)m;}
void led_FAST(tca8418_t*m){(void)m;}
struct st{const char*n;Event e;};
static tca8418_t M;
static void run(const char*t,struct st*s,int n){tca8418_ctor(&M,0);M.layer_active=0;M.used=0;printf("== %s\n",t);
 for(int i=0;i<n;i++){tca8418_dispatch(&M,s[i].e);printf("  %-16s -> %-10s layer=%d used=%d\n",s[i].n,sn(&M),M.layer_active,M.used);}
 printf("  FINAL %s layer=%d\n\n",sn(&M),M.layer_active);}
#define S(x){#x,x}
int main(void){
 struct st a[]={S(EV_KEY_PRES),S(EV_KEY_RELE),S(EV_OTHER_KEY_PRES),S(EV_TIMEOUT_300),S(EV_OTHER_KEY_PRES)};
 run("tap, single key held past 300ms, then next key",a,5);
 struct st b[]={S(EV_OTHER_KEY_PRES),S(EV_KEY_PRES),S(EV_KEY_RELE),S(EV_OTHER_KEY_PRES),S(EV_TIMEOUT_300),S(EV_OTHER_KEY_PRES)};
 run("tap while pre-held key down, 2nd key, timeout, next key",b,6);
 return 0;}
