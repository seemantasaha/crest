# 1 "./structure_test.cil.c"
# 1 "<built-in>"
# 1 "<command-line>"
# 1 "/usr/include/stdc-predef.h" 1 3 4
# 1 "<command-line>" 2
# 1 "./structure_test.cil.c"
# 26 "structure_test.c"
void __globinit_structure_test(void) ;
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
# 15 "structure_test.c"
struct bar {
   int x ;
   int y ;
};
# 20 "structure_test.c"
struct foo {
   int x ;
   struct bar bar ;
   int y ;
};
# 202 "../bin/../include/crest.h"
extern void __CrestInt(int *x ) __attribute__((__crest_skip__)) ;
# 26 "structure_test.c"
int main(void)
{
  struct foo f1 ;
  struct foo f2 ;
  struct foo f3 ;
  struct bar b ;
  int __retres5 ;

  {
  __globinit_structure_test();
  __CrestCall(1, 1);
# 30 "structure_test.c"
  __CrestInt(& b.x);
# 31 "structure_test.c"
  __CrestInt(& b.y);
  __CrestLoad(2, (unsigned long )0, (long long )7);
  __CrestStore(3, (unsigned long )(& f1.x));
# 33 "structure_test.c"
  f1.x = 7;
# 34 "structure_test.c"
  f1.bar = b;
  __CrestLoad(4, (unsigned long )0, (long long )19);
  __CrestStore(5, (unsigned long )(& f1.y));
# 35 "structure_test.c"
  f1.y = 19;
# 37 "structure_test.c"
  __CrestInt(& f2.x);
# 38 "structure_test.c"
  __CrestInt(& f3.x);
# 39 "structure_test.c"
  __CrestInt(& f2.y);
# 41 "structure_test.c"
  f2 = f1;
  __CrestLoad(8, (unsigned long )(& f2.bar.x), (long long )f2.bar.x);
  __CrestLoad(7, (unsigned long )0, (long long )3);
  __CrestApply2(6, 14, (long long )(f2.bar.x > 3));
# 43 "structure_test.c"
  if (f2.bar.x > 3) {
    __CrestBranch(9, 3, 1);
    __CrestLoad(11, (unsigned long )0, (long long )1);
    __CrestStore(12, (unsigned long )(& f3.x));
# 43 "structure_test.c"
    f3.x = 1;
  } else {
    __CrestBranch(10, 4, 0);

  }
  __CrestLoad(15, (unsigned long )(& f2.y), (long long )f2.y);
  __CrestLoad(14, (unsigned long )0, (long long )18);
  __CrestApply2(13, 16, (long long )(f2.y < 18));
# 44 "structure_test.c"
  if (f2.y < 18) {
    __CrestBranch(16, 6, 1);
    __CrestLoad(18, (unsigned long )0, (long long )1);
    __CrestStore(19, (unsigned long )(& f3.x));
# 44 "structure_test.c"
    f3.x = 1;
  } else {
    __CrestBranch(17, 7, 0);

  }
  __CrestLoad(22, (unsigned long )(& f2.bar.y), (long long )f2.bar.y);
  __CrestLoad(21, (unsigned long )0, (long long )7);
  __CrestApply2(20, 12, (long long )(f2.bar.y == 7));
# 45 "structure_test.c"
  if (f2.bar.y == 7) {
    __CrestBranch(23, 9, 1);
    __CrestLoad(25, (unsigned long )0, (long long )1);
    __CrestStore(26, (unsigned long )(& f3.x));
# 45 "structure_test.c"
    f3.x = 1;
  } else {
    __CrestBranch(24, 10, 0);

  }
  __CrestLoad(29, (unsigned long )(& f2.x), (long long )f2.x);
  __CrestLoad(28, (unsigned long )0, (long long )0);
  __CrestApply2(27, 14, (long long )(f2.x > 0));
# 46 "structure_test.c"
  if (f2.x > 0) {
    __CrestBranch(30, 12, 1);
    __CrestLoad(32, (unsigned long )0, (long long )1);
    __CrestStore(33, (unsigned long )(& f3.x));
# 46 "structure_test.c"
    f3.x = 1;
  } else {
    __CrestBranch(31, 13, 0);

  }
  __CrestLoad(34, (unsigned long )0, (long long )0);
  __CrestStore(35, (unsigned long )(& __retres5));
# 48 "structure_test.c"
  __retres5 = 0;
  __CrestLoad(36, (unsigned long )(& __retres5), (long long )__retres5);
  __CrestReturn(37);
# 26 "structure_test.c"
  return (__retres5);
}
}
void __globinit_structure_test(void)
{


  {
  __CrestInit();
}
}
