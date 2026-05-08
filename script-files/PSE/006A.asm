0:{
text(1)
op_03EC()
op_03F5()
op_0004()
op_0000()
}

1:{
mov(v120,58)
mov(v121,0)
call(57345,1)
dat_call(107,1)
op_0000()
}

2:{
sprite_hide(v8,1,55)
dat_call(210,1)
op_0004()
op_0000()
}

3:{
sprite_anim(v8,1,73)
dat_call(2256,1)
sprite_load(v36,32,87)
dat_call(1296,1)
sprite_load(v46,12,101)
dat_call(776,1)
dat_call(211,1)
op_0004()
op_0000()
}

4:{
op_0004()
op_0000()
}

5:{
op_0004()
op_0000()
}

6:{
op_0004()
op_0000()
}

7:{
op_0004()
op_0000()
}

8:{
op_0004()
op_0000()
}

9:{
op_0004()
op_0000()
}

10:{
op_0004()
op_0000()
}

11:{
test_seen(3296)
msg_reset()
msg_wait_idle()
msg_sync()
op_0402(30)
op_0410(327,11,10)
text(2)
op_03EA()
op_03E8()
text(3)
op_03EA()
op_03E8()
text(4)
op_03EC()
op_0412(0,0,11)
msg_reset()
msg_wait_idle()
msg_sync()
op_03F5()
set_seen(3296)
op_0004()
op_0000()
}
