# 1 "./simple.cil.c"
# 1 "<built-in>"
# 1 "<command-line>"
# 1 "/usr/include/stdc-predef.h" 1 3 4
# 1 "<command-line>" 2
# 1 "./simple.cil.c"
# 15 "simple.c"
void __globinit_simple(void) ;
extern void __CrestInit(void) __attribute__((__crest_skip__)) ;
extern void __CrestHandleReturn(int id , long long val ) __attribute__((__crest_skip__)) ;
extern void __CrestReturn(int id ) __attribute__((__crest_skip__)) ;
extern void __CrestCall(int id , unsigned int fid ) __attribute__((__crest_skip__)) ;
extern void __CrestBranch(int id , int bid , unsigned char b ) __attribute__((__crest_skip__)) ;
extern void __CrestApply2(int id , int op , long long val ) __attribute__((__crest_skip__)) ;
extern void __CrestApply1(int id , int op , long long val ) __attribute__((__crest_skip__)) ;
extern void __CrestClearStack(int id ) __attribute__((__crest_skip__)) ;
extern void __CrestStore(int id , unsigned long addr ) __attribute__((__crest_skip__)) ;
extern void __CrestLoad(int id , unsigned long addr , long long val ) __attribute__((__crest_skip__)) ;
# 202 "../bin/../include/crest.h"
extern void __CrestInt(int *x ) __attribute__((__crest_skip__)) ;
# 318 "/usr/include/stdio.h"
extern int printf(char const * __restrict __format , ...) ;
# 15 "simple.c"
int main(void)
{
  int a ;
  int b ;
  int __retres3 ;

  {
  __globinit_simple();
  __CrestCall(1, 1);
# 17 "simple.c"
  __CrestInt(& a);
  __CrestLoad(6, (unsigned long )0, (long long )3);
  __CrestLoad(5, (unsigned long )(& a), (long long )a);
  __CrestApply2(4, 2, (long long )(3 * a));
  __CrestLoad(3, (unsigned long )0, (long long )2);
  __CrestApply2(2, 0, (long long )(3 * a + 2));
  __CrestStore(7, (unsigned long )(& b));
# 18 "simple.c"
  b = 3 * a + 2;
  __CrestLoad(10, (unsigned long )(& b), (long long )b);
  __CrestLoad(9, (unsigned long )0, (long long )8);
  __CrestApply2(8, 12, (long long )(b == 8));
# 19 "simple.c"
  if (b == 8) {
    __CrestBranch(11, 3, 1);
# 20 "simple.c"
    printf((char const * __restrict )"8\n");
    __CrestClearStack(13);
  } else {
    __CrestBranch(12, 4, 0);
# 22 "simple.c"
    printf((char const * __restrict )"not 8\n");
    __CrestClearStack(14);
  }
  __CrestLoad(15, (unsigned long )0, (long long )0);
  __CrestStore(16, (unsigned long )(& __retres3));
# 24 "simple.c"
  __retres3 = 0;
  __CrestLoad(17, (unsigned long )(& __retres3), (long long )__retres3);
  __CrestReturn(18);
# 15 "simple.c"
  return (__retres3);
}
}
void __globinit_simple(void)
{


  {
  __CrestInit();
}
}
