#include "py/dynruntime.h"
#include <stdio.h>
#define POLYNOMIAL 0xD5u

static mp_obj_t crc8(mp_obj_t x_obj) {
   mp_int_t x = mp_obj_get_int(x_obj);
   uint8_t data[2] = {x >> 8, x};
   uint8_t crc = 0xFF;
   for(int i = 0; i < 2; i++) {
       crc ^= data[i];
       for(uint8_t bit = 8; bit > 0; --bit) {
           if(crc & 0x80) {
               crc = (crc << 1) ^ POLYNOMIAL;
           } else {
               crc = (crc << 1);
           }
       }
   }
   mp_int_t rslt = crc;
   return mp_obj_new_int(rslt);
}

static MP_DEFINE_CONST_FUN_OBJ_1(crc8_obj, crc8);

mp_obj_t mpy_init(mp_obj_fun_bc_t *self, size_t n_args, size_t n_kw, mp_obj_t *args) {
   MP_DYNRUNTIME_INIT_ENTRY

   mp_store_global(MP_QSTR_crc8, MP_OBJ_FROM_PTR(&crc8_obj));

   MP_DYNRUNTIME_INIT_EXIT
}
