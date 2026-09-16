#include <stdlib.h>
#include <malloc.h>
#include <xcb/xcb.h>
#include <X11/Xtrans/Xtrans.h>
/* Record requested bytes while supplying ample aligned physical storage.
   Even the old generator is exercised without an actual out-of-bounds write. */
void *xcb_test_allocate(size_t bytes);
#undef alloca
#define alloca xcb_test_allocate
