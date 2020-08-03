# 1 "./unsigned.cil.c"
# 1 "<built-in>"
# 1 "<command-line>"
# 1 "/usr/include/stdc-predef.h" 1 3 4
# 1 "<command-line>" 2
# 1 "./unsigned.cil.c"
# 15 "unsigned.c"
void __globinit_unsigned(void) ;
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
# 199 "../bin/../include/crest.h"
extern void __CrestUInt(unsigned int *x ) __attribute__((__crest_skip__)) ;
# 318 "/usr/include/stdio.h"
extern int printf(char const * __restrict __format , ...) ;
# 15 "unsigned.c"
int main(void)
{
  unsigned int a ;
  int __retres2 ;

  {
  __globinit_unsigned();
  __CrestCall(1, 1);
# 17 "unsigned.c"
  __CrestUInt(& a);
  __CrestLoad(4, (unsigned long )(& a), (long long )a);
  __CrestLoad(3, (unsigned long )0, (long long )2147483647U);
  __CrestApply2(2, 14, (long long )(a > 2147483647U));
# 19 "unsigned.c"
  if (a > 2147483647U) {
    __CrestBranch(5, 3, 1);
    {
    __CrestLoad(9, (unsigned long )(& a), (long long )a);
    __CrestLoad(8, (unsigned long )0, (long long )4294967294U);
    __CrestApply2(7, 14, (long long )(a > 4294967294U));
# 20 "unsigned.c"
    if (a > 4294967294U) {
      __CrestBranch(10, 4, 1);
# 21 "unsigned.c"
      printf((char const * __restrict )"a\n");
      __CrestClearStack(12);
    } else {
      __CrestBranch(11, 5, 0);
# 23 "unsigned.c"
      printf((char const * __restrict )"b\n");
      __CrestClearStack(13);
    }
    }
  } else {
    __CrestBranch(6, 6, 0);
# 27 "unsigned.c"
    printf((char const * __restrict )"c\n");
    __CrestClearStack(14);
  }
  __CrestLoad(15, (unsigned long )0, (long long )0);
  __CrestStore(16, (unsigned long )(& __retres2));
# 30 "unsigned.c"
  __retres2 = 0;
  __CrestLoad(17, (unsigned long )(& __retres2), (long long )__retres2);
  __CrestReturn(18);
# 15 "unsigned.c"
  return (__retres2);
}
}
void __globinit_unsigned(void)
{


  {
  __CrestInit();
}
}
