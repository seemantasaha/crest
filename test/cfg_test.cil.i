# 1 "./cfg_test.cil.c"
# 1 "<built-in>"
# 1 "<command-line>"
# 1 "/usr/include/stdc-predef.h" 1 3 4
# 1 "<command-line>" 2
# 1 "./cfg_test.cil.c"
# 55 "cfg_test.c"
void __globinit_cfg_test(void) ;
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
# 15 "cfg_test.c"
void f(int a ) ;
# 16 "cfg_test.c"
void g(int a ) ;
# 17 "cfg_test.c"
void h(int a ) ;
# 19 "cfg_test.c"
void f(int a )
{


  {
  __CrestCall(2, 1);
  __CrestStore(1, (unsigned long )(& a));
  {
  __CrestLoad(5, (unsigned long )(& a), (long long )a);
  __CrestLoad(4, (unsigned long )0, (long long )13);
  __CrestApply2(3, 14, (long long )(a > 13));
# 20 "cfg_test.c"
  if (a > 13) {
    __CrestBranch(6, 2, 1);
# 21 "cfg_test.c"
    printf((char const * __restrict )"greater than 13\n");
    __CrestClearStack(8);
  } else {
    __CrestBranch(7, 3, 0);
# 23 "cfg_test.c"
    printf((char const * __restrict )"not greater than 13\n");
    __CrestClearStack(9);
  }
  }

  {
  __CrestReturn(10);
# 19 "cfg_test.c"
  return;
  }
}
}
# 36 "cfg_test.c"
void i(int a ) ;
# 27 "cfg_test.c"
void g(int a )
{


  {
  __CrestCall(12, 2);
  __CrestStore(11, (unsigned long )(& a));
  __CrestLoad(13, (unsigned long )(& a), (long long )a);
# 28 "cfg_test.c"
  h(a);
  __CrestClearStack(14);
  {
  __CrestLoad(17, (unsigned long )(& a), (long long )a);
  __CrestLoad(16, (unsigned long )0, (long long )7);
  __CrestApply2(15, 12, (long long )(a == 7));
# 30 "cfg_test.c"
  if (a == 7) {
    __CrestBranch(18, 8, 1);
# 31 "cfg_test.c"
    printf((char const * __restrict )"7\n");
    __CrestClearStack(20);
  } else {
    __CrestBranch(19, 9, 0);
# 33 "cfg_test.c"
    printf((char const * __restrict )"not 7\n");
    __CrestClearStack(21);
  }
  }
  __CrestLoad(22, (unsigned long )(& a), (long long )a);
# 36 "cfg_test.c"
  i(a);
  __CrestClearStack(23);

  {
  __CrestReturn(24);
# 27 "cfg_test.c"
  return;
  }
}
}
# 39 "cfg_test.c"
void h(int a )
{


  {
  __CrestCall(26, 3);
  __CrestStore(25, (unsigned long )(& a));
  {
  __CrestLoad(29, (unsigned long )(& a), (long long )a);
  __CrestLoad(28, (unsigned long )0, (long long )-4);
  __CrestApply2(27, 12, (long long )(a == -4));
# 40 "cfg_test.c"
  if (a == -4) {
    __CrestBranch(30, 14, 1);
# 41 "cfg_test.c"
    printf((char const * __restrict )"-4\n");
    __CrestClearStack(32);
  } else {
    __CrestBranch(31, 15, 0);
# 43 "cfg_test.c"
    printf((char const * __restrict )"not -4\n");
    __CrestClearStack(33);
  }
  }

  {
  __CrestReturn(34);
# 39 "cfg_test.c"
  return;
  }
}
}
# 47 "cfg_test.c"
void i(int a )
{


  {
  __CrestCall(36, 4);
  __CrestStore(35, (unsigned long )(& a));
  {
  __CrestLoad(39, (unsigned long )(& a), (long long )a);
  __CrestLoad(38, (unsigned long )0, (long long )100);
  __CrestApply2(37, 12, (long long )(a == 100));
# 48 "cfg_test.c"
  if (a == 100) {
    __CrestBranch(40, 19, 1);
# 49 "cfg_test.c"
    printf((char const * __restrict )"100\n");
    __CrestClearStack(42);
  } else {
    __CrestBranch(41, 20, 0);
# 51 "cfg_test.c"
    printf((char const * __restrict )"not 100\n");
    __CrestClearStack(43);
  }
  }

  {
  __CrestReturn(44);
# 47 "cfg_test.c"
  return;
  }
}
}
# 55 "cfg_test.c"
int main(void)
{
  int a ;
  int __retres2 ;

  {
  __globinit_cfg_test();
  __CrestCall(45, 5);
# 57 "cfg_test.c"
  __CrestInt(& a);
  __CrestLoad(48, (unsigned long )(& a), (long long )a);
  __CrestLoad(47, (unsigned long )0, (long long )19);
  __CrestApply2(46, 12, (long long )(a == 19));
# 59 "cfg_test.c"
  if (a == 19) {
    __CrestBranch(49, 25, 1);
# 60 "cfg_test.c"
    printf((char const * __restrict )"19\n");
    __CrestClearStack(51);
  } else {
    __CrestBranch(50, 26, 0);
# 62 "cfg_test.c"
    printf((char const * __restrict )"not 19\n");
    __CrestClearStack(52);
  }
  __CrestLoad(53, (unsigned long )(& a), (long long )a);
# 65 "cfg_test.c"
  f(a);
  __CrestClearStack(54);
  __CrestLoad(55, (unsigned long )(& a), (long long )a);
# 67 "cfg_test.c"
  g(a);
  __CrestClearStack(56);
  __CrestLoad(59, (unsigned long )(& a), (long long )a);
  __CrestLoad(58, (unsigned long )0, (long long )1);
  __CrestApply2(57, 13, (long long )(a != 1));
# 69 "cfg_test.c"
  if (a != 1) {
    __CrestBranch(60, 29, 1);
# 70 "cfg_test.c"
    printf((char const * __restrict )"not 1\n");
    __CrestClearStack(62);
  } else {
    __CrestBranch(61, 30, 0);
# 72 "cfg_test.c"
    printf((char const * __restrict )"1\n");
    __CrestClearStack(63);
  }
  __CrestLoad(64, (unsigned long )0, (long long )0);
  __CrestStore(65, (unsigned long )(& __retres2));
# 75 "cfg_test.c"
  __retres2 = 0;
  __CrestLoad(66, (unsigned long )(& __retres2), (long long )__retres2);
  __CrestReturn(67);
# 55 "cfg_test.c"
  return (__retres2);
}
}
void __globinit_cfg_test(void)
{


  {
  __CrestInit();
}
}
