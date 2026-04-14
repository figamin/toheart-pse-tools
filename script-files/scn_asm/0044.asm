0:{
text(1)
op_03E8()
text(2)
op_03EC()
op_03F5()
op_0004()
op_0000()
}

1:{
mov(v120,20)
mov(v121,4)
call(57345,1)
dat_call(69,1)
op_0000()
}

2:{
dat_call(201,1)
op_0004()
op_0000()
}

3:{
dat_call(224,1)
sprite_anim(v16,0,101)
sprite_anim(v16,1,101)
sprite_anim(v16,2,101)
sprite_anim(v16,3,101)
dat_call(224,1)
dat_call(202,1)
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
test_seen(3162)
msg_reset()
msg_wait_idle()
msg_sync()
op_0402(30)
op_0410(337,11,10)
text(3)
op_03EA()
op_03E8()
text(4)
op_03EA()
op_03E8()
text(5)
op_03EC()
op_0412(0,0,11)
msg_reset()
msg_wait_idle()
msg_sync()
op_03F5()
set_seen(3162)
op_0004()
op_0000()
}
